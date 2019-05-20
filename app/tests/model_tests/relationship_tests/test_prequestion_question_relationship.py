import pytest
from src import create_app
from datetime import datetime

class Test_Prequestion_Question_Relationship:

    app = create_app(
        mode="development",
        static_path="../static",
        templates_path="../templates",
        instance_path="../instance"
    )

    def test_create_relationship(self):
        with self.app.app_context():
            from src.database.db import init_db, distroy_db, get_db
            from src.models.question_model import Question, PreQuestion

            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_question_1 = Question(
                    question="Test Question 1",
                    slug="test_question_1",
                    language="en"
                )
                test_question_1.save()
                test_prequestion_1 = PreQuestion(
                    text = "This is an example prequestion",
                    slug = "test_prequestion_1",
                    language = "en"
                )
                test_prequestion_1.save()

                rel = test_prequestion_1.questions.connect(test_question_1)

                pytest.test_question_1 = test_question_1
                pytest.test_prequestion_1 = test_prequestion_1
                pytest.test_prequestion_question_rel_1 = rel
    
    def test_addedOn_field_is_datetime(self):
        assert pytest.test_prequestion_question_rel_1.addedOn is not None
        assert isinstance(
            pytest.test_prequestion_question_rel_1.addedOn,
            datetime
        )
