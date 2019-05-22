
from src import create_app
import pytest
from datetime import datetime

class Test_Survey_Schema_Dump:
    app = create_app(
        mode="development",
        static_path="../static",
        instance_path="../instance",
        templates_path="../templates"
    )
    def test_schema_dump(self):
        with self.app.app_context():
            from src.database.db import get_db, init_db, distroy_db
            from src.models.survey_model import Survey
            from src.utils.marshmallow.survey_schema import SurveySchema

            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_1 = Survey(
                    slug="test_survey_1",
                    language = "en",
                )
                test_survey_1.save()
            
            test_output_1 = SurveySchema().dump(test_survey_1)
            pytest.test_survey_1 = test_survey_1
            pytest.test_output_1_data = test_output_1.data
            assert bool(test_output_1.errors) is False 
    def test_addedOn_field_is_ISO8601(self):
        output_addedOn = pytest.test_output_1_data['addedOn']
        addedOn = datetime.strptime(output_addedOn,
                                    '%Y-%m-%dT%H:%M:%S.%f%z')
        assert addedOn == pytest.test_survey_1.addedOn
    
    def test_nested_surveyversion(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion
            from src.utils.marshmallow.survey_schema import SurveySchema

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_1 = pytest.test_survey_1
                test_surveyversion_1 = SurveyVersion(
                    title = "Test Survey Version 1"
                )
                test_surveyversion_1.save()
                test_survey_1.versions.connect(
                    test_surveyversion_1
                )
            pytest.test_surveyversion_1 = test_surveyversion_1

            test_output_2 = SurveySchema().dump(
                test_survey_1
            )
            
            pytest.test_output_2_data = test_output_2.data
            assert bool(test_output_2.errors) is False
    
    def test_versions_field_is_array(self):
        
        output_versions_field = pytest.test_output_2_data['versions']
        assert output_versions_field is not None
        assert len(output_versions_field) == 1
    
    def test_currentVersion_field_is_None(self):
        output_currentVersion_field = pytest.test_output_2_data['currentVersion']
        assert output_currentVersion_field is None
    
    def test_multiple_nested_versions(self):
        with app.app








