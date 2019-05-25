import pytest
from src import create_app
from src.utils.model_wrappers.survey_wrapper import SurveyVersionWrapper

class Test_SurveyVersion_Wrapper:
    app = create_app(
        mode="development",
        static_path="../static",
        instance_path="../instance",
        templates_path="../templates"
    )
    def test_set_up(self):
        with self.app.app_context():
            from src.database.db import get_db, distroy_db, init_db
            from src.models.survey_model import SurveyVersion
            
            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_1 = SurveyVersion(
                    title="Test Survey Version 1"
                )
                test_survey_version_1.save()

            pytest.test_survey_version_1 = test_survey_version_1
    
    def test_construct_wrapper(self):
        test_survey_version_1 = pytest.test_survey_version_1
        test_survey_version_wrapper_1 = SurveyVersionWrapper(test_survey_version_1)
        pytest.test_survey_version_wrapper_1 = test_survey_version_wrapper_1
    
    def test_version_getter(self):
        test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1
        got_test_survey_version_1 = test_survey_version_wrapper_1.version

        assert got_test_survey_version_1 == pytest.test_survey_version_1
    
    def test_nodeId_set(self):

        test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1
        got_test_survey_version_1_nodeId = test_survey_version_wrapper_1.nodeId

        assert got_test_survey_version_1_nodeId == pytest.test_survey_version_1.nodeId
    
    def test_title_is_set(self):
        
        test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1
        got_test_survey_version_1_title = test_survey_version_wrapper_1.title

        assert got_test_survey_version_1_title == pytest.test_survey_version_1.title 