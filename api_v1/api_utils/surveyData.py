from flask import current_app
from db import get_db
import os 
import json
import pandas as pd
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
        self.params = kwargs
    def __get_survey_file(self):
        if self.survey is None:
            raise SurveyNotFound('Survey does not exist')
        elif self.survey['status_name'] == 'processing':
            raise SurveyNotAvailable('Survey is processing and should be available shortly if successful')
        elif self.survey['status_name'] == 'erred':
            raise SurveyProcessingError('The survey has encountered an error while processing and will not be available')
        staticpath = current_app.static_folder
        jsonPath = str(self.survey['json_path']).rsplit(os.path.sep, 1)[1]
        jsonPath = os.path.join(staticpath,'json',jsonPath)
        with open(jsonPath,encoding='utf-8') as f:
            info = json.load(f)
            f.close()
        self.data = info
    def get_survey_info(self):
        self.__get_survey_file()
        survey = {}
        survey["surveyName"] = self.survey['survey_name']
        survey["surveyDate"] = self.data['survey_date']
        if self.data.get('survey_location') is not None:
            survey["surveyLocation"] = self.data['survey_location']
        if self.data.get('date_last_scraped') is not None:
            survey["dateLastScraped"] = self.data['date_last_scraped']
        if self.data.get('total_number_of_questions') is not None:
            survey["totalNumberOfQuestions"] = self.data['total_number_of_questions']
        survey['processedNumberOfQuestions'] = self.data['processed_number_of_questions']
        survey['dateGenerated'] = self.survey['processing_date']
        survey['questionIndex'] = self.data['question_index']
        survey['sentimentScore'] = self.data['sentiment_score']
        survey['magnitudeScore'] = self.data['magnitude_score']
        survey['numberOfCommentSections'] = self.data['number_of_comment_sections']
        survey['numberOfComments'] = self.data['number_of_comments']
        survey['numberOfSentences'] = self.data['number_of_sentences']
        survey['numberOfWords'] = self.data['number_of_words']
        return survey
    def get_questions_obj(self):
        #get survey file and check the kwargs for get arguments
        self.__get_survey_file()
        self.questions = Questions(data = self.data, params = self.params)
        return self.questions
class QuestionsNotFound(ValueError):
    """This error is used when one or more questions could not be found"""
    pass
class SentimentOutOfBounds(ValueError):
    """This error is used when the sentiment score specified is less than -1 or greater than 1"""
    pass
class MagnitudeOutOfBounds(ValueError):
    """This error is used when the magnitude score specified is ledd than 0"""
    pass
class SentimentMinIsGreaterThanMax(ValueError):
    """This error is used when the sentimentScoreMin > sentimentScoreMax"""
    pass
class MagnitudeMinIsGreaterThanMax(ValueError):
    """This error is used when the magnitudeScoreMin < magnitudeScoreMax"""
    pass
class Questions:
    def __init__(self,data,params,**kwargs):
        self.data = data
        self.params = params
        self.questionList = self.params.get('questions')
        self.questions = self.data['questions']
        questionKeys = list(self.questions.keys())
        if self.questionList is not None:
            self.__check_question_list()
            for question in questionKeys:
                if question not in self.questionList:
                    self.questions.pop(question)
        self.questionsDict = {}
        for question in self.questions:
            self.questionsDict[question] = Question(self.questions[question], params = self.params).get_question()
    def __get_data_question_list(self):
        """create a set of questions list from the survey data"""
        dataQuestionsList = []
        for question in self.questions:
            dataQuestionsList.append(question)
        self.dataQuestionList = set(dataQuestionsList)
    def __check_question_list(self):
        self.__get_data_question_list()
        questionsNotFound = []
        for question in self.questionList:
            if question not in self.dataQuestionList:
                questionsNotFound.append(question)
        if len(questionsNotFound) > 0:
            raise QuestionsNotFound('The following questions could not be found ' + str(questionsNotFound).strip('[]'))
        else:
            self.questionList = set(self.questionList)
    def get_questions(self):
        return self.questionsDict
class Question:
    def __init__(self, data, params, **kwargs):
        self.params = params
        self.withComments = self.params.get('withComments')
        if self.withComments is None:
            self.withComments = True
        else:
            self.withComments = bool(self.withComments)
        questionDict = {}
        if self.withComments:
            if data['has_comments'] == True:
                self.comments = Comments(data['comments'], data['sentences'], params = self.params)
        questionDict['questionNumber'] = data['index']
        questionDict['title'] = data['title']
        questionDict['responseData'] = data['response_data']
        questionDict['hasComments'] = data['has_comments']
        self.response = questionDict
    def get_question(self):
        return self.response
