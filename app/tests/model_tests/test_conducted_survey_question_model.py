import pytest
from src import create_app
from datetime import datetime

class Test_Conducted_Survey_Model:
    app = create_app(
        mode="development",
        static_path="../static",
        templates_path="../templates",
        instance_path="../instance"
    )
    def test_create_node(self):
        with self.app.app_context():
            from src.database.db import get_db, init_db, distroy_db
            from src.models.conducted_survey_question_model import ConductedSurveyQuestion

            distroy_db(self.app)
            init_db(self.app)
            current_transaction = get_db().transaction

            with current_transaction:
                test_conducted_survey_question_1 = ConductedSurveyQuestion()
                test_conducted_survey_question_1.save()
            
            assert test_conducted_survey_question_1.nodeId is not None
            assert test_conducted_survey_question_1.addedOn is not None
            assert isinstance(test_conducted_survey_question_1.addedOn, datetime)
            assert test_conducted_survey_question_1.sentimentSet is True
            assert test_conducted_survey_question_1.sentimentCalculated is False

