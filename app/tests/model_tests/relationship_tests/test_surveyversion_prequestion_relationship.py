import pytest
from src import create_app
from datetime import datetime


class Test_SurveyVersion_Prequestion_Relationship:
    app = create_app(
        mode="development",
        static_path="../static",
        templates_path="../templates",
        instance_path="../instance"
    )

    def test_create_relationship(self):
        with self.app.app_context():
            from src.database.db import get_db, init_db, distroy_db
            from src.models.question_model import PreQuestion
            from src.models.survey_model import SurveyVersion

            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_prequestion_1 = PreQuestion(
                    slug="test_prequestion_1",
                    text="This is and example PreQuestion 1",
                    language="en"
                )
                test_prequestion_1.save()
                test_surveyversion_1 = SurveyVersion(
                    title="Test SurveyVersion 1"
                )
                test_surveyversion_1.save()

                rel = test_surveyversion_1.prequestions.connect(
                    test_prequestion_1
                )

                pytest.test_prequestion_1 = test_prequestion_1
                pytest.test_surveyversion_1 = test_surveyversion_1
                pytest.test_surveyversion_prequestion_rel_1 = rel
    
    def test_addedOn_field_is_datetime(self):
        assert pytest.test_surveyversion_prequestion_rel_1.addedOn is not None
        assert isinstance(
            pytest.test_surveyversion_prequestion_rel_1.addedOn,
            datetime
        )