class Comments:
    def __init__(self,comment_data,sentence_data,params,**kwargs):
        self.params = params
        self.sentimentScoreMin = self.params.get('sentimentScoreMin')
        self.sentimentScoreMax = self.params.get('sentimentScoreMax')
        self.magnitudeScoreMin = self.params.get('magnitudeScoreMin')
        self.magnitudeScoreMax = self.params.get('magnitudeScoreMax')
        self.__check_params()
        self.commentsdf = pd.DataFrame.from_dict(comment_data)
        self.sentencesdf = pd.DataFrame.from_dict(sentence_data)
        self.response = {}
        for row in self.commentsdf.index:
           current_comment =  Comment(self.commentsdf.loc[row], 
           self.sentencesdf.loc[self.sentencesdf['comment_id'] == row],params)
           self.response[row] = current_comment.get_comment()

    def __check_params(self):
        if self.sentimentScoreMin is not None and self.sentimentScoreMax is not None:
            if self.sentimentScoreMin > 1 or self.sentimentScoreMin < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            elif self.sentimentScoreMax > 1 or self.sentimentScoreMax < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            elif self.sentimentScoreMin > self.sentimentScoreMax:
                raise SentimentMinIsGreaterThanMax('sentimentScoreMin must be less than or equal to sentimentScoreMax')
            self.withComments = True
        elif self.sentimentScoreMin is not None and self.sentimentScoreMax is None:
            if self.sentimentScoreMin > 1 or self.sentimentScoreMin < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            self.withComments = True 
        elif self.sentimentScoreMax is not None and self.sentimentScoreMin is None:
            if self.sentimentScoreMax > 1 or self.sentimentScoreMax < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            self.withComments = True 
        if self.magnitudeScoreMin is not None and self.magnitudeScoreMax is not None:
            if self.magnitudeScoreMin > 1 or self.magnitudeScoreMin < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            elif self.magnitudeScoreMax > 1 or self.magnitudeScoreMax < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            elif self.magnitudeScoreMin > self.magnitudeScoreMax:
                raise SentimentMinIsGreaterThanMax('magnitudeScoreMin must be less than or equal to magnitudeScoreMax')
            self.withComments = True
        elif self.magnitudeScoreMin is not None and self.magnitudeScoreMax is None:
            if self.magnitudeScoreMin > 1 or self.magnitudeScoreMin < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            self.withComments = True 
        elif self.magnitudeScoreMax is not None and self.magnitudeScoreMin is None:
            if self.magnitudeScoreMax > 1 or self.magnitudeScoreMax < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
    def get_comments(self):
        return self.response
class Comment:
    def __init__(self,comment_data,sentences_data,params,**kwargs):
        self.params = params
        self.sentimentScoreMin = self.params.get('sentimentScoreMin')
        self.sentimentScoreMax = self.params.get('sentimentScoreMax')
        self.magnitudeScoreMin = self.params.get('magnitudeScoreMin')
        self.magnitudeScoreMax = self.params.get('magnitudeScoreMax')
        self.comment_data = comment_data
        self.sentences_data = sentences_data
        if self.__check_comments():
            self.__parse_comment()
        for row in self.sentences_data.index:
            current_sentence = Sentence(self.sentences_data.loc[row], params)
            self.response['sentences']['row'] = current_sentence.get_sentence()
    def __check_comment(self):
        if self.sentimentScoreMin is not None:
            if self.comment_data['sentiment_score'] < self.sentimentScoreMin:
                return False
        if self.sentimentScoreMax is not None:
            if self.comment_data['sentiment_score'] > self.sentimentScoreMax:
                return False
        if self.magnitudeScoreMin is not None:
            if self.comment_data['magnitude_score'] < self.magnitudeScoreMin:
                return False
        if self.magnitudeScoreMax is not None:
            if self.comment_data['magnitude_score'] > self.magnitudeScoreMax:
                return False
        return True
    def __parse_comment(self):
        temp_dict = dict(self.comment_data)
        self.response = {}
        self.response['commentId'] = temp_dict['Name'] 
        self.response['sentimentScore'] = temp_dict['sentiment_score']
        self.response['magnitudeScore'] = temp_dict['magnitude_score']
        self.response['numberOfSentences'] = temp_dict['number_of_sentences']
        self.response['numberOfWords'] = temp_dict['number_of_words']
        self.response['language'] = temp_dict['language']
        self.response['sentences'] = {}
    def get_comment(self):
        return self.response
class Sentence:
    def __init__(self,data,params,**kwargs):
        self.params = params
        self.data = data
        self.__parse_data()
    def __parse_data(self):
        temp_dict = dict(self.data)
        self.response = {}
        self.response['sentenceId'] = temp_dict['Name']
        self.response['sentimentScore'] = temp_dict['sentiment_score']
        self.response['magnitudeScore'] = temp_dict['magnitudeScore']
        self.response['language'] = temp_dict['language']
        self.response['number_of_words'] = temp_dict['numberOfWords']
    def get_sentence(self):
        return self.response



    









