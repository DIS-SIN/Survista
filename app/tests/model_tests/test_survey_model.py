import pytest
from src import create_app
from datetime import datetime


class Test_Survey_Model_CRUD():
    app = create_app(mode="development",
                     static_path="../static",
                     templates_path="../templates",
                     instance_path="../instance")

    def test_create_node(self):
        with self.app.app_context():
            from src.database.db import get_db, distroy_db, init_db
            distroy_db(self.app)
            init_db(self.app)

            from src.models.survey_model import Survey
            transaction_factory = get_db()
            current_transaction = transaction_factory.transaction
            with current_transaction:
                from src.models.survey_model import Survey
                test_survey_1 = Survey(title="Test Survey 1",
                                    slug="test_survey_1",
                                    language="en")
                test_survey_1.save()
            
            pytest.test_survey_1 = test_survey_1

    def test_nodeId_field_is_generated(self):
        assert pytest.test_survey_1.nodeId is not None
    
    def test_addedOn_field_is_datetime(self):
        assert pytest.test_survey_1.addedOn is not None
        assert isinstance(pytest.test_survey_1.addedOn, datetime)

    def test_addedOn_field_is_equal_to_updatedOn_field_on_creation(self):
        assert pytest.test_survey_1.updatedOn == pytest.test_survey_1.addedOn

    def test_language_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from neomodel.exceptions import RequiredProperty
            from src.models.survey_model import Survey
            transaction_factory = get_db()
            current_transaction = transaction_factory.transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_survey_2 = Survey(title="Test Survey 2",
                                           slug="test_survey_2")
                    test_survey_2.save()
            current_transaction = transaction_factory.transaction
            with current_transaction:
                test_survey_2.language = "en"
                test_survey_2.save()

    def test_language_options_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            from neomodel.exception import DeflateError
            current_transaction = get_db().transaction
            with pytest.raises(DeflateError):
                with current_transaction:
                    test_survey_3 = Survey(title="Test Survey 3",
                                           slug="test_survey_3",
                                           language="Japanese")
                    test_survey_3.save()

            with current_transaction:
                test_survey_3.language = "en"
                test_survey_3.save()
                
                test_survey_3.language = "fr"
                test_survey_3.save()

    def test_title_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_survey_4 = Survey(
                        slug="test_survey_4",
                        language="en"
                    )
                    test_survey_4.save()

            with current_transaction:
                test_survey_4.title = "Test Survey 4"
                test_survey_4.save()

    def test_slug_required_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_survey_5 = Survey(
                        title="Test survey 5",
                        language="en"
                    )
                    test_survey_5.save()

            with current_transaction:
                test_survey_5.slug = "test_survey_5"
                test_survey_5.save()

    def test_slug_unique_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            from neomodel.exceptions import UniqueProperty

            current_transaction = get_db().transaction
            with pytest.raises(UniqueProperty):
                with current_transaction:
                    test_survey_6 = Survey(
                        slug="test_survey_5",
                        title="Test survey 6",
                        language="en"
                    )
                    test_survey_6.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_survey_6.slug = "test_survey_6"
                test_survey_6.save()

    def test_update_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            current_transation = get_db().transaction
            with current_transation:
                test_survey_1 = Survey.nodes.get(slug="test_survey_1")
                test_survey_1.title = "Test Survey 1 Updated"
                test_survey_1.save()

            assert test_survey_1.updatedOn > pytest.test_survey_1.updatedOn

    def test_delete_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            current_transaction = get_db().transaction
            with current_transaction:
                Survey.nodes.get(slug="test_survey_1").delete()

            deletedNode = get_db().cypher_query(
                "MATCH (s:Survey {slug: 'test_survey_1'}) RETURN s"
            )
            assert not deletedNode[0]
