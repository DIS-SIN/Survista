import numpy as np
import pandas as pd
import sqlite3
import os
from datetime import datetime 
import json
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import translate
import re
from nltk.tokenize import word_tokenize
import copy
import random
import shutil
class SurveyDataLoader:
    def __init__(self, path_to_raw_file,
                 db_connection,                 
                 path_to_index = None,
                 path_to_metadata = None,
                 path_to_comments_folder = None):
        #load raw file path and index db connection into object variabled
        self.path_to_raw_file = path_to_raw_file
        self.db = db_connection
        #check if raw file path exists and throw an error if not
        if os.path.isdir(self.path_to_raw_file) == False:
            raise FileNotFoundError('The path_to_raw_file {path} is not valid'.format(path= self.path_to_raw_file))
        # if path of metadata is not provided assume the default path and try loading it into a dataframe
        if path_to_metadata is None:
            self.path_to_metadata = self.path_to_raw_file + '/survey_metadata.csv'
        try:
            self.metadata = pd.read_csv(self.path_to_metadata, encoding = 'utf-8', index_col = 0)
        except:
            raise FileNotFoundError('The path_to_metadata {path} is not valid'.format(path = path_to_metadata))
        #look at the db to see if the survey data already exists 
        self.__check_index()
        #check if these paths arguments are valid
        if not self.already_processing:
            if os.path.isdir(self.path_to_raw_file) == False:
                raise FileNotFoundError('The path_to_raw_file {path} is not valid'.format(path= self.path_to_raw_file))
            if path_to_index is None:
                self.path_to_index = self.path_to_raw_file + '/question_index.csv'
                print(self.path_to_index)
            if path_to_comments_folder is None:
                self.path_to_comments_folder = self.path_to_processed_file + '/comments/'  
            try:
                self.index_df = pd.read_csv(self.path_to_index, encoding = 'utf-8', index_col = 0)
            except FileNotFoundError:
                raise FileNotFoundError("The path_to_index {path} is not valid".format(path = path_to_index))                       
            #set object variables so object methods have access
            self.path_to_index = path_to_index
            self.path_to_metadata = path_to_metadata
            #call private function which generates the survey datastructure
            self.__init_dict()
            self.__load_questions()
            self.__load_comments()
            #Initialise Comment_Sections Object which handles comment data
            self.__load_sentiment()
            self.__to_json()
            self.__completed() 
    def __init_dict(self):
        #This function is prodomanantly for readability of data structure
        results_dict = {}
        results_dict["survey_title"] = self.metadata.loc[0,'Title_Of_Survey']
        results_dict["survey_date"] = self.metadata.loc[0,'Date_Of_Survey']
        results_dict['survey_location'] = self.metadata.loc[0,'Location_Of_Event']
        results_dict['number_of_questions'] = self.index_df.shape[0]
        results_dict['date_generated'] = datetime.datetime.now().strftime('%d-%m-%y')
        results_dict['question_index'] = self.index_df
        results_dict['sentiment_score'] = 0.0
        results_dict['magnitude_score'] = 0.0
        results_dict['number_of_comment_sections'] = 0 
        results_dict['number_of_comments'] = 0
        results_dict['number_of_sentences'] = 0
        results_dict['number_of_words'] = 0
        results_dict['comments'] = {}
        results_dict['sentences'] ={}
        results_dict['questions'] = {}
        self.results_dict = results_dict
    def __load_questions(self):
        results_dict = self.results_dict
        for i in self.index_df.index:
            try:
                question_file = self.path_to_raw_file + '/q' + i + '.csv'
                results_dict['questions'][i] = {
                                'index': i,
                                'title': self.index_df.loc[i][0], 
                                'response_data': pd.read_csv(question_file, encoding = 'utf-8'),
                                'has_comments': False
                               }
            except FileNotFoundError:
                raise FileNotFoundError('Question file {q_file} could not be found, please modify your index or restore the file'.format(q_file = question_file)) 
    def __load_comments(self):
        for file in os.listdir(self.path_to_raw_file):
            #decode the file object to a string name
            filename = os.fsdecode(file)
            #check if file is a comments file
            if filename.endswith('comments.csv'):
                #get the question number
                question_number = filename.split('_')[0][1:]
                #get the question from the survey datastructure 
                question = self.results_dict['questions'].get(question_number)
                #check to see if question has been dropped 
                if not question is None:
                    question['has_comments'] = True
                    try:
                        file_path = os.path.join(self.path_to_raw_file, filename)
                        question['comments'] = pd.read_csv(os.path.join(file_path),
                                                          encoding = 'utf-8',
                                                          index_col = 0)
                        question['comments'].dropna(inplace = True)
                    except:
                        raise FileNotFoundError('failed to load {path}'.format(file_path))
    def __load_sentiment(self):
        if os.path.isdir(self.path_to_comments_folder) == False:
            os.mkdir(self.path_to_comments_folder)
        questions = self.get_all_questions() 
        #comments frames which will be concatenated to form global comment frame
        comment_frames = []
        sentence_frames = []
        #variables to calculate
        sentiment_total = 0
        magnitude_total = 0 
        number_of_sections = 0
        number_of_words = 0
        #loop over keys which is the index of questions
        for question in questions:
            current_section = questions[question]
            if current_section['has_comments'] == True:
                #load comment sections then append the comment and sentence frame to their respective frame lists
                section = CommentSectionLoader(current_section,question,self.path_to_comments_folder)
                comment_frames.append(section.get_comments_frame())
                sentence_frames.append(section.get_sentences_frame())
                #collect sentiment and magnitude scores
                sentiment_total += section.get_sentiment_score() * section.get_comment_count()
                magnitude_total += section.get_magnitude_score()
                number_of_words += section.get_number_of_words()
                number_of_sections += 1
        #concatenate comment and sentence frames and get the count which is the number of rows
        self.results_dict['comments'] = pd.concat(comment_frames, sort = False)
        comment_count = self.results_dict['comments'].shape[0]
        self.results_dict['number_of_comments'] = comment_count
        self.results_dict['sentences'] = pd.concat(sentence_frames, sort = False)
        sentence_count = self.results_dict['sentences'].shape[0]
        self.results_dict['number_of_sentences'] = sentence_count
        self.results_dict['number_of_sections'] = number_of_sections
        self.results_dict['number_of_words'] = number_of_words
        self.results_dict['number_of_comment_sections'] = number_of_sections
        #calculate overall sentiment score and then add it to the dictionary
        sentiment_score = sentiment_total/comment_count
        self.results_dict['sentiment_score'] = sentiment_score
        self.results_dict['magnitude_score'] = magnitude_total
    def __to_json(self):
        json_obj = self.results_dict
        json_obj['index_used'] = json_obj['index_used'].to_dict()
        json_obj['comments'] = json_obj['comments'].to_dict()
        json_obj['sentences'] = json_obj['sentences'].to_dict()
        for key in json_obj['questions']:
            json_obj['questions'][key]['response_data'] = json_obj['questions'][key]['response_data'].to_dict()
            if json_obj['questions'][key]['has_comments'] == True:
                json_obj['questions'][key]['comments'] = json_obj['questions'][key]['comments'].to_dict()
                json_obj['questions'][key]['sentences'] = json_obj['questions'][key]['sentences']
        with open(self.path_to_json,'w+') as f:
            f.write(json.dumps(json_obj, ensure_ascii= False))
            f.close()
    def __check_index(self):
        #load into function level variable for convenience
        db = self.db
        #execute the query to check if the data exists and fetch the row if it does
        res = db.execute(
            """SELECT *
               FROM index
               WHERE raw_data_path = {path}
            """.format(path = self.path_to_raw_file).replace("\n","")
        ).fetchone()
        #if the row doesn't exist then get the last id and increment to get the key
        if res is None:
            count = db.execute(
                """SELECT MAX(id) max_id FROM index"""
            ).fetchone()['max_id']
            self.key = count + 1
            #generate paths and insert into index table
            self.path_to_processed_file = './static/processed_data/' + self.key
            self.path_to_json = './static/json/' + self.key + '.json'
            db.execute("""
               INSERT INTO index(survey_name, raw_data_path, processed_data_path, json_path, status, processing_data)
                VALUES({s},{r},{p},{j},{st},{d})
            """.format(s= self.metadata.loc[0,'Title_Of_Survey']),
                       r= self.path_to_raw_file,
                       p= self.path_to_processed_file,
                       j= self.path_to_json,
                       st = "processing",
                       d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S').replace("\n", "")
            )
            #flush the pipeline
            db.commit()
            #log the processing of new survey data
            db.execute("""
            INSERT INTO logs(index_id, log_type, log_text, date_of_log)
             VALUES({id},{t},{l},{d})
            """.format(id = self.key,
                       t = "ns_processing",
                       l = "New survey data being processed",
                       d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            ).replace("\n",""))
            db.commit()
        #othwerwise if the row exists meaning that the survey data already exists 
        else:
            #we need to check the status to ensure that we are not processing the same data at the same time
            status = res['status']
            if status == 'processing':
                self.already_processing = True
                return
            else:
                #Update status of the survey data to processing
                self.already_processing = False
                db.execute(""""
                UPDATE index
                 SET status = 'processing'
                 WHERE id = {my_id}
                """.format(my_id = res['id']).replace("\n",""))
                db.execute("""
                INSERT INTO logs(index_id, log_text, date_of_log)
                 VALUES({id},{t},{l},{d})""".format(id = self.key,
                       t = "s_processing",
                       l = "processing survey",
                       d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            ).replace("\n",""))
                db.commit()
                self.key = res['id']
                self.path_to_processed_file = res['processed_data_path']
                self.path_to_json = res['json_path']
    def __completed(self):
        #when called will update the status and log it
        db = self.db
        db.execute("""
        UPDATE index
         SET status = 'completed'
         WHERE id = {my_id}
        """.format(my_id = self.key).replace("\n",""))
        db.execute("""
                INSERT INTO logs(index_id, log_text, date_of_log)
                 VALUES({id},{t},{l},{d})""".format(id = self.key,
                       t = "completion_notice",
                       l = "Survey processing completed",
                       d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            ).replace("\n",""))
        db.commit()
    #getters
    def get_all_questions(self):
        return self.results_dict['questions']
    def get_already_processing(self):
        return self.already_processing
