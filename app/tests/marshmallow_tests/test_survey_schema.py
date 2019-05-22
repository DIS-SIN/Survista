
from src import create_app
import pytest
from datetime import datetime

class Test_Survey_Schema:
    app = create_app(
        mode="development",
        static_path="../static",
        instance_path="../instance",
        templates_path="../templates"
    )
    def test_survey_dump(self):
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
            
            test_output = SurveySchema().dump(test_survey_1)
            pytest.test_survey_1 = test_survey_1
            pytest.test_output_data = test_output.data
            pytest.test_output_errors = test_output.errors
            assert bool(pytest.test_output_errors) is False 
    def test_addedOn_field_is_ISO8601(self):
        output_addedOn = pytest.test_output_data['addedOn']
        addedOn = datetime.strptime(output_addedOn,
                                    '%Y-%m-%dT%H:%M:%S.%f%z')
        assert addedOn == pytest.test_survey_1.addedOn
    
    

