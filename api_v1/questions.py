from flask_restful import Resource, reqparse
from basicauth import bauth
from .api_utils.surveyData import *
parser = reqparse.RequestParser()
parser.add_argument('questions', type=str, action = 'append', help='provide comma seperated values')
parser.add_argument('withComments', type=int, choices = (0,1), help = 'must provide a value of 0 or 1', default = 1)
parser.add_argument('sentimentScoreMin', type=float, help = 'provide a float value between -1 and 1')
parser.add_argument('sentimentScoreMax', type=float, help = 'provide a float value between -1 and 1')
parser.add_argument('magnitudeScoreMin', type=float, help = 'provide a float value above 0')
parser.add_argument('magnitudeScoreMax', type=float, help = 'provide a float value above 0')

class APIQuestions(Resource):
    @bauth.required
    def get(self,**kwargs):
        args = parser.parse_args(strict= True)
        try:
            data = SurveyData(surveyId = kwargs.get('surveyId'), 
            slugName = kwargs.get('slugName'), questions = args.get('questions'),
            withComments = args.get('withComments'), sentimentScoreMin = args.get('sentimentScoreMin'),
            sentimentScoreMax = args.get('sentimentScoreMax'), magnitudeScoreMin = args.get('magnitudeScoreMin'),
            magnitudeScoreMax = args.get('magnitudeScoreMax'))
        except SurveyNotFound as e:
            return {"error": repr(e)}, 400
        except SurveyNotAvailable as e:
            return {"error": repr(e)}, 202
        except SurveyProcessingError as e:
            return {"error": repr(e)}, 404
        try:
            questions = data.get_questions_obj()
            return questions.get_questions()
        except QuestionsNotFound as e:
            return {"error": repr(e)}, 400
        except SentimentOutOfBounds as e:
            return {"error": repr(e)}, 400
        except MagnitudeOutOfBounds as e:
            return {"error": repr(e)}, 400
        except SentimentMinIsGreaterThanMax as e:
            return {"error": repr(e)}, 400
        except MagnitudeMinIsGreaterThanMax as e:
            return {"error": repr(e)}, 400