from flask_restful import Resource
from flask import g, current_app
from db import get_db
from basicauth import bauth
import json
import os
from .api_utils.surveyData import SurveyData, SurveyNotFound, SurveyNotAvailable, SurveyProcessingError
class Survey(Resource):
    @bauth.required
    def get(self, **kwargs):
        try:
            data = SurveyData(surveyId = kwargs.get('surveyId'), slugName = kwargs.get('slugName'))
            return data.get_survey_info()
        except SurveyNotFound as e:
            return {"error": repr(e)}, 400
        except SurveyNotAvailable as e:
            return {"error": repr(e)}, 202
        except SurveyProcessingError as e:
            return {"error": repr(e)}, 404

                


