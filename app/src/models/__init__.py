
def init_base(app):
    from neomodel import config
    config.DATABASE_URL = app.config['NEOMODEL_DATABASE_URI']
    from .survey_model import Survey, SurveyVersion
    from .question_model import Question
    from .conducted_survey_model import ConductedSurvey
    from .conducted_survey_question_model import ConductedSurveyQuestion
    from .answers_model import Answer
