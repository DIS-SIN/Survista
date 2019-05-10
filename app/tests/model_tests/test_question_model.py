from src import create_app
from datetime import datetime
import pytest


class Test_Question_Model_CRUD():
    app = create_app(mode="development",
                     static_path="../static",
                     templates_path="../templates",
                     instance_path="../instance")

    def test_create_node(self):
        with self.app.app_context():
            from src.database.db import get_db, distroy_db, init_db
            distroy_db(self.app)
            init_db(self.app)
            from src.models.question_model import Question
            transaction_factory = get_db()
            current_transaction = transaction_factory.transaction
            with current_transaction:
                test_question_1 = Question(question="Test Question 1",
                                        slug="test_question_1",
                                        language="en")
                test_question_1.save()
            pytest.test_question_1 = test_question_1
    
    def test_nodeId_field_is_generated(self):
        assert pytest.test_question_1.nodeId is not None

    def test_addedOn_field_is_datetime(self):
        assert pytest.test_question_1.addedOn is not None
        assert isinstance(pytest.test_question_1.addedOn, datetime)

    def test_updatedOn_field_is_datetime(self):
        assert pytest.test_question_1.updatedOn is not None
        assert isinstance(pytest.test_question_1.updatedOn, datetime)
    
    def test_addedOn_field_is_equal_to_updatedOn_field_on_creation(self):
        assert pytest.test_question_1.addedOn == pytest.test_question_1.updatedOn

    def test_language_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from neomodel.exceptions import RequiredProperty
            from src.models.question_model import Question
            transaction_factory = get_db()
            current_transaction = transaction_factory.transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_question_2 = Question(question="Test Question 2",
                                            slug="test_question_2")
                    test_question_2.save()
            with current_transaction:
                test_question_2.language = "en"
                test_question_2.save()
    # TODO
    # Fix the rest of the tests
    def test_language_options_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exception import DeflateError
            current_transaction = get_db().transaction
            with pytest.raises(DeflateError):
                with current_transaction:
                    new_question = Question(question="Test Question 3",
                                            slug="test_question_3",
                                            language="Japanese")
                    new_question.save()
            current_transaction = get_db().transaction
            with current_transaction:
                new_question.language = "en"
                new_question.save()
            current_transaction = get_db().transaction
            with current_transaction:
                test_question_4 = Question(
                    question="Test Question 4",
                    slug="test_question_4",
                    language="fr"
                )
                test_question_4.save()

    def test_question_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_question_5 = Question(
                        slug="test_question_5",
                        language="en",
                    )
                    test_question_5.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_question_5.question = "Test Question 5"
                test_question_5.save()

    def test_slug_required_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_question_6 = Question(
                        question="Test question 6",
                        language="en"
                    )
                    test_question_6.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_question_6.slug = "test_question_6"
                test_question_6.save()

    def test_slug_unique_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exceptions import UniqueProperty

            current_transaction = get_db().transaction
            with pytest.raises(UniqueProperty):
                with current_transaction:
                    test_question_6 = Question(
                        slug="test_question_6",
                        question="Test question 7",
                        language="en"
                    )
                    test_question_6.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_question_6.slug = "test_question_7"
                test_question_6.save()

    def test_update_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            current_transation = get_db().transaction
            with current_transation:
                test_question_1 = Question.nodes.get(slug="test_question_1")
                test_question_1.title = "Test Question 1 Updated"
                test_question_1.save()

            updatedNode = get_db().cypher_query(
                "MATCH (s:Question {slug: 'test_question_1'}) RETURN s")
            assert test_question_1.title == \
                updatedNode[0][0][0]._properties['title']
            assert test_question_1.updatedOn > pytest.question_last_updatedOn

    def test_delete_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            current_transaction = get_db().transaction
            with current_transaction:
                Question.nodes.get(slug="test_question_1").delete()

            deletedNode = get_db().cypher_query(
                "MATCH (s:Question {slug: 'test_question_1'}) RETURN s"
            )
            assert not deletedNode[0]
