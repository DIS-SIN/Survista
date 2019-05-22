from src import create_app
import pytest

class Test_SurveyVersion_Schema_Dump:
    app = create_app(
        mode="development",
        static_path="../static",
        instance_path="../instance",
        templates_path="../templates"
    )
    def test_schema_dump(self):
        with self.app.app_context():
            from src.database.db import get_db, init_db, distroy_db
            from src.models.survey_model import SurveyVersion
            from src.utils.marshmallow.surveyversion_schema import SurveyVersionSchema

            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_surveyversion_1 = SurveyVersion(
                    title = "Test SurveyVersion 1",
                )
                test_surveyversion_1.save()
            
            pytest.test_surveyversion_1 = test_surveyversion_1
            test_output_1 = SurveyVersionSchema().dump(test_surveyversion_1)
            pytest.test_output_1_data = test_output_1.data
            pytest.test_output_1_errors = test_output_1.errors

            assert bool(pytest.test_output_1_errors) == False