class CommentSectionLoader:
    def __init__(self, sectionDict, 
                 section_key, 
                 path_to_comments):
        #section paths are made this is under the comments folder consisting of section_ + the sectionKey (question index)
        self.path_to_section = path_to_comments + "/section_" + section_key
        #check if section folder exists and if not create it to house the comment files
        if os.path.isdir(self.path_to_section) == False:
            os.mkdir(self.path_to_section)
        sentence_frames = []
        comment_frames = []
        number_of_words = 0
        sentiment_total = 0
        magnitude_total = 0
        for index in range(0,sectionDict['comments'].shape[0]):
            #create the comment_key by adding the sectionKey (question number) + - and the comment number
            comment_key = section_key + '-' + str(index)
            comment_text = sectionDict['comments'].loc[index][0]
            #construct comment object
            current_comment = CommentLoader(comment_key, section_key, 
                                            comment_text, self.path_to_section)
            #add data to comments frame
            comment_frames.append(current_comment.get_comment_frame())
            sentence_frames.append(current_comment.get_sentences_frame())
            sentiment_total += current_comment.get_sentiment_score()
            magnitude_total += current_comment.get_magnitude_score()
            number_of_words += current_comment.get_number_of_words()
        #calculating sentiment score and concatinating sentence frames
        self.comments = pd.concat(comment_frames, sort = False)
        self.sentences = pd.concat(sentence_frames, sort = False)   
        self.number_of_comments = self.comments.shape[0]
        self.number_of_sentences = self.sentences.shape[0]
        self.magnitude_score = magnitude_total
        self.sentiment_score = sentiment_total/self.number_of_comments
        self.number_of_words = number_of_words
        #adding data to sectionDict
        sectionDict['comments'] = self.comments
        sectionDict['sentences'] = self.sentences
        sectionDict['sentiment_score'] = self.sentiment_score
        sectionDict['magnitude_score'] = self.magnitude_score
        sectionDict['number_of_comments'] = self.number_of_comments
        sectionDict['number_of_sentences'] = self.number_of_sentences
        sectionDict['number_of_words'] = self.number_of_words       
    def get_comments_frame(self):
        return self.comments
    def get_sentences_frame(self):
        return self.sentences 
    def get_comment_count(self):
        return self.number_of_comments
    def get_number_of_words(self):
        return self.number_of_words
    def get_sentiment_score(self):
        return self.sentiment_score
    def get_magnitude_score(self):
        return self.magnitude_score 
