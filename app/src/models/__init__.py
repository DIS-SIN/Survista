
def init_base(app):
    from .base_model import base
    base.init_app(app)
    from .question_model import QuestionModel, QuestionTypeModel
    from .survey_model import SurveyModel, SurveyQuestionsModel
