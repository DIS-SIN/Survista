import pytest
from src import create_app
from src.utils.model_wrappers.survey_wrapper import SurveyVersionWrapper, SurveyWrapper

class Test_SurveyVersion_Wrapper:
    app = create_app(
        mode="development",
        static_path="../static",
        instance_path="../instance",
        templates_path="../templates"
    )
    def test_set_up(self):
        with self.app.app_context():
            from src.database.db import get_db, distroy_db, init_db
            from src.models.survey_model import SurveyVersion
            
            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_1 = SurveyVersion(
                    title="Test Survey Version 1"
                )
                test_survey_version_1.save()

            pytest.test_survey_version_1 = test_survey_version_1
    
    def test_construct_wrapper(self):
        test_survey_version_1 = pytest.test_survey_version_1
        test_survey_version_wrapper_1 = SurveyVersionWrapper(test_survey_version_1)
        pytest.test_survey_version_wrapper_1 = test_survey_version_wrapper_1
    
    def test_version_getter(self):
        test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1
        got_test_survey_version_1 = test_survey_version_wrapper_1.version

        assert got_test_survey_version_1 == pytest.test_survey_version_1
    
    def test_nodeId_set(self):

        test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1
        got_test_survey_version_1_nodeId = test_survey_version_wrapper_1.nodeId

        assert got_test_survey_version_1_nodeId == pytest.test_survey_version_1.nodeId
    
    def test_title_is_set(self):
        
        test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1
        got_test_survey_version_1_title = test_survey_version_wrapper_1.title

        assert got_test_survey_version_1_title == pytest.test_survey_version_1.title

    def test_add_questions_method(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.question_model import Question
            from neomodel import RelationshipManager
            current_transaction = get_db().transaction
            test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1
            with current_transaction:
                test_question_1 = Question(
                    question = "Test Question 1",
                    slug = "test_question_1",
                    language = "en"
                )
                test_question_1.save()

                test_survey_version_wrapper_1.add_question(test_question_1)
                assert isinstance(
                    test_survey_version_wrapper_1._questions,
                    RelationshipManager
                )

                test_question_2 = Question(
                    question = "Test Question 2",
                    slug = "test_question_2",
                    language = "en"
                )

                test_survey_version_wrapper_1.add_question(test_question_2)

                assert len(test_survey_version_wrapper_1._version.questions) == 2
            
            pytest.test_question_1 = test_question_1
            pytest.test_question_2 = test_question_2
    
    def test_question_getter(self):
        with self.app.app_context():
            from src.database.db import get_db
            
            test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1
            test_question_1 = pytest.test_question_1
            test_question_2 = pytest.test_question_2

            current_transaction = get_db().transaction

            with current_transaction:
                questions = test_survey_version_wrapper_1.questions
                questionNodes = [i.question for i in questions]
                assert len(questions) == 2
                assert test_question_1 in questionNodes
                assert test_question_2 in questionNodes

    def test_dump_method(self):
        with self.app.app_context():
            from src.database.db import get_db

            test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1

            current_transaction = get_db().transaction

            with current_transaction:

                test_output_1 = test_survey_version_wrapper_1.dump()
            
            pytest.test_output_1 = test_output_1

    def test_empty_survey_in_dump(self):
        test_output_1 = pytest.test_output_1
        assert test_output_1['survey'] == {}
    
    def test_empty_previousVersions_in_dump(self):
        test_output_1 = pytest.test_output_1
        assert test_output_1['previousVersions'] == []   
   
    def test_parent_wrapper_assignment(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey

            current_transaction = get_db().transaction
            test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1

            with current_transaction:

                test_survey_1 = Survey(
                    language="en",
                    slug="test_survey_1"
                )

                test_survey_1.save()

                test_survey_1.versions.connect(
                    test_survey_version_wrapper_1.version
                )

                test_survey_wrapper_1 = SurveyWrapper(test_survey_1)
                pytest.test_survey_wrapper_1 = test_survey_wrapper_1
                test_survey_version_wrapper_1.parent_wrapper = test_survey_wrapper_1

                assert test_survey_version_wrapper_1.parent_wrapper == test_survey_wrapper_1
    
    def test_dump_with_survey(self):
        with self.app.app_context():
            from src.database.db import get_db
            
            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_wrapper_1 = pytest.test_survey_version_wrapper_1

                test_output_2 = test_survey_version_wrapper_1.dump()
            
            pytest.test_output_2 = test_output_2
    
    def test_survey_in_dump_with_survey(self):
        test_output_2 = pytest.test_output_2
        assert isinstance(test_output_2['survey'], dict)
        assert bool(test_output_2['survey']) is True
    
    def test_empty_previousVersions_in_dump_with_survey(self):
        test_output_2 = pytest.test_output_2
        assert test_output_2['previousVersions'] == [] 
    

    def test_CurrentVersion_dump_method(self):
        with self.app.app_context():
            from src.database.db import get_db

            current_transaction = get_db().transaction
            
            test_survey_wrapper_1  = pytest.test_survey_wrapper_1
            test_survey_version_1 = pytest.test_survey_version_1

            with current_transaction:

                test_survey_wrapper_1.currentVersion = test_survey_version_1

                test_output_3 = test_survey_wrapper_1.currentVersion.dump()

            pytest.test_output_3 = test_output_3
    
    def test_empty_previousVersions_in_CurrentVersion_dump(self):
        test_output_3 = pytest.test_output_3
        assert test_output_3['previousVersions'] == []
    
    def test_survey_in_CurrentVersion_dump(self):
        test_output_3 = pytest.test_output_3
        assert isinstance(test_output_3['survey'], dict)
        assert bool(test_output_3['survey']) is True

        with pytest.raises(KeyError):
            test_output_3['survey']['currentVersionNode']
    
    def test_dump_with_previousVersions(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_wrapper_1 = pytest.test_survey_wrapper_1

                test_survey_version_2 = SurveyVersion(
                    title = 'Test Survey Version 2'
                )

                test_survey_version_2.save()

                test_survey_version_3 = SurveyVersion(
                    title = 'Test Survey Version 3'
                )

                test_survey_version_3.save()

                test_survey_wrapper_1.currentVersion = test_survey_version_2
                test_survey_wrapper_1.currentVersion = test_survey_version_3

                pytest.test_survey_version_3 = test_survey_version_3
                pytest.test_survey_version_2 = test_survey_version_2

                pytest.test_output_4 = test_survey_wrapper_1.currentVersion.dump()
    
    def test_previousVersions_in_dump_with_previousVersions(self):

        test_output_4 = pytest.test_output_4 
        assert len(test_output_4['previousVersions']) == 2
        assert test_output_4['previousVersions'][0]['nodeId'] == pytest.test_survey_version_2.nodeId
        assert test_output_4['previousVersions'][1]['nodeId'] == pytest.test_survey_version_1.nodeId











            
                




            

                
