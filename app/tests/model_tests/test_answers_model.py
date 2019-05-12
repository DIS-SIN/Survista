import pytest
from src import create_app


class Test_Answers_Model:
    app = create_app(
        mode="development",
        static_path="../static",
        templates_path="../templates",
        instance_path="../instance"
    )
    def test_create_answer_node(self):
        with self.app.app_context():
            from src.database.db import get_db, init_db, distroy_db
            distroy_db(self.app)
            init_db(self.app)
            from src.models.answers_model import Answer
            current_transaction = get_db().transaction
            with current_transaction:
                test_answer_1 = Answer(
                    answer="this is an answer 1"
                )
                test_answer_1.save()
            node = get_db().cypher_query(
                "MATCH (a:Answer) RETURN a"
            )
            assert test_answer_1.answer == \
                node[0][0][0]._properties['answer']
            assert test_answer_1.updatedOn is not None
            assert test_answer_1.addedOn is not None
            assert test_answer_1.id is not None
            
    def test_answer_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.answers_model import Answer
            current_transaction = get_db().transaction
            from neomodel.exception import RequiredProperty
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_answer_2 = Answer()
                    test_answer_2.save()
            with current_transaction:
                test_answer_2.answer = "this is an answer 2"
                test_answer_2.save()


    def test_update_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.answers_model import Answer
            current_transaction = get_db().transaction
            with current_transaction:
                test_answer_1 = Answer.nodes.get(
                    answer="this is an answer 1"
                )
                oldUpdatedOn = test_answer_1.updatedOn
                test_answer_1.answer = "this is an updated answer 1"
                test_answer_1.save()
                assert test_answer_1.updatedOn > oldUpdatedOn
            
            node = get_db().cypher_query(
                'MATCH (a:Answer {answer:"this is an updated answer 1"}) ' +
                'RETURN a'
            )
            assert node[0]

    def test_delete_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.answers_model import Answer
            current_transaction = get_db().transaction
            with current_transaction:
                test_answer_2 = Answer.nodes.get(
                    answer ="this is an answer 2"
                )
                test_answer_2.delete()
            node = get_db().cypher_query(
                "MATCH (a:Answer {answer: 'this is an answer 2'}) " +
                "RETURN a"
            )
            assert not node[0]
            
      
