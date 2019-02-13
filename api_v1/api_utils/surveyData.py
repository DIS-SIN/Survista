from flask import current_app
from db import get_db
import os 
import json
# this utility requires an application context
# this util class is specially designed for the rest api so that code executes only when it needs to
class SurveyNotFound(ValueError):
    pass
class SurveyProcessingError(Exception):
    pass
class SurveyNotAvailable(Exception):
    pass
class SurveyData:
    def __init__(self, **kwargs):
        #check arguments provided
        self.user_db, self.index_db = get_db()
        if kwargs.get('slugName') is None and kwargs.get('surveyId') is None:
            raise SurveyNotFound()
        elif kwargs.get('surveyId') is not None and kwargs.get('slugName') is None:
            self.surveyId = kwargs.get('surveyId')
            self.slugName = None
            query = "SELECT it.id, it.survey_name, it.processing_date, it.json_path, st.status_name \
                     FROM index_table AS it \
                     INNER JOIN statuses AS st ON it.status_id = st.id  WHERE it.id = {id}".format(
                     id = self.surveyId
                 )
        elif kwargs.get('slugName') is not None and kwargs.get('surveyId') is None:
            self.surveyId = None
            self.slugName = kwargs.get('slugName')
            raw_path = '../static/raw_data/' + self.slugName
            query = "SELECT it.id, it.survey_name, it.processing_date, it.json_path, st.status_name \
                     FROM index_table AS it \
                     INNER JOIN statuses AS st ON it.status_id = st.id  WHERE it.raw_data_path = '{slug}'".format(
                     slug = raw_path
                 )
        else:
            raise SurveyNotFound('Cannot provide both slugName and surveyId')
        self.survey = self.index_db.execute(query).fetchone()
    def get_survey_info(self):
        if self.survey is None:
            raise SurveyNotFound('Survey does not exist')
        elif self.survey['status_name'] == 'processing':
            raise SurveyNotAvailable('Survey is processing and should be available shortly if successful')
        elif self.survey['status_name'] == 'erred':
            raise SurveyProcessingError('The survey has encountered an error while processing and will not be available')
        survey = {}
        survey["surveyName"] = self.survey['survey_name']
        staticpath = current_app.static_folder
        jsonPath = str(self.survey['json_path']).rsplit(os.path.sep, 1)[1]
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
        survey['dateGenerated'] = self.survey['processing_date']
        survey['questionIndex'] = info['question_index']
        survey['sentimentScore'] = info['sentiment_score']
        survey['magnitudeScore'] = info['magnitude_score']
        survey['numberOfCommentSections'] = info['number_of_comment_sections']
        survey['numberOfComments'] = info['number_of_comments']
        survey['numberOfSentences'] = info['number_of_sentences']
        survey['numberOfWords'] = info['number_of_words']
        return survey


