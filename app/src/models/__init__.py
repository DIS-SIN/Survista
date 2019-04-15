
def init_base(app):
    from .base_model import base
    base.init_app(app)
    from .conducted_survey_model import (
        ConductedSurveyModel,
        ConductedSurveyQuestionModel
    )
    from .question_model import QuestionModel, QuestionTypeModel
    from .survey_model import SurveyModel, SurveyQuestionsModel
