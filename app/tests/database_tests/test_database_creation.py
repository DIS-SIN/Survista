
class Test_Application_Database_Config_Initialisation():

    def test_application_database_initialisation(self):
        """testing initialising the application initialisation"""
        from src import create_app
        app = create_app(mode='development',
                         static_path='../static',
                         templates_path='../templates',
                         instance_path='../instance')
        from neomodel import config
        assert config.DATABASE_URL == app.config['NEOMODEL_DATABASE_URI']
        from neomodel import db
        from src.models.survey_model import Survey
        from src.models.conducted_survey_model import ConductedSurvey
        from src.models.question_model import Question
        from src.models.conducted_survey_question_model import ConductedSurveyQuestion
        assert Survey in db._NODE_CLASS_REGISTRY.values()
        assert Question in db._NODE_CLASS_REGISTRY.values()
        assert ConductedSurvey in db._NODE_CLASS_REGISTRY.values()
        assert ConductedSurveyQuestion in db._NODE_CLASS_REGISTRY.values()


class Test_Database_Creation_Deletion():

    def test_database_creation(self):
        from src import create_app
        app = create_app(mode='development',
                         static_path='../static',
                         templates_path='../templates',
                         instance_path='../instance')
        with app.app_context():
            from src.database.db import init_db
            init_db(app)
            from neomodel import db

            labels = [lab[0] for lab in db.cypher_query("CALL db.labels")[0]]

            assert "Survey" in labels
            assert "Question" in labels
            assert "ConductedSurvey" in labels
            assert "ConductedSurveyQuestion" in labels
    
    def test_database_deletion(self):
        from src import create_app
        app = create_app(mode='development',
                         static_path='../static',
                         templates_path='../templates',
                         instance_path='../instance')
        with app.app_context():
            from src.database.db import distroy_db
            distroy_db(app)
            from neomodel import db
            labels = [lab for lab in db.cypher_query("CALL db.labels")[0]]
            assert len(labels) == 0