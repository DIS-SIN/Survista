import pytest
from src import create_app
from datetime import datetime
import pytz

class Test_ConductedSurvey_Model_CRUD():
    app = create_app(mode="development",
                     static_path="../static",
                     templates_path="../templates",
                     instance_path="../instance")

    def test_create_node(self):
        with self.app.app_context():
            from src.database.db import get_db, distroy_db, init_db
            distroy_db(self.app)
            init_db(self.app)
            from src.models.conducted_survey_model import ConductedSurvey
            transaction_factory = get_db()
            current_transaction = transaction_factory.transaction
            with current_transaction:
                from src.models.conducted_survey_model import ConductedSurvey
                test_conducted_survey_1 = ConductedSurvey()
                test_conducted_survey_1.save()

            pytest.test_conducted_survey_1 = test_conducted_survey_1
            pytest.nodeId = test_conducted_survey_1.nodeId

    def test_nodeId_field_is_generated(self):
        assert pytest.test_conducted_survey_1.nodeId is not None
    
    def test_addedOn_field_is_datetime(self):
        assert pytest.test_conducted_survey_1.addedOn is not None
        assert isinstance(pytest.test_conducted_survey_1.addedOn, datetime)
    
    def test_addedOn_field_is_equal_to_updatedOn_field_on_creation(self):
        assert pytest.test_conducted_survey_1.addedOn == pytest.test_conducted_survey_1.updatedOn
    
    def test_sentimentSet_field_is_true(self):
        assert pytest.test_conducted_survey_1.sentimentSet is True

    def test_status_options_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exception import DeflateError
            current_transaction = get_db().transaction
            with pytest.raises(DeflateError):
                with current_transaction:
                    test_conducted_survey_2 = ConductedSurvey(
                        status="not-valid"
                    )
                    test_conducted_survey_2.save()
            with current_transaction:
                test_conducted_survey_2.status = "active"
                test_conducted_survey_2.save()
                test_conducted_survey_2.status = "abandoned"
                test_conducted_survey_2.save()
                test_conducted_survey_2.status = "closed"
                test_conducted_survey_2.save()
    def test_setClosedOn_method(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey

            current_transaction = get_db().transaction
            with current_transaction:
                test_conducted_survey_3 = ConductedSurvey()
                test_conducted_survey_3.set_closedOn()
                test_conducted_survey_3.save()
            
            assert test_conducted_survey_3.closedOn is not None
            assert isinstance(test_conducted_survey_3.closedOn, datetime)
            
    def test_update_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            current_transation = get_db().transaction
            with current_transation:
                test_conducted_survey_1 = ConductedSurvey.nodes.all()[0]
                test_conducted_survey_1.googleSentimentScore = 0.4
                test_conducted_survey_1.save()

            assert test_conducted_survey_1.updatedOn >\
                pytest.test_conducted_survey_1.updatedOn

    def test_delete_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            current_transaction = get_db().transaction
            with current_transaction:
                test_conducted_survey_1 = ConductedSurvey.nodes.all()[0]
                test_conducted_survey_1.delete()

            deletedNode = get_db().cypher_query(
                "MATCH (s:ConductedSurvey {nodeId: " + 
                f"'{test_conducted_survey_1.nodeId}'" + "}) " +
                "RETURN s"
            )
            assert not deletedNode[0]
