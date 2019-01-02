from res.enkf.enums import EnkfInitModeEnum, HookRuntime
from res.enkf import ErtRunContext
from ert_gui.ertwidgets.models.ertmodel import getNumberOfIterations
from ert_gui.simulation.models import BaseRunModel, ErtRunError


class IteratedEnsembleSmoother(BaseRunModel):

    def __init__(self, queue_config):
        super(IteratedEnsembleSmoother, self).__init__("Iterated Ensemble Smoother", queue_config , phase_count=2)
        self.support_restart = False

    def setAnalysisModule(self, module_name):
        module_load_success = self.ert().analysisConfig().selectModule(module_name)

        if not module_load_success:
            raise ErtRunError("Unable to load analysis module '%s'!" % module_name)

        return self.ert().analysisConfig().getModule(module_name)


    def _runAndPostProcess(self, run_context):
        self._job_queue = self._queue_config.create_job_queue( )
        phase_msg = "Running iteration %d of %d simulation iterations..." % (run_context.get_iter(), self.phaseCount() - 1)
        self.setPhase(run_context.get_iter(), phase_msg, indeterminate=False)

        self.setPhaseName("Pre processing...", indeterminate=True)
        self.ert().getEnkfSimulationRunner().createRunPath( run_context )
        self.ert().getEnkfSimulationRunner().runWorkflows( HookRuntime.PRE_SIMULATION )

        self.setPhaseName("Running forecast...", indeterminate=False)
        num_successful_realizations = self.ert().getEnkfSimulationRunner().runSimpleStep(self._job_queue, run_context)

        self.checkHaveSufficientRealizations(num_successful_realizations)

        self.setPhaseName("Post processing...", indeterminate=True)
        self.ert().getEnkfSimulationRunner().runWorkflows( HookRuntime.POST_SIMULATION )
        self._job_queue = None



    def createTargetCaseFileSystem(self, phase, target_case_format):
        target_fs = self.ert().getEnkfFsManager().getFileSystem(target_case_format % phase)
        return target_fs


    def analyzeStep(self, run_context):
        target_fs = run_context.get_target_fs( )
        self.setPhaseName("Analyzing...", indeterminate=True)
        source_fs = self.ert().getEnkfFsManager().getCurrentFileSystem()

        self.setPhaseName("Pre processing update...", indeterminate=True)
        self.ert().getEnkfSimulationRunner().runWorkflows(HookRuntime.PRE_UPDATE)
        es_update = self.ert().getESUpdate()

        success = es_update.smootherUpdate(run_context)
        if not success:
            raise ErtRunError("Analysis of simulation failed!")

        self.setPhaseName("Post processing update...", indeterminate=True)
        self.ert().getEnkfSimulationRunner().runWorkflows(HookRuntime.POST_UPDATE)

    def runSimulations(self, arguments):
        phase_count = getNumberOfIterations() + 1
        self.setPhaseCount(phase_count)

        analysis_module = self.setAnalysisModule(arguments["analysis_module"])
        target_case_format = arguments["target_case"]
        run_context = self.create_context( arguments , 0 )

        self.ert().analysisConfig().getAnalysisIterConfig().setCaseFormat( target_case_format )

        self._runAndPostProcess( run_context )

        analysis_config = self.ert().analysisConfig()
        analysis_iter_config = analysis_config.getAnalysisIterConfig()
        num_retries_per_iteration = analysis_iter_config.getNumRetries()
        num_tries = 0

        while True:
            pre_analysis_iter_num = analysis_module.getInt("ITER")
            self.analyzeStep( run_context )
            current_iter = analysis_module.getInt("ITER")

            analysis_success = False
            if current_iter > pre_analysis_iter_num:
                analysis_success = True

            if analysis_success:
                run_context = self.create_context( arguments, current_iter, prior_context = run_context )
                self.ert().getEnkfFsManager().switchFileSystem(run_context.get_target_fs())
                self._runAndPostProcess(run_context)
                num_tries = 0
            else:
                run_context = self.create_context( arguments, current_iter, prior_context = run_context , rerun = True)
                self._runAndPostProcess(run_context)
                num_tries += 1
                if num_tries >= num_retries_per_iteration:
                    break

            if current_iter == getNumberOfIterations():
                break

        if current_iter == (phase_count - 1):
            self.setPhase(phase_count, "Simulations completed.")
        else:
            raise ErtRunError("Iterated Ensemble Smoother stopped: maximum number of iteration retries (%d retries) reached for iteration %d" % (num_retries_per_iteration, current_iter))

        return run_context


    def create_context(self, arguments, itr, prior_context = None, rerun = False):
        model_config = self.ert().getModelConfig( )
        runpath_fmt = model_config.getRunpathFormat( )
        jobname_fmt = model_config.getJobnameFormat( )
        subst_list = self.ert().getDataKW( )
        fs_manager = self.ert().getEnkfFsManager()
        target_case_format = arguments["target_case"]

        if prior_context is None:
            mask = arguments["active_realizations"]
        else:
            mask = prior_context.get_mask( )

        sim_fs = self.createTargetCaseFileSystem(itr, target_case_format)
        if rerun:
            target_fs = None
        else:
            target_fs = self.createTargetCaseFileSystem(itr + 1 , target_case_format)

        run_context = ErtRunContext.ensemble_smoother( sim_fs, target_fs, mask, runpath_fmt, jobname_fmt, subst_list, itr)
        return run_context



