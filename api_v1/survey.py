from flask_restful import Resource
from flask import g, current_app
from db import get_db
from basicauth import bauth
import json
import os
class Survey(Resource):
    @bauth.required
    def get(self, **kwargs):
        get_db()
        slugName = kwargs.get("slugName")
        surveyId = kwargs.get("surveyId")
        if surveyId is not None:
            query = "SELECT it.id, it.survey_name, it.processing_date, it.json_path, st.status_name \
                 FROM index_table AS it \
                 INNER JOIN statuses AS st ON it.status_id = st.id  WHERE it.id = {id}".format(
                     id = surveyId
                 )
        elif slugName is not None:
            raw_path = '../static/raw_data/' + slugName
            query = "SELECT it.id, it.survey_name, it.processing_date, it.json_path, st.status_name \
                 FROM index_table AS it \
                 INNER JOIN statuses AS st ON it.status_id = st.id  WHERE it.raw_data_path = '{slug}'".format(
                     slug = raw_path
                 )
        survey = {}
        res = g.index_db.execute(query).fetchone()
        if res is None:
            return {"error": "surveyNotFound"},404
        else:
            
            survey["surveyName"] = res['survey_name']
            staticpath = current_app.static_folder
            jsonPath = str(res['json_path']).rsplit(os.path.sep, 1)[1]
            jsonPath = os.path.join(staticpath,'json',jsonPath)
            with open(jsonPath,encoding='utf-8') as f:
                info = json.load(f)
                f.close()
            survey["surveyDate"] = info['survey_date']
            if info.get('survey_location') is not None:
                survey["surveyLocation"] = info['survey_location']
            if info.get('date_last_scraped') is not None:
                survey["dateLastScraped"] = info['date_last_scraped']
            if info.get('total_number_of_questions') is not None:
                survey["totalNumberOfQuestions"] = info['total_number_of_questions']
            survey['processedNumberOfQuestions'] = info['processed_number_of_questions']
            survey['dateGenerated'] = res['processing_date']
            survey['questionIndex'] = info['question_index']
            survey['sentimentScore'] = info['sentiment_score']
            survey['magnitudeScore'] = info['magnitude_score']
            survey['numberOfCommentSections'] = info['number_of_comment_sections']
            survey['numberOfComments'] = info['number_of_comments']
            survey['numberOfSentences'] = info['number_of_sentences']
            survey['numberOfWords'] = info['number_of_words']
            return survey
        
            
                


