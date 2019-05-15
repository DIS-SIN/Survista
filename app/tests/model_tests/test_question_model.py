from src import create_app
from datetime import datetime
import pytest


class Test_Question_Model_CRD():
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
                test_question_1 = Question(
                                    question = "Test Question 1",
                                    slug="test_question_1",
                                    language="en"
                                )
                test_question_1.save()
            pytest.test_question_1 = test_question_1
    
    def test_nodeId_field_is_generated(self):
        assert pytest.test_question_1.nodeId is not None

    def test_addedOn_field_is_datetime(self):
        assert pytest.test_question_1.addedOn is not None
        assert isinstance(pytest.test_question_1.addedOn, datetime)

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

    def test_language_options_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exception import DeflateError
            current_transaction = get_db().transaction
            with pytest.raises(DeflateError):
                with current_transaction:
                    test_question_3 = Question(question="Test Question 3",
                                            slug="test_question_3",
                                            language="Japanese")
                    test_question_3.save()
        
            with current_transaction:
                test_question_3.language = "en"
                test_question_3.save()

                test_question_3.language = "fr"
                test_question_3.save()

    def test_slug_required_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_question_5 = Question(
                        question="Test Question 5",
                        language="en"
                    )
                    test_question_5.save()

            with current_transaction:
                test_question_5.slug = "test_question_5"
                test_question_5.save()
    
    def test_slug_unique_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exceptions import UniqueProperty

            current_transaction = get_db().transaction
            with pytest.raises(UniqueProperty):
                with current_transaction:
                    test_question_6 = Question(
                        slug="test_question_1",
                        question="Test question 6",
                        language="en"
                    )
                    test_question_6.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_question_6.slug = "test_question_6"
                test_question_6.save()
    
    def test_question_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_question_6 = Question(
                        slug = "test_question_7",
                        language = "en"
                    )
                    test_question_6.save()
            
            with current_transaction:
                test_question_6.question = "Test Question 7"
                test_question_6.save()
    
    def test_question_unique_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel.exceptions import UniqueProperty

            current_transaction = get_db().transaction
            with pytest.raises(UniqueProperty):
                with current_transaction:
                    test_question_7 = Question(
                        slug = "test_question_8",
                        language = "en",
                        question = "Test Question 1"
                    )
                    test_question_7.save()
            with current_transaction:
                test_question_7.question = "Test Question 8"
                test_question_7.save()

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



