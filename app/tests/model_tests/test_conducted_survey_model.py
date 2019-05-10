import pytest
from src import create_app
from datetime import datetime


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
                test_conducted_survey_1 = ConductedSurvey(
                    title="Test ConductedSurvey 1",
                    slug="test_conducted_survey_1",
                    completedOn=datetime(2019, 4, 21),
                    respondentId="some_hash",
                    token="some_other_hash_1",
                    status="closed"
                )
                test_conducted_survey_1.save()

            pytest.test_conducted_survey_1 = test_conducted_survey_1
            assert new_conducted_survey.nodeId is not None
            assert isinstance(new_conducted_survey.addedOn, datetime)
            assert isinstance(new_conducted_survey.updatedOn, datetime)
            pytest.conducted_survey_last_updatedOn = \
                new_conducted_survey.updatedOn

    def test_nodeId_field_is_generated(self):
        assert pytest.test_conducted_survey_1.nodeId is not None
    
    def test_addedOn_field_is_datetime(self):
        assert pytest.test_conducted_survey_1.addedOn is not None
        assert isinstance(pytest.test_conducted_survey_1.addedOn, datetime)
    
    def test_addedOn_field_is_equal_to_updatedOn_field_on_creation(self):
        assert pytest.test_conducted_survey_1.addedOn == pytest.test_conducted_survey_1.updatedOn

    def test_title_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_conducted_survey_2 = ConductedSurvey(
                        slug="test_conducted_survey_2",
                        completedOn=datetime(2019, 4, 21),
                        respondentId="some_hash",
                        token="some_other_hash_2",
                        status="closed"
                    )
                    test_conducted_survey_2.save()

            with current_transaction:
                test_conducted_survey_2.title = "Test ConductedSurvey 2"
                test_conducted_survey_2.save()

    def test_slug_unique_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exceptions import UniqueProperty

            current_transaction = get_db().transaction
            with pytest.raises(UniqueProperty):
                with current_transaction:
                    test_conducted_survey_4 = ConductedSurvey(
                        slug="test_conducted_survey_3",
                        title="Test conducted_survey 4",
                        completedOn=datetime(2019, 4, 21),
                        respondentId="some_hash",
                        token="some_other_hash_4",
                        status="closed"
                    )
                    test_conducted_survey_4.save()

            with current_transaction:
                test_conducted_survey_4.slug = "test_conducted_survey_4"
                test_conducted_survey_4.save()

    def test_respondantId_required_contraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exceptions import RequiredProperty
            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_conducted_survey_5 = ConductedSurvey(
                        slug="test_conducted_survey_5",
                        title="Test conducted survey 5",
                        completedOn=datetime(2019, 4, 21),
                        token="some_other_hash_5",
                        status="closed"
                    )
                    test_conducted_survey_5.save()

            with current_transaction:
                test_conducted_survey_5.respondentId = "some-hash"
                test_conducted_survey_5.save()

    def test_token_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exceptions import RequiredProperty
            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_conducted_survey_6 = ConductedSurvey(
                        slug="test_conducted_survey_6",
                        title="test conducted_survey_6",
                        completedOn=datetime(2019, 4, 21),
                        respondentId="some-hash",
                        status="closed"
                    )
                    test_conducted_survey_6.save()

            with current_transaction:
                test_conducted_survey_6.token = "some_other_hash_6"
                test_conducted_survey_6.save()

    def test_status_options_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exception import DeflateError
            current_transaction = get_db().transaction
            with pytest.raises(DeflateError):
                with current_transaction:
                    test_conducted_survey_10 = ConductedSurvey(
                        slug="test_conducted_survey_10",
                        title="test_conducted_survey_10",
                        completedOn=datetime(2019, 4, 21),
                        token="some_other_hash_8",
                        status="not-valid",
                        respondentId="some-hash",
                    )
                    test_conducted_survey_10.save()
            with current_transaction:
                test_conducted_survey_10.status = "active"
                test_conducted_survey_10.save()
                test_conducted_survey_10.status = "abandoned"
                test_conducted_survey_10.save()
                test_conducted_survey_10.status = "closed"
                test_conducted_survey_10.save()
    def test_completedOn_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exceptions import RequiredProperty
            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_conducted_survey_11 = ConductedSurvey(
                        slug="test_conducted_survey_11",
                        title="test conducted_survey_11",
                        token="some_other_hash_9",
                        respondentId="some-hash",
                        status="closed"
                    )
                    test_conducted_survey_11.save()
            with current_transaction:
                test_conducted_survey_11.completedOn = datetime(2019, 4, 21)
                test_conducted_survey_11.save()
    def test_update_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            current_transation = get_db().transaction
            with current_transation:
                test_conducted_survey_1 = ConductedSurvey.nodes.get(
                    slug="test_conducted_survey_1")
                test_conducted_survey_1.title = \
                    "Test ConductedSurvey 1 Updated"
                test_conducted_survey_1.save()

            updatedNode = get_db().cypher_query(
                "MATCH (s:ConductedSurvey {slug: 'test_conducted_survey_1'})" +
                "RETURN s")
            assert test_conducted_survey_1.title == \
                updatedNode[0][0][0]._properties['title']
            assert test_conducted_survey_1.updatedOn >\
                pytest.conducted_survey_last_updatedOn

    def test_delete_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            current_transaction = get_db().transaction
            with current_transaction:
                ConductedSurvey.nodes.get(
                    slug="test_conducted_survey_1").delete()

            deletedNode = get_db().cypher_query(
                "MATCH (s:ConductedSurvey {slug: 'test_conducted_survey_1'})" +
                "RETURN s"
            )
            assert not deletedNode[0]
