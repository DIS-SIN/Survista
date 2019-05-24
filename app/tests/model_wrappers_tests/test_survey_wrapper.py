from src import create_app
import pytest
from src.utils.model_wrappers.survey_wrapper import SurveyWrapper
from datetime import datetime
import pytz

class Test_Survey_Wrapper:

    app = create_app(
        mode="development",
        static_path="../static",
        instance_path="../instance",
        templates_path="../templates"
    )
    
    def test_set_up(self):
        with self.app.app_context():
            from src.database.db import get_db, init_db, distroy_db
            from src.models.survey_model import Survey

            distroy_db(self.app)
            init_db(self.app)

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_1 = Survey(
                    slug = "test_survey_1",
                    language = "en"
                )
                test_survey_1.save()
            
            pytest.test_survey_1 = test_survey_1 # type: Survey
    
    def test_construct_SurveyWrapper(self):
        test_survey_1 = pytest.test_survey_1
        test_survey_wrapper_1 = SurveyWrapper(test_survey_1)
        pytest.test_survey_wrapper_1 = test_survey_wrapper_1 # type: SurveyWrapper
    
    def test_survey_getter(self):
        test_survey_wrapper_1 = pytest.test_survey_wrapper_1 # type: SurveyWrapper
        got_test_survey_1 = test_survey_wrapper_1.survey

        assert got_test_survey_1 == pytest.test_survey_1
    
    def test_survey_setter(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey
            
            current_transaction = get_db().transaction
            with current_transaction:
                test_survey_2 = Survey(
                    slug="test_survey_2",
                    language="en"
                )
                test_survey_2.save()
            
            test_survey_wrapper_1 = pytest.test_survey_wrapper_1 # type: SurveyWrapper

            test_survey_wrapper_1.survey = test_survey_2

            assert test_survey_wrapper_1._survey == test_survey_2
    
    def test_currentVersion_getter_no_versions(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.utils.exceptions.wrapper_exceptions import NoCurrentVersionFound

            current_transction = get_db().transaction
 
            with current_transction:
                test_survey_wrapper_1 = pytest.test_survey_wrapper_1

                with pytest.raises(NoCurrentVersionFound):
                    test_survey_wrapper_1.currentVersion
    
    def test_currentVersion_getter_with_version(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_1 = SurveyVersion(
                    title="Test Survey Version 1",
                    currentVersion=True
                )
                test_survey_version_1.save()
                
                test_survey_wrapper_1 = pytest.test_survey_wrapper_1
                test_survey = test_survey_wrapper_1.survey

                test_survey.versions.connect(test_survey_version_1)
                assert test_survey_version_1 in test_survey.versions
                assert test_survey_wrapper_1.currentVersionNode == test_survey_version_1

    def test_currentVersion_setter_with_node(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_2 = SurveyVersion(
                    title="Test Survey Version 2",
                )
                test_survey_version_2.save()

                test_survey_wrapper_1 = pytest.test_survey_wrapper_1
                test_survey_wrapper_1.currentVersion = test_survey_version_2

                assert test_survey_version_2.currentVersion is True
    
    def test_currentVersion_setter_with_nodeId(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_3 = SurveyVersion(
                    title="Test Survey Version 3"
                )
                test_survey_version_3.save()

                test_survey_wrapper_1 = pytest.test_survey_wrapper_1
                test_survey_wrapper_1.currentVersion = test_survey_version_3.nodeId

                test_survey_version_3.refresh()
                assert test_survey_version_3.currentVersion is True
    
    def test_currentVersion_setter_node_from_another_parent(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion
            from src.utils.exceptions.wrapper_exceptions import VersionDoesNotBelongToNode
            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_4 = SurveyVersion(
                    title="Test Survey Version 4"
                )

                test_survey_version_4.save()
                test_survey_1 = pytest.test_survey_1

                test_survey_1.versions.connect(test_survey_version_4)
                
                test_survey_wrapper_1 = pytest.test_survey_wrapper_1
                with pytest.raises(VersionDoesNotBelongToNode):
                    test_survey_wrapper_1.currentVersion = test_survey_version_4
    def test_set_survey_variables_method(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import SurveyVersion
            from src.utils.exceptions.wrapper_exceptions import VersionDoesNotBelongToNode
            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_wrapper_1 = pytest.test_survey_wrapper_1

                test_survey_wrapper_1.set_survey_variables(
                    some_var="some_var",
                    some_other_var="some_other_var"    
                )

                some_survey = test_survey_wrapper_1.survey
                assert some_survey.some_var == "some_var"
                assert some_survey.some_other_var == "some_other_var"

    def test_setup_for_datetime_filtering_methods(self):
        with self.app.app_context():
            from src.database.db import get_db
            from src.models.survey_model import Survey,SurveyVersion
            
            current_transaction = get_db().transaction
            
            with current_transaction:
                test_survey_3 = Survey(
                    slug="test_survey_3",
                    language="en"
                )
                test_survey_3.save()
                test_survey_version_4 = SurveyVersion(
                    title="Test Survey Version 4",
                )
                test_survey_version_5 = SurveyVersion(
                    title="Test Survey Version 5"
                )
                test_survey_version_6 = SurveyVersion(
                    title="Test Survey Version 6"
                )
                test_survey_version_7 = SurveyVersion(
                    title="Test Survey Version 7"
                )
                test_survey_version_8 = SurveyVersion(
                    title="Test Survey Version 8"
                )
                test_survey_version_4.save()
                test_survey_version_5.save()
                test_survey_version_6.save()
                test_survey_version_7.save()
                test_survey_version_8.save()
                test_survey_3.versions.connect(
                    test_survey_version_4,
                    {'addedOn': datetime(2019,4,21,14,2,40,12,pytz.utc)}
                )
                test_survey_3.versions.connect(
                    test_survey_version_5,
                    {'addedOn': datetime(2019,4,22,14,2,40,12,pytz.utc)}
                )
                test_survey_3.versions.connect(
                    test_survey_version_6,
                    {'addedOn': datetime(2019,4,22,18,2,40,12,pytz.utc)}
                )
                test_survey_3.versions.connect(
                    test_survey_version_7,
                    {'addedOn': datetime(2019,4,23,18,2,40,12,pytz.utc)}
                )
                test_survey_3.versions.connect(
                    test_survey_version_8,
                    {'addedOn': datetime(2019,5,22,18,2,40,12,pytz.utc)}
                )
                test_survey_wrapper_3 = SurveyWrapper(test_survey_3)
                test_survey_wrapper_3.currentVersion = test_survey_version_8
                
                pytest.test_survey_3 = test_survey_3
                pytest.test_survey_version_4 = test_survey_version_4
                pytest.test_survey_version_5 = test_survey_version_5
                pytest.test_survey_version_6 = test_survey_version_6
                pytest.test_survey_version_7 = test_survey_version_7
                pytest.test_survey_version_8 = test_survey_version_8
                pytest.test_survey_wrapper_3 = test_survey_wrapper_3
    def tes_get_survey_versions_lt_datetime(self):
        with self.app.app_context():
            from src.database.db import get_db
            
            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_4 = pytest.test_survey_version_4
                test_survey_version_5 = pytest.test_survey_version_5
                test_survey_version_6 = pytest.test_survey_version_6
                test_survey_version_7 = pytest.test_survey_version_7
                test_survey_version_8 = pytest.test_survey_version_8
                test_survey_wrapper_3 = pytest.test_survey_wrapper_3
                
                nodes = test_survey_wrapper_3.get_survey_versions_lt_datetime(
                    datetime(2019,4,23,18,2,40,12,pytz.utc)
                )
                assert test_survey_version_4 in nodes
                assert test_survey_version_5 in nodes
                assert test_survey_version_6 in nodes 
                assert test_survey_version_7 not in nodes
                assert test_survey_version_8 not in nodes
                assert len(nodes) == 3

                nodes = test_survey_wrapper_3.get_survey_versions_lt_datetime(
                    datetime(2019,4,23,18,2,40,12,pytz.utc),
                    True
                )

                assert test_survey_version_4 in nodes
                assert test_survey_version_5 in nodes
                assert test_survey_version_6 in nodes 
                assert test_survey_version_7 in nodes
                assert test_survey_version_8 not in nodes
                assert len(nodes) == 4
    
    def test_get_survey_versions_gt_datetime(self):
        with self.app.app_context():
            from src.database.db import get_db

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_4 = pytest.test_survey_version_4
                test_survey_version_5 = pytest.test_survey_version_5
                test_survey_version_6 = pytest.test_survey_version_6
                test_survey_version_7 = pytest.test_survey_version_7
                test_survey_version_8 = pytest.test_survey_version_8

                test_survey_wrapper_3 = pytest.test_survey_wrapper_3
                test_survey_wrapper_3 = pytest.test_survey_wrapper_3

                nodes = test_survey_wrapper_3.get_survey_versions_gt_datetime(
                    datetime(2019,4,22,14,2,40,12,pytz.utc)
                )

                assert test_survey_version_4 not in nodes
                assert test_survey_version_5 not in nodes
                assert test_survey_version_6 in nodes 
                assert test_survey_version_7 in nodes
                assert test_survey_version_8 in nodes
                assert len(nodes) == 3

                nodes = test_survey_wrapper_3.get_survey_versions_gt_datetime(
                    datetime(2019,4,22,14,2,40,12,pytz.utc),
                    True
                )
                assert test_survey_version_4 not in nodes
                assert test_survey_version_5 in nodes
                assert test_survey_version_6 in nodes 
                assert test_survey_version_7 in nodes
                assert test_survey_version_8 in nodes
                assert len(nodes) == 4
    
    def test_get_survey_versions_between_datetime(self):
        with self.app.app_context():
            from src.database.db import get_db

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_4 = pytest.test_survey_version_4
                test_survey_version_5 = pytest.test_survey_version_5
                test_survey_version_6 = pytest.test_survey_version_6
                test_survey_version_7 = pytest.test_survey_version_7
                test_survey_version_8 = pytest.test_survey_version_8

                test_survey_wrapper_3 = pytest.test_survey_wrapper_3

                nodes = test_survey_wrapper_3.get_survey_versions_between_datetime(
                    datetime(2019,4,22,14,2,40,12,pytz.utc),
                    datetime(2019,4,23,18,2,40,12,pytz.utc),
                    False,
                    False
                )
                for i in range(0,len(nodes)):
                    nodes[i] = nodes[i].version
                
                assert test_survey_version_4 not in nodes
                assert test_survey_version_5 not in nodes
                assert test_survey_version_6 in nodes
                assert test_survey_version_7 not in nodes
                assert test_survey_version_8 not in nodes
                assert len(nodes) == 1

    def test_get_survey_versions_between_datetime_lower_inclusive_higher_not_inclusive(self):
        with self.app.app_context():
            from src.database.db import get_db

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_4 = pytest.test_survey_version_4
                test_survey_version_5 = pytest.test_survey_version_5
                test_survey_version_6 = pytest.test_survey_version_6
                test_survey_version_7 = pytest.test_survey_version_7
                test_survey_version_8 = pytest.test_survey_version_8

                test_survey_wrapper_3 = pytest.test_survey_wrapper_3
                
                nodes = test_survey_wrapper_3.get_survey_versions_between_datetime(
                    datetime(2019,4,22,14,2,40,12,pytz.utc),
                    datetime(2019,4,23,18,2,40,12,pytz.utc),
                )

                for i in range(0,len(nodes)):
                    nodes[i] = nodes[i].version

                assert test_survey_version_4 not in nodes
                assert test_survey_version_5 in nodes
                assert test_survey_version_6 in nodes
                assert test_survey_version_7 not in nodes
                assert test_survey_version_8 not in nodes
                assert len(nodes) == 2
    
    def test_get_survey_versions_between_datetime_lower_not_inclusive_higher_inclusive(self):
        with self.app.app_context():
            from src.database.db import get_db

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_4 = pytest.test_survey_version_4
                test_survey_version_5 = pytest.test_survey_version_5
                test_survey_version_6 = pytest.test_survey_version_6
                test_survey_version_7 = pytest.test_survey_version_7
                test_survey_version_8 = pytest.test_survey_version_8

                test_survey_wrapper_3 = pytest.test_survey_wrapper_3

                nodes = test_survey_wrapper_3.get_survey_versions_between_datetime(
                    datetime(2019,4,22,14,2,40,12,pytz.utc),
                    datetime(2019,4,23,18,2,40,12,pytz.utc),
                    False,
                    True 
                )
                for i in range(0,len(nodes)):
                    nodes[i] = nodes[i].version
                
                assert test_survey_version_4 not in nodes
                assert test_survey_version_5 not in nodes
                assert test_survey_version_6 in nodes
                assert test_survey_version_7 in nodes
                assert test_survey_version_8 not in nodes
                assert len(nodes) == 2
    def test_get_survey_versions_between_datetime_lower_inclusive_higher_inclusive(self):
        with self.app.app_context():
            from src.database.db import get_db

            current_transaction = get_db().transaction

            with current_transaction:
                test_survey_version_4 = pytest.test_survey_version_4
                test_survey_version_5 = pytest.test_survey_version_5
                test_survey_version_6 = pytest.test_survey_version_6
                test_survey_version_7 = pytest.test_survey_version_7
                test_survey_version_8 = pytest.test_survey_version_8

                test_survey_wrapper_3 = pytest.test_survey_wrapper_3
                
                nodes = test_survey_wrapper_3.get_survey_versions_between_datetime(
                    datetime(2019,4,22,14,2,40,12,pytz.utc),
                    datetime(2019,4,23,18,2,40,12,pytz.utc),
                    True,
                    True 
                )
                for i in range(0,len(nodes)):
                    nodes[i] = nodes[i].version
                
                assert test_survey_version_4 not in nodes
                assert test_survey_version_5 in nodes
                assert test_survey_version_6 in nodes
                assert test_survey_version_7 in nodes
                assert test_survey_version_8 not in nodes
                assert len(nodes) == 3 

    def test_SurveyWrapper_dump_method(self):
        with self.app.app_context():
            from src.database.db import get_db

            current_transaction = get_db().transaction

            test_survey_wrapper_3 = pytest.test_survey_wrapper_3

            with current_transaction:
                output = test_survey_wrapper_3.dump()
            
            pytest.test_output_1 = output
    
    









            


