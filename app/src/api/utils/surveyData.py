from flask import current_app
from db import get_db
import os 
import json
import pandas as pd
import numpy
import re 
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
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
        self.questionsDict['surveyInfo'] = {}
        self.questionsDict['surveyInfo']['numberOfComments'] = self.data['number_of_comments']
        if self.data['number_of_comments'] > 0:
            self.questionsDict['surveyInfo']['sentimentScore'] = self.data['sentiment_score']
            self.questionsDict['surveyInfo']['magnitudeScore'] = self.data['magnitude_score']
            self.questionsDict['surveyInfo']['numberOfSections'] = self.data['number_of_comment_sections']
            self.questionsDict['surveyInfo']['numberOfSentences'] = self.data['number_of_sentences']
            self.questionsDict['surveyInfo']['numberOfWords'] = self.data['number_of_words']
            self.questionsDict['surveyInfo']['meanNumberCommentsPerSection'] = self.data['number_of_comments'] / self.data['number_of_comment_sections']
            self.questionsDict['surveyInfo']['meanNumberSentencesPerSection'] = self.data['number_of_sentences'] / self.data['number_of_comment_sections']
            self.questionsDict['surveyInfo']['meanNumberWordsPerSection'] = self.data['number_of_words'] / self.data['number_of_comment_sections']
            temp_data = ' '.join(pd.DataFrame.from_dict(self.data['comments'])['comment']).split()
            self.questionsDict['surveyInfo']['overallMostCommonWords'] = pd.Series(temp_data).value_counts()[:20].to_dict()
            self.questionsDict['surveyInfo']['overallLeastCommonWords'] = pd.Series(temp_data).value_counts()[-20:].to_dict()
        sentimentScore = 0
        magnitudeScore = 0
        numberOfComments = 0
        numberOfSentences = 0
        numberOfWords = 0
        numberOfSections = 0
        self.corpus_english = []
        self.corpus_french = []
        for question in self.questions:
            self.questionsDict[question] = Question(self.questions[question], params = self.params).get_question()
            comments = self.questionsDict[question].get('selectedComments')
            if comments is not None and comments['comments']:
                numberOfComments += comments['numberOfComments']
                numberOfWords += comments['numberOfWords']
                numberOfSentences += comments['numberOfSentences']
                sentimentScore += comments['sentimentScore'] * comments['numberOfComments']
                magnitudeScore += comments['magnitudeScore']
                for comment in comments['comments']:
                    if comments['comments'][comment].get('commentId') is not None:
                        if comments['comments'][comment]['language'] == 'en':
                            self.corpus_english.append(comments['comments'][comment]['comment'])
                        elif comments['comments'][comment]['language'] == 'fr':
                            self.corpus_french.append(comments['comments'][comment]['comment'])
                numberOfSections += 1
        if numberOfComments > 0:
            self.questionsDict['numberOfComments'] = numberOfComments
            self.questionsDict['numberOfSentences'] = numberOfSentences
            self.questionsDict['numberOfWords'] = numberOfWords
            self.questionsDict['sentimentScore'] = sentimentScore / numberOfComments
            self.questionsDict['magnitudeScore'] = magnitudeScore
            self.questionsDict['meanNumberOfSentencesPerComment'] = numberOfSentences / numberOfComments
            self.questionsDict['meanNumberOfWordsPerComment'] = numberOfWords / numberOfComments
            self.questionsDict['meanNumberOfCommentsPerSection'] = numberOfComments / numberOfSections
            self.questionsDict['meanNumberOfSentencesPerSection'] = numberOfSentences / numberOfSections
            self.questionsDict['meanNumberOfWordsPerSection'] = numberOfWords / numberOfSections
            self.__calculate_count_vector()
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
    def __calculate_count_vector(self):
        stop_words_english = set(stopwords.words("english"))
        stop_words_french = set(stopwords.words("french"))
        corpus_english = []
        corpus_french = []
        lem = WordNetLemmatizer()
        for eng in self.corpus_english:
            text = re.sub('[^a-zA-Z]',' ',eng)
            #remove tags
            text = re.sub("&lt;/?.*?&gt;"," &lt;&gt; ", text)
            #remove special chars and digits
            text = re.sub("(\\d|\\W)+"," ", text)
            text = text.split()
            text = [lem.lemmatize(word) for word in text if not word in stop_words_english]
            text = " ".join(text)
            corpus_english.append(text)
        for fr in self.corpus_french:
            text = re.sub('[^a-zA-Z]',' ',fr)
            #remove tags
            text = re.sub("&lt;/?.*?&gt;"," &lt;&gt; ", text)
            #remove special chars and digits
            text = re.sub("(\\d|\\W)+"," ", text)
            text = text.split()
            text = [lem.lemmatize(word) for word in text if not word in stop_words_french]
            text = " ".join(text)
            corpus_french.append(text)
        if corpus_english != []:
            cv_english = CountVectorizer(stop_words= stop_words_english,
            max_features=10000, ngram_range=(1,3))
            vec_english = cv_english.fit(corpus_english)
            bag_of_words_english = vec_english.transform(corpus_english)
            sum_words_english = bag_of_words_english.sum(axis = 0)
            words_freq_english = [(word, sum_words_english[0,idx]) for word, idx in vec_english.vocabulary_.items()]
            words_freq_english = sorted(words_freq_english, key = lambda x: x[1], reverse = True)
            if len(words_freq_english) > 20:
                top_words_english = words_freq_english[:10]
            else:
                top_words_english = words_freq_english[:len(words_freq_english)// 2]
            top_words_english_df = pd.DataFrame(top_words_english, columns=['Word', "Frequency"])
            self.questionsDict['surveyInfo']['topUniGramsEnglish'] = top_words_english_df.to_dict()
        if corpus_french != []: 
            cv_french = CountVectorizer(stop_words= stop_words_french,
            max_features=10000, ngram_range=(1,3))
            vec_french = cv_french.fit(corpus_french)
            bag_of_words_french = vec_french.transform(corpus_french)
            sum_words_french = bag_of_words_french.sum(axis = 0)
            words_freq_french = [(word, sum_words_french[0,idx]) for word, idx in vec_french.vocabulary_.items()]
            words_freq_french = sorted(words_freq_french, key = lambda x: x[1], reverse = True)
            if len(words_freq_french) > 20:
                top_words_french = words_freq_french[:20]
            else:
                top_words_french = words_freq_french[:len(words_freq_french)//2]
            top_words_french_df = pd.DataFrame(top_words_french, columns=['Word', "Frequency"])
            self.questionsDict['surveyInfo']['topUniGramsFrench'] = top_words_french_df.to_dict()
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
        questionDict['questionNumber'] = data['index']
        questionDict['title'] = data['title']
        questionDict['responseData'] = data['response_data']
        questionDict['hasComments'] = data['has_comments']
        if self.withComments:
            if data['has_comments'] == True:
                self.comments = Comments(data['comments'], data['sentences'], params = self.params)
                questionDict['sentimentScore'] = float(data['sentiment_score'])
                questionDict['magnitudeScore'] = float(data['magnitude_score'])
                questionDict['totalNumberOfComments'] = int(data['number_of_comments'])
                questionDict['totalNumberOfSentences'] = int(data['number_of_sentences'])
                questionDict['totalNumberOfWords'] = int(data['number_of_words'])
                questionDict['overallMeanNumberOfSentencesPerComment'] = questionDict['totalNumberOfSentences'] / questionDict['totalNumberOfComments']
                questionDict['overallMeanNumberOfWordsPerComment'] = questionDict['totalNumberOfWords'] / questionDict['totalNumberOfComments']
                questionDict['overallMeanNumberOfWordsPerSentence'] = questionDict['totalNumberOfWords'] / questionDict['totalNumberOfComments']
                questionDict['overallMostCommonWords'] = pd.Series(' '.join(self.comments.get_comments_df()['comment']).split()).value_counts()[:20].to_dict()
                questionDict['overallLeastCommonWords'] = pd.Series(' '.join(self.comments.get_comments_df()['comment']).split()).value_counts()[-20:].to_dict()
                questionDict['selectedComments'] = self.comments.get_comments()
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
        self.response['comments'] = {}
        numberOfSentences = 0
        numberOfComments = 0
        numberOfWords = 0
        sentimentScore = 0
        magnitudeScore = 0
        for row in self.commentsdf.index:
           current_comment =  Comment(self.commentsdf.loc[row], 
           self.sentencesdf.loc[self.sentencesdf['comment_id'] == row],params).get_comment()
           if current_comment != False:
               numberOfComments += 1
               numberOfSentences += current_comment['numberOfSentences']
               numberOfWords += current_comment['numberOfWords']
               sentimentScore += current_comment['sentimentScore']
               magnitudeScore += current_comment['magnitudeScore']
               self.response['comments'][row] = current_comment
        if numberOfComments != 0:
            sentimentScore = sentimentScore / numberOfComments
            self.response['numberOfComments'] = numberOfComments
            self.response['numberOfSentences'] = numberOfSentences
            self.response['numberOfWords'] = numberOfWords
            self.response['sentimentScore'] = sentimentScore
            self.response['magnitudeScore'] = magnitudeScore
            self.response['meanNumberOfSentencesPerComment'] = numberOfSentences / numberOfComments
            self.response['meanNumberOfWordsPerComment'] = numberOfWords / numberOfComments 
            self.response['meanNumberOfWordsPerSentence'] =  numberOfWords / numberOfSentences
            self.__calculate_count_vector()
    def __check_params(self):
        if self.sentimentScoreMin is not None and self.sentimentScoreMax is not None:
            if self.sentimentScoreMin > 1 or self.sentimentScoreMin < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            elif self.sentimentScoreMax > 1 or self.sentimentScoreMax < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
            elif self.sentimentScoreMin > self.sentimentScoreMax:
                raise SentimentMinIsGreaterThanMax('sentimentScoreMin must be less than or equal to sentimentScoreMax')
        elif self.sentimentScoreMin is not None and self.sentimentScoreMax is None:
            if self.sentimentScoreMin > 1 or self.sentimentScoreMin < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
        elif self.sentimentScoreMax is not None and self.sentimentScoreMin is None:
            if self.sentimentScoreMax > 1 or self.sentimentScoreMax < -1:
                raise SentimentOutOfBounds('Sentiment scores must be between -1 and 1 inclusive')
        if self.magnitudeScoreMin is not None and self.magnitudeScoreMax is not None:
            if self.magnitudeScoreMin < 0 :
                raise MagnitudeOutOfBounds('Magnitude scores must greater or equal to 0 ')
            elif self.magnitudeScoreMax < 0:
                raise MagnitudeOutOfBounds('Magnitude scores must greater or equal to 0 ')
            elif self.magnitudeScoreMin > self.magnitudeScoreMax:
                raise MagnitudeMinIsGreaterThanMax('magnitudeScoreMin must be less than or equal to magnitudeScoreMax')
        elif self.magnitudeScoreMin is not None and self.magnitudeScoreMax is None:
            if self.magnitudeScoreMin < 0 :
                raise MagnitudeOutOfBounds('Magnitude scores must greater or equal to 0 ') 
        elif self.magnitudeScoreMax is not None and self.magnitudeScoreMin is None:
            if self.magnitudeScoreMax < 0:
                raise MagnitudeOutOfBounds('Magnitude scores must greater or equal to 0 ')
    def __calculate_count_vector(self):
        stop_words_english = set(stopwords.words("english"))
        stop_words_french = set(stopwords.words("french"))
        corpus_english = []
        corpus_french = []
        for comment in self.response['comments']:
            language = self.response['comments'][comment]['language']
            #remove punctuation
            text = re.sub('[^a-zA-Z]',' ',self.response['comments'][comment]['comment'])
            #remove tags
            text = re.sub("&lt;/?.*?&gt;"," &lt;&gt; ", text)
            #remove special chars and digits
            text = re.sub("(\\d|\\W)+"," ", text)
            text = text.split()
            lem = WordNetLemmatizer()
            if language == 'fr':
                text = [lem.lemmatize(word) for word in text if not word in stop_words_french]
                text = " ".join(text)
                corpus_french.append(text)
            elif language == 'en':
                text = [lem.lemmatize(word) for word in text if not word in stop_words_english]
                text = " ".join(text)
                corpus_english.append(text)
        if corpus_english != []:
            cv_english = CountVectorizer(stop_words= stop_words_english,
            max_features=10000, ngram_range=(1,3))
            vec_english = cv_english.fit(corpus_english)
            bag_of_words_english = vec_english.transform(corpus_english)
            sum_words_english = bag_of_words_english.sum(axis = 0)
            words_freq_english = [(word, sum_words_english[0,idx]) for word, idx in vec_english.vocabulary_.items()]
            words_freq_english = sorted(words_freq_english, key = lambda x: x[1], reverse = True)
            if len(words_freq_english) > 20:
                top_words_english = words_freq_english[:20]
            else:
                top_words_english = words_freq_english[:len(words_freq_english)// 2]
            top_words_english_df = pd.DataFrame(top_words_english, columns=['Word', "Frequency"])
            self.response['topUniGramsEnglish'] = top_words_english_df.to_dict()
        if corpus_french != []: 
            cv_french = CountVectorizer(stop_words= stop_words_french,
            max_features=10000, ngram_range=(1,3))
            vec_french = cv_french.fit(corpus_french)
            bag_of_words_french = vec_french.transform(corpus_french)
            sum_words_french = bag_of_words_french.sum(axis = 0)
            words_freq_french = [(word, sum_words_french[0,idx]) for word, idx in vec_french.vocabulary_.items()]
            words_freq_french = sorted(words_freq_french, key = lambda x: x[1], reverse = True)
            if len(words_freq_french) > 20:
                top_words_french = words_freq_french[:20]
            else:
                top_words_french = words_freq_french[:len(words_freq_french)//2]
            top_words_french_df = pd.DataFrame(top_words_french, columns=['Word', "Frequency"])
            self.response['topUniGramsFrench'] = top_words_french_df.to_dict()
    def get_comments(self):
        return self.response
    def get_comments_df(self):
        return self.commentsdf
    def get_sentence_df(self):
        return self.sentencesdf
class Comment:
    def __init__(self,comment_data,sentences_data,params,**kwargs):
        self.params = params
        self.sentimentScoreMin = self.params.get('sentimentScoreMin')
        self.sentimentScoreMax = self.params.get('sentimentScoreMax')
        self.magnitudeScoreMin = self.params.get('magnitudeScoreMin')
        self.magnitudeScoreMax = self.params.get('magnitudeScoreMax')
        self.comment_data = comment_data
        self.sentences_data = sentences_data
        if self.__check_comment():
            self.__parse_comment()
            for row in self.sentences_data.index:
                current_sentence = Sentence(self.sentences_data.loc[row], params)
                self.response['sentences'][row] = current_sentence.get_sentence()
        else:
            self.response = False
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
        self.response = {}
        self.response['commentId'] = self.comment_data.name
        temp_dict = dict(self.comment_data)
        self.response['comment'] = temp_dict['comment']
        self.response['sentimentScore'] = float(temp_dict['sentiment_score'])
        self.response['magnitudeScore'] = float(temp_dict['magnitude_score'])
        self.response['numberOfSentences'] = int(temp_dict['number_of_sentences'])
        self.response['numberOfWords'] = int(temp_dict['number_of_words'])
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
        self.response = {}
        self.response['sentenceId'] = self.data.name
        temp_dict = dict(self.data)
        self.response['sentence'] = temp_dict['sentence']
        self.response['sentimentScore'] = float(temp_dict['sentiment_score'])
        self.response['magnitudeScore'] = float(temp_dict['magnitude_score'])
        self.response['language'] = temp_dict['language']
        self.response['number_of_words'] = int(temp_dict['number_of_words'])
    def get_sentence(self):
        return self.response



    








