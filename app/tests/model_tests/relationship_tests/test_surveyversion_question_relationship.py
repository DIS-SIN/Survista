import pytest
from src import create_app
from datetime import datetime

class Test_SurveyVersion_Question_Relationship:
    app = create_app(
        mode="development",
        static_path='../static',
        templates_path='../templates',
        instance_path='../instance'
    )
    def test_create_relationship(self):
        with self.app.app_context():
            from src.database.db import get_db, init_db, distroy_db
            from src.models.survey_model import SurveyVersion
            from src.models.question_model import Question
            
            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_surveyversion_1 = SurveyVersion(
                    title="Test Survey Version 1"
                )
                test_surveyversion_1.save()
                test_question_1 = Question(
                    slug = "test_question_1",
                    question = "Test Question 1",
                    language = "en"
                )
                test_question_1.save()
                rel = test_surveyversion_1.questions.connect(
                    test_question_1
                )
                pytest.test_question_1 = test_question_1
                pytest.test_surveyversion_1 = test_surveyversion_1
                pytest.test_surveyversion_question_rel_1 = rel
    def test_addedOn_field_is_datetime(self):
        assert pytest.test_surveyversion_question_rel_1.addedOn is not None
        assert isinstance(pytest.test_surveyversion_question_rel_1.addedOn, datetime)

