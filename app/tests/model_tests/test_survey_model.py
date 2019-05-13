import pytest
from src import create_app
from datetime import datetime


class Test_Survey_Model_CRD():
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
                test_survey_1 = Survey(
                                        slug="test_survey_1",
                                        language="en"
                                    )
                test_survey_1.save()
            
            pytest.test_survey_1 = test_survey_1

    def test_nodeId_field_is_generated(self):
        assert pytest.test_survey_1.nodeId is not None
    
    def test_addedOn_field_is_datetime(self):
        assert pytest.test_survey_1.addedOn is not None
        assert isinstance(pytest.test_survey_1.addedOn, datetime)

    def test_language_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from neomodel.exceptions import RequiredProperty
            from src.models.survey_model import Survey
            transaction_factory = get_db()
            current_transaction = transaction_factory.transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_survey_2 = Survey(
                        slug="test_survey_2"
                    )
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
                    test_survey_3 = Survey(
                        slug="test_survey_3",
                        language="Japanese"
                    )
                    test_survey_3.save()

            with current_transaction:
                test_survey_3.language = "en"
                test_survey_3.save()
                
                test_survey_3.language = "fr"
                test_survey_3.save()

    def test_slug_required_constrain(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_survey_5 = Survey(
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
                        language="en"
                    )
                    test_survey_6.save()

            current_transaction = get_db().transaction
            with current_transaction:
                test_survey_6.slug = "test_survey_6"
                test_survey_6.save()

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

class Test_SurveyVersion_Model_CRD:
    app = create_app(mode="development",
                     static_path="../static",
                     templates_path="../templates",
                     instance_path="../instance")

    def test_create_node(self):
        with self.app.app_context():
            from src.database.db import get_db, distroy_db, init_db
            from src.models.survey_model import SurveyVersion
            distroy_db(self.app)
            init_db(self.app)
            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_1 = SurveyVersion(
                    title="Survey Version 1"
                )
                test_survey_version_1.save()
            
            pytest.test_survey_version_1 = test_survey_version_1
    
    def test_nodeId_field_is_generated(self):
        assert pytest.test_survey_version_1.nodeId is not None
    
    def test_currentVersion_field_is_default_false(self):
        assert pytest.test_survey_version_1.currentVersion is False

    def test_title_required_constraint(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion
            from neomodel.exceptions import RequiredProperty

            current_transaction = get_db().transaction
            with pytest.raises(RequiredProperty):
                with current_transaction:
                    test_survey_version_2 = SurveyVersion(
                    )
                    test_survey_version_2.save()

            with current_transaction:
                test_survey_version_2.title = "Survey Version 2"
                test_survey_version_2.save()

class Test_Survey_SurveyVersion_Relationship:

    app = create_app(
        mode='development',
        static_path='../static',
        templates_path='../templates',
        instance_path='../instance'
    )
    
    def test_create_relationship(self):
        with self.app.app_context():
            from src.database.db import get_db, init_app, distroy_db
            from src.models.survey_model import Survey, SurveyVersion
            
            distroy_db(self.app)
            init_app(self.app)

            current_transaction = get_db().transaction
            with current_transaction:
                test_Survey_1 = Survey(
                    slug="test_survey_1",
                    language="en"
                )
                test_SurveyVersion_1 = SurveyVersion(
                    title="Test Survey 1"
                )
                test_Survey_1.save()
                test_SurveyVersion_1.save()
                rel = test_Survey_1.versions.connect(test_SurveyVersion_1)

            assert len(test_SurveyVersion_1.survey.all()) == 1
            
            pytest.test_Survey_SurveyVersion_rel_1 = rel
            pytest.test_Survey_1 = test_Survey_1
            pytest.test_SurveyVersion_1 = test_SurveyVersion_1
    def test_addedOn_field_is_datetime(self):
        assert pytest.test_Survey_SurveyVersion_rel_1.addedOn is not None
        assert isinstance(pytest.test_Survey_SurveyVersion_rel_1.addedOn, datetime)
    
    def test_one_cardinality_for_SurveyVersion(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion, Survey
            from neomodel.exceptions import AttemptedCardinalityViolation
            current_transaction = get_db().transaction
            with pytest.raises(AttemptedCardinalityViolation):
                with current_transaction:
                    test_Survey_2 = Survey(
                        slug='test_survey_2',
                        language='en'
                    )
                    test_Survey_2.save()
                    test_SurveyVersion_1 = pytest.test_SurveyVersion_1
                    test_SurveyVersion_1.survey.connect(test_Survey_2)
    
    def test_one_or_mode_cardinality_for_Survey(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion

            current_transaction = get_db().transaction

            with current_transaction:
                test_Survey_1 = pytest.test_Survey_1
                test_SurveyVersion_2 = SurveyVersion(
                    title="Test SurveyVersion 2"
                )
                test_SurveyVersion_2.save()
                test_Survey_1.versions.connect(test_SurveyVersion_2)
            
            assert len(test_Survey_1.versions.all()) == 2


                



            


    
            
