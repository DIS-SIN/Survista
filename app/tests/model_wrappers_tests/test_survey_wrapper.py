from src import create_app
import pytest
from src.utils.model_wrappers.survey_wrapper import SurveyWrapper

class Test_Survey_Wrapper:

    app = create_app(
        mode="development",
        static_path="../static",
        instance_path="../instance",
        templates_path="../templates"
    )
    
    def test_set_up(self):
        with self.app.app_context():
            from src.database.db import get_db, init_db, distroy_db
            from src.models.survey_model import Survey

            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_1 = Survey(
                    slug = "test_survey_1",
                    language = "en"
                )
                test_survey_1.save()
            
            pytest.test_survey_1 = test_survey_1 # type: Survey
    
    def test_construct_SurveyWrapper(self):
        test_survey_1 = pytest.test_survey_1
        test_survey_wrapper_1 = SurveyWrapper(test_survey_1)
        pytest.test_survey_wrapper_1 = test_survey_wrapper_1 # type: SurveyWrapper
    
    def test_SurveyWrapper_getter(self):
        test_survey_wrapper_1 = pytest.test_survey_wrapper_1 # type: SurveyWrapper
        got_test_survey_1 = test_survey_wrapper_1.survey

        assert got_test_survey_1 == pytest.test_survey_1
    
    def test_SurveyWrapper_setter(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            
            current_transaction = get_db().transaction
            with current_transaction:
                test_survey_2 = Survey(
                    slug="test_survey_2",
                    language="en"
                )
                test_survey_2.save()
            
            test_survey_wrapper_1 = pytest.test_survey_wrapper_1 # type: SurveyWrapper

            test_survey_wrapper_1.survey = test_survey_2

            assert test_survey_wrapper_1._survey == test_survey_2
    



            


