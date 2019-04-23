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
                new_conducted_survey = ConductedSurvey(
                    title="Test ConductedSurvey 1",
                    slug="test_conducted_survey_1",
                    conductedOn=datetime(2019, 4, 21),
                    language="en")
                new_conducted_survey.save()

            node = transaction_factory.cypher_query(
                "MATCH (s:ConductedSurvey) RETURN s")
            assert new_conducted_survey.title == \
                node[0][0][0]._properties['title']
            assert isinstance(new_conducted_survey.addedOn, datetime)
            assert isinstance(new_conducted_survey.updatedOn, datetime)
            pytest.conducted_survey_last_updatedOn = \
                new_conducted_survey.updatedOn

    def test_language_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from neomodel.exceptions import RequiredProperty
            from src.models.conducted_survey_model import ConductedSurvey
            transaction_factory = get_db()
            current_transaction = transaction_factory.transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    new_conducted_survey = ConductedSurvey(
                        title="Test ConductedSurvey 2",
                        conductedOn=datetime(2019, 4, 21),
                        slug="test_conducted_survey_2")
                    new_conducted_survey.save()
            current_transaction = transaction_factory.transaction
            with current_transaction:
                new_conducted_survey.language = "en"
                new_conducted_survey.save()

    def test_language_options_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exception import DeflateError
            current_transaction = get_db().transaction
            with pytest.raises(DeflateError):
                with current_transaction:
                    new_conducted_survey = ConductedSurvey(
                        title="Test ConductedSurvey 3",
                        slug="test_conducted_survey_3",
                        conductedOn=datetime(2019, 4, 21),
                        language="Japanese")
                    new_conducted_survey.save()
            current_transaction = get_db().transaction
            with current_transaction:
                new_conducted_survey.language = "en"
                new_conducted_survey.save()
            current_transaction = get_db().transaction
            with current_transaction:
                test_conducted_survey_4 = ConductedSurvey(
                    title="Test ConductedSurvey 4",
                    slug="test_conducted_survey_4",
                    conductedOn=datetime(2019, 4, 21),
                    language="fr"
                )
                test_conducted_survey_4.save()

    def test_title_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_conducted_survey_5 = ConductedSurvey(
                        slug="test_conducted_survey_5",
                        conductedOn=datetime(2019, 4, 21),
                        language="en"
                    )
                    test_conducted_survey_5.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_conducted_survey_5.title = "Test ConductedSurvey 5"
                test_conducted_survey_5.save()

    def test_slug_required_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_conducted_survey_6 = ConductedSurvey(
                        title="Test conducted_survey 6",
                        conductedOn=datetime(2019, 4, 21),
                        language="en"
                    )
                    test_conducted_survey_6.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_conducted_survey_6.slug = "test_conducted_survey_6"
                test_conducted_survey_6.save()

    def test_slug_unique_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.conducted_survey_model import ConductedSurvey
            from neomodel.exceptions import UniqueProperty

            current_transaction = get_db().transaction
            with pytest.raises(UniqueProperty):
                with current_transaction:
                    test_conducted_survey_6 = ConductedSurvey(
                        slug="test_conducted_survey_6",
                        title="Test conducted_survey 7",
                        conductedOn=datetime(2019, 4, 21),
                        language="en"
                    )
                    test_conducted_survey_6.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_conducted_survey_6.slug = "test_conducted_survey_7"
                test_conducted_survey_6.save()

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