class CommentLoader:
    def __init__(self, comment_key, section_key, comment, path_to_section):
        self.comment_key = comment_key
        self.section_key = section_key
        self.path_to_comment = path_to_section + "/comment_" + comment_key
        self.comment = comment
        self.number_of_words = 0
        self.sentences_frames = []
        if os.path.isdir(self.path_to_comment) == False:
            os.mkdir(self.path_to_comment)
            self.__init_sentiment()
        elif os.path.isfile(self.path_to_comment + '/comment_' + comment_key + '.csv') == False:
            self.__init_sentiment()
        else:
            comment_df = pd.read_csv(self.path_to_comment + '/comment_' + comment_key + '.csv',encoding = 'utf-8', index_col = 0)
            self.comment_frame = comment_df
            self.language = comment_df.loc[comment_key,'language']
            self.sentiment_score = comment_df.loc[comment_key,'sentiment_score']
            self.magnitude_score = comment_df.loc[comment_key,'magnitude_score']
            self.number_of_sentences =  comment_df.loc[comment_key,'number_of_sentences']
            self.number_of_words = comment_df.loc[comment_key, 'number_of_words']
            for index in range(0,self.number_of_sentences):
                sentence_key = comment_key + '-' + str(index)
                current_sentence = Sentence(sentence_key, comment_key, self.path_to_comment, self.language)
                self.sentences_frames.append(current_sentence.get_sentences_frame())
            self.sentences = pd.concat(self.sentences_frames, sort = False)         
    def __init_sentiment(self):
        #creating an instance of the google natural language client class 
        client = language.LanguageServiceClient()
        #creating a document object with the content being the type and the type being plain text
        document  = types.Document(content = self.comment,type = enums.Document.Type.PLAIN_TEXT)
        #send request to google api to analyze with our document and requesting encoding to be UTF8
        sentiment = client.analyze_sentiment(document = document,encoding_type = 'UTF8')
        #getting the language the sentiment score and the magnitude score
        self.language = sentiment.language
        self.sentiment_score = sentiment.document_sentiment.score
        self.magnitude_score = sentiment.document_sentiment.magnitude
        #loop over sentences generating a sentence key everytime that consists of the section_key - comment_key - sentence_number
        count = 0
        for sentence in sentiment.sentences:
            sentence_key = self.comment_key + '-' + str(count)
            current_sentence = Sentence(sentence_key, self.comment_key, self.path_to_comment, self.language, sentence)
            #add data to sentence frame
            self.sentences_frames.append(current_sentence.get_sentences_frame())
            self.number_of_words += current_sentence.get_number_of_words()
            count += 1
        #create and fill comment data frame for storage 
        self.sentences = pd.concat(self.sentences_frames, sort = False)
        self.number_of_sentences = self.sentences.shape[0]
        comment_df = pd.DataFrame(columns = ['comment_id',
                                            'language',
                                            'comment',
                                            'sentiment_score',
                                            'magnitude_score',
                                            'number_of_sentences',
                                            'number_of_words'])
        comment_df.set_index('comment_id', inplace= True)
        comment_df.loc[self.comment_key,'language'] = self.language
        comment_df.loc[self.comment_key,'comment'] = self.comment
        comment_df.loc[self.comment_key,'sentiment_score'] = self.sentiment_score
        comment_df.loc[self.comment_key,'magnitude_score'] = self.magnitude_score
        comment_df.loc[self.comment_key,'number_of_sentences'] = self.number_of_sentences
        comment_df.loc[self.comment_key,'number_of_words'] = self.number_of_words
        self.comment_frame = comment_df
        comment_df.to_csv(self.path_to_comment + '/comment_' + self.comment_key + '.csv',encoding = 'utf-8')
    def get_sentiment_score(self):
        return self.sentiment_score
    def get_magnitude_score(self):
        return self.magnitude_score
    def get_language(self):
        return self.language
    def get_number_of_words(self):
        return self.number_of_words
    def get_number_of_sentences(self):
        return self.number_of_sentences 
    def get_sentences_frame(self):
        return self.sentences
    def get_comment_frame(self):
        return self.comment_frame 
