from ert_gui.ide.keywords.definitions import IntegerArgument, KeywordDefinition, ConfigurationLineDefinition, PathArgument, StringArgument


class EnsembleKeywords(object):
    def __init__(self, ert_keywords):
        super(EnsembleKeywords, self).__init__()
        self.group = "Ensemble"

        ert_keywords.addKeyword(self.addNumRealizations())
        ert_keywords.addKeyword(self.addEnkfScheduleFile())
        ert_keywords.addKeyword(self.addEnsPath())
        ert_keywords.addKeyword(self.addSelectCase())
        ert_keywords.addKeyword(self.addEndDate())
        ert_keywords.addKeyword(self.addHistorySource())
        ert_keywords.addKeyword(self.addRefCase())
        ert_keywords.addKeyword(self.addObsConfig())
        ert_keywords.addKeyword(self.addResultPath())




    def addNumRealizations(self):
        num_realizations = ConfigurationLineDefinition(keyword=KeywordDefinition("NUM_REALIZATIONS"),
                                                       arguments=[IntegerArgument(from_value=1)],
                                                       documentation_link="ensemble/num_realizations",
                                                       required=True,
                                                       group=self.group)
        return num_realizations



    def addEnkfScheduleFile(self):
        enkf_schedule_file = ConfigurationLineDefinition(keyword=KeywordDefinition("ENKF_SCHED_FILE"),
                                                         arguments=[PathArgument()],
                                                         documentation_link="ensemble/enkf_sched_file",
                                                         required=False,
                                                         group=self.group)
        return enkf_schedule_file

    def addEndDate(self):
        end_date = ConfigurationLineDefinition(keyword=KeywordDefinition("END_DATE"),
                                                         arguments=[StringArgument()],
                                                         documentation_link="ensemble/end_date",
                                                         required=False,
                                                         group=self.group)
        return end_date


    def addEnsPath(self):
        ens_path = ConfigurationLineDefinition(keyword=KeywordDefinition("ENSPATH"),
                                               arguments=[PathArgument()],
                                               documentation_link="ensemble/enspath",
                                               required=False,
                                               group=self.group)
        return ens_path



    def addSelectCase(self):
        select_case = ConfigurationLineDefinition(keyword=KeywordDefinition("SELECT_CASE"),
                                                  arguments=[StringArgument()],
                                                  documentation_link="ensemble/select_case",
                                                  required=False,
                                                  group=self.group)
        return select_case


    def addHistorySource(self):
        history_source = ConfigurationLineDefinition(keyword=KeywordDefinition("HISTORY_SOURCE"),
                                                  arguments=[StringArgument(built_in=True)],
                                                  documentation_link="ensemble/history_source",
                                                  required=False,
                                                  group=self.group)
        return history_source


    def addRefCase(self):
        refcase = ConfigurationLineDefinition(keyword=KeywordDefinition("REFCASE"),
                                                  arguments=[PathArgument()],
                                                  documentation_link="ensemble/refcase",
                                                  required=False,
                                                  group=self.group)
        return refcase




    def addObsConfig(self):
        obs_config = ConfigurationLineDefinition(keyword=KeywordDefinition("OBS_CONFIG"),
                                                   arguments=[PathArgument()],
                                                   documentation_link="ensemble/obs_config",
                                                   required=False,
                                                   group=self.group)
        return obs_config


    def addResultPath(self):
        result_path = ConfigurationLineDefinition(keyword=KeywordDefinition("RESULT_PATH"),
                                                  arguments=[PathArgument()],
                                                  documentation_link="ensemble/result_path",
                                                  required=False,
                                                  group=self.group)
        return result_path