class Sentence:
    def __init__(self, sentence_key, comment_key, path_to_comment, comment_language = None, sentence = None):
        self.path_to_sentence = path_to_comment + "/sentence_" + sentence_key + ".csv"
        print(comment_key)
        if os.path.isfile(self.path_to_sentence) == False:
            if sentence is None:
                raise ValueError('sentence argument must not be none for new sentences')
            self.sentence = sentence.text.content
            self.sentiment_score = sentence.sentiment.score
            self.magnitude_score = sentence.sentiment.magnitude
            sentence_df = pd.DataFrame(columns = ['sentence_id',
                                                  'comment_id',
                                                  'language',
                                                  'sentence',
                                                  'sentiment_score',
                                                  'magnitude_score',
                                                  'number_of_words'])
            sentence_df.set_index('sentence_id', inplace= True)
            sentence_df.loc[sentence_key,'comment_id'] = comment_key
            sentence_df.loc[sentence_key,'sentence'] = self.sentence
            sentence_df.loc[sentence_key,'sentiment_score'] =  self.sentiment_score
            sentence_df.loc[sentence_key,'magnitude_score'] = self.magnitude_score
            client = translate.Client()
            self.language = client.detect_language(self.sentence)['language']
            sentence_df.loc[sentence_key, 'language'] = self.language
            self.__calculate_number_of_words()
            sentence_df.loc[sentence_key,'number_of_words'] = self.number_of_words
            self.sentence_frame = sentence_df
            sentence_df.to_csv(self.path_to_sentence, encoding = 'utf-8')
        else:
            sentence_df = pd.read_csv(self.path_to_sentence,
                                      encoding = 'utf-8',
                                      index_col = 0)
            self.sentence_frame = sentence_df
            self.language = sentence_df.loc[sentence_key,'language']
            self.sentence = sentence_df.loc[sentence_key,'sentence']
            self.sentiment_score = sentence_df.loc[sentence_key,'sentiment_score']
            self.magnitude_score = sentence_df.loc[sentence_key,'magnitude_score']
            self.number_of_words = sentence_df.loc[sentence_key,'number_of_words']
    def __calculate_number_of_words(self):
        #creating array of words for text
        text = self.sentence
        raw_textarr = word_tokenize(text)
        punctuation = [",", ".", "?", ";", "!", ":", ">" ,"<", "{", "}", "[", "]", "\\", "/"]
        no_punct = lambda arr, punct: [y[0] for y in zip(arr) if not y[0] in punct]
        text_arr = no_punct(raw_textarr, punctuation)
        self.number_of_words = len(text_arr)
    def get_sentiment_score(self):
        return self.sentiment_score
    def get_magnitude_score(self):
        return self.magnitude_score
    def get_text(self):
        return self.sentence
    def get_number_of_words(self):
        return self.number_of_words
    def get_language(self):
        return self.language
    def get_sentences_frame(self):
        return self.sentence_frame
  