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
from distutils.dir_util import copy_tree
class MetadataFileNotExist(FileNotFoundError):
    pass
class RawdataFolderNotExist(FileNotFoundError):
    pass
class QuestionIndexFileNotExist(FileNotFoundError):
    pass
class MetadataFormatNotValid(ValueError):
    pass
class QuestionIndexFormatNotValid(ValueError):
    pass 
class SurveyDataLoader:
    def __init__(self, path_to_raw_folder,
                 path_to_processed_folder,
                 path_to_json_folder,
                 db_connection,
                 survey_preprocessed = False,
                 force_process = False):
        #load raw file path and index db connection into object variabled
        self.path_to_raw_folder = path_to_raw_folder
        self.path_to_processed_folder = path_to_processed_folder
        self.path_to_json_folder = path_to_json_folder
        self.db = db_connection
        #check if survey is processing and if the survey is processing return
        res = self.__get_survey_entry()
        if not res[0]:
            if self.__get_status(res[1]['status_id']) != "completed" and not force_process:
                return
        #check if raw file path file exists and is valid
        if os.path.isdir(self.path_to_raw_folder) == False and not survey_preprocessed:
            error = RawdataFolderNotExist('The path_to_raw_folder {path} is not valid'.format(path= self.path_to_raw_folder))
            self.__error_logger(error)
        self.path_to_metadata = os.path.join(self.path_to_raw_folder , 'survey_metadata.csv')
        #attempt loading the survey metadata and then check it has a valid format 
        try:
            self.metadata = pd.read_csv(self.path_to_metadata, encoding = 'utf-8', index_col = 0)
        except FileNotFoundError as error:
            error = MetadataFileNotExist("Metadata not found:" + str(error))
            self.__error_logger(error)
        #check format of metadata is valid
        self.__check_metadata_format()
        #if new survey then generate new processed data and json paths and then update database otherwise mark survey for processing
        if res[0]:
            self.__update_survey_entry_details()
        else:
            self.__mark_survey_status()
        #check if these paths arguments are valid
        if survey_preprocessed:
            self.path_to_index = os.path.join(self.path_to_processed_folder, 'question_index.csv')
        else:
            self.path_to_index = os.path.join(self.path_to_raw_folder, 'question_index.csv')
        if not os.path.isfile(self.path_to_index):
            if survey_preprocessed:
                self.path_to_index_raw = os.path.join(self.path_to_raw_folder, 'question_index.csv')
                if not os.path.isfile(self.path_to_index_raw):
                    error = QuestionIndexFileNotExist('Both raw folder and processed folder do not contain question_index.csv')
                    self.__error_logger(error)
                else:
                    shutil.copy2(self.path_to_index_raw ,self.path_to_index)
            else:
                error =  QuestionIndexFileNotExist('Folder does not contain question_index.csv')
                self.__error_logger(error)
        #check if question index file is of right format
        try:
            self.index_df = pd.read_csv(self.path_to_index, encoding = 'utf-8', index_col = 0)
        except Exception as error:
            self.__error_logger(error)
        self.__check_index_format() 
        if os.path.isdir(self.path_to_processed_folder) and not survey_preprocessed:
            shutil.rmtree(self.path_to_processed_folder)
            copy_tree(self.path_to_raw_folder, self.path_to_processed_folder)
        elif not survey_preprocessed:
            copy_tree(self.path_to_raw_folder, self.path_to_processed_folder)  
        self.path_to_comments_folder = os.path.join(self.path_to_processed_folder, 'comments')                     
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
        results_dict["survey_title"] = self.metadata_columns['Title_Of_Survey']
        results_dict["survey_date"] = self.metadata_columns['Date_Of_Survey']
        if self.metadata_columns['Location_Of_Event'] != False:
            results_dict['survey_location'] = self.metadata_columns['Location_Of_Event']
        if self.metadata_columns['Date_Last_Scraped'] != False:
            results_dict['date_last_scraped'] = self.metadata_columns['Date_Last_Scraped']
        if self.metadata_columns['Number_Of_Questions'] != False:
            results_dict['total_number_of_questions'] = int(self.metadata_columns['Number_Of_Questions'])
        results_dict['processed_number_of_questions'] = self.index_df.shape[0]
        results_dict['date_generated'] = datetime.now().strftime('%d-%m-%y')
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
                #TO ADD: Support for text questions
                question_file = os.path.join(self.path_to_raw_folder, 'q' + i + '.csv')
                results_dict['questions'][i] = {
                                'index': i,
                                'title': self.index_df.loc[i][0], 
                                'response_data': pd.read_csv(question_file, encoding = 'utf-8'),
                                'has_comments': False
                               }
            except:
                raise FileExistsError('Question file {q_file} could not be found, please modify your index or restore the file'.format(q_file = question_file)) 
    def __load_comments(self):
        for file in os.listdir(self.path_to_raw_folder):
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
                        file_path = os.path.join(self.path_to_raw_folder, filename)
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
        json_obj['number_of_comments'] = int(json_obj['number_of_comments'])
        json_obj['number_of_comment_sections'] = int(json_obj['number_of_comment_sections'])
        json_obj['number_of_sentences'] = int(json_obj['number_of_sentences'])
        json_obj['number_of_words'] = int(json_obj['number_of_words'])
        json_obj['question_index'] = json_obj['question_index'].to_dict()
        json_obj['comments'] = json_obj['comments'].to_dict()
        json_obj['sentences'] = json_obj['sentences'].to_dict()
        for key in json_obj['questions']:
            json_obj['questions'][key]['response_data'] = json_obj['questions'][key]['response_data'].to_dict()
            if json_obj['questions'][key]['has_comments'] == True:
                json_obj['questions'][key]['comments'] = json_obj['questions'][key]['comments'].to_dict()
                json_obj['questions'][key]['sentences'] = json_obj['questions'][key]['sentences'].to_dict()
        with open(self.path_to_json_file,'w+') as f:
            f.write(json.dumps(json_obj, ensure_ascii= False))
            f.close()
    def __get_current_datetime(self):
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    def __check_index(self):
        db = self.db
        query = """SELECT *
               FROM index_table
               WHERE raw_data_path = '{path}' ;
            """.format(path = self.path_to_raw_folder).replace("\n","")
        res = db.execute(query).fetchone()
        return res 
    def __initialise_row(self):
        db = self.db
        query = """
               INSERT INTO index_table(survey_name, raw_data_path, processed_data_path, json_path, status_id, processing_date)
                VALUES('{s}','{r}','{p}','{j}',{st},'{d}');
            """.format(s= self.path_to_raw_folder,
                       r= self.path_to_raw_folder,
                       p= self.path_to_raw_folder,
                       j= self.path_to_raw_folder,
                       st = "(SELECT id FROM statuses WHERE status_name = 'processing')",
                       d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')).replace("\n", "")
        db.execute(query)
            #flush the pipeline
        db.commit()
    def __get_key(self):
        db = self.db
        key = self.__check_index()
        row_initialised = False
        if key is None:
            self.__initialise_row()
            key = db.execute("SELECT id FROM index_table WHERE raw_data_path = '{path}'".format(path = self.path_to_raw_folder)).fetchone()['id']
            row_initialised = True 
        else:
            key = key['id']
        self.key = key
        return row_initialised
    def __update_survey_entry_details(self):
        db = self.db
        self.path_to_processed_folder = os.path.join(self.path_to_processed_folder,str(self.key))
        self.path_to_json_file = os.path.join(self.path_to_json_folder, str(self.key) + '.json') 
        query = "UPDATE index_table SET survey_name = '{survey_name}' , processed_data_path = '{p_path}', json_path = '{j_path}' WHERE id = {id}".format(
                survey_name = self.metadata_columns['Title_Of_Survey'],
                p_path = self.path_to_processed_folder,
                j_path = self.path_to_json_file,
                id = self.key
        )
        db.execute(query)
        db.commit()
        query = """
        INSERT INTO logs(index_id, log_type_id, log_text, date_of_log)
         VALUES({id},{t},'{l}','{d}');
        """.format( id = self.key,
                    t = "(SELECT id FROM logTypes WHERE log_type = 'new_survey_processing')",
                    l = "New survey data being processed",
                    d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        ).replace("\n","")
        db.execute(query)
        db.commit()
    def __get_status(self, status_id):
        db = self.db
        status = db.execute(("SELECT status_name FROM statuses WHERE id = {id} ;".format(id = status_id))).fetchone()
        status = status['status_name']
        return status
    def __get_survey_entry(self):
        db = self.db
        row_initialised = self.__get_key()
        res = db.execute('SELECT * FROM index_table WHERE id = {id}'.format(id= self.key)).fetchone()
        return [row_initialised, res]
    def __mark_survey_status(self):
        #load into function level variable for convenience
        db = self.db
        #execute the query to check if the data exists and fetch the row if it does
        res = self.__get_survey_entry()
        query = "UPDATE index_table SET status_id = {status}, processing_date = '{t}' WHERE id = {my_id} ;".format(
            status = "(SELECT id FROM statuses WHERE status_name = 'processing')",
            my_id = self.key, 
            t = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')).replace("\n","")
        db.execute(query)
        query = """
        INSERT INTO logs(index_id, log_type_id, log_text, date_of_log)
         VALUES({id},{t},'{l}','{d}');""".format(id = self.key,
                t = "(SELECT id FROM logTypes WHERE log_type = 'survey_reprocessing')",
                l = "processing survey",
                d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')).replace("\n","")
        db.execute(query)
        db.commit()
        self.path_to_processed_folder = res[1]['processed_data_path']
        self.path_to_json_file = res[1]['json_path']
    def __completed(self):
        #when called will update the status and log it
        db = self.db
        db.execute(("""
        UPDATE index_table
         SET status_id = {status}
         WHERE id = {my_id} ;
        """.format(status = "(SELECT id FROM statuses WHERE status_name = 'completed')"
            ,my_id = self.key).replace("\n","")))
        db.execute(("""
                INSERT INTO logs(index_id, log_type_id, log_text, date_of_log)
                 VALUES({id},{t},'{l}','{d}');""".format(id = self.key,
                       t = "(SELECT id FROM logTypes WHERE log_type = 'completion_notice')",
                       l = "Survey processing completed",
                       d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            ).replace("\n","")))
        db.commit()
    def __error_logger(self, error):
        db = self.db
        error_name = type(error).__name__ 
        query = "SELECT id FROM errors WHERE error = '{error_name}'".format(error_name = error_name)
        res = db.execute(query).fetchone()
        self.__get_survey_entry()
        if res is None:
            query = "SELECT id FROM errors WHERE error = 'UnknownError'"
            res = db.execute(query).fetchone()['id']
        else:
            query = """INSERT INTO logs(index_id, error_id, log_type_id, log_text, date_of_log)
             VALUES ({iid},{eid},{ltid},"{lt}",'{dof}')""".format(
                 iid = self.key,
                 eid = res['id'],
                 ltid = "(SELECT id FROM logTypes WHERE log_type = 'error')",
                 lt = str(error),
                 dof = self.__get_current_datetime() 
             ).replace("\n","")
            db.execute(query)
            query = "UPDATE index_table SET status_id = {status_id} WHERE id = {key}".format(
                status_id = "(SELECT id FROM statuses WHERE status_name = 'erred')",
                key = self.key
            )
            db.execute(query)
            db.commit()
        raise error
    def __check_metadata_format(self):
        metadata_columns = {
            "Title_Of_Survey" : False,
            "Date_Of_Survey": False,
            "Location_Of_Event": False,
            "Number_Of_Questions": False,
            "Date_Last_Scraped":False
        }
        for column in self.metadata.columns:
            metacol = metadata_columns.get(column)
            if metacol is None:
                error = MetadataFormatNotValid("Column " + column + " is not valid")
                self.__error_logger(error)
            else:
                column_value = self.metadata.loc[0,column]
                if column_value == "" or column_value != column_value:
                    error = MetadataFormatNotValid("Columns included in metadata csv must not be empty")
                    self.__error_logger(error)
                else:
                    metadata_columns[column] = column_value
        if metadata_columns["Title_Of_Survey"] == False:
            error = MetadataFormatNotValid("Column Title_Of_Survey in metadata.csv must be provided")
            self.__error_logger(error)
        if metadata_columns["Date_Of_Survey"] == False:
            error = MetadataFormatNotValid("Column Date_Of_Survey in metadata.csv must be provided")
            self.__error_logger(error)
        self.metadata_columns = metadata_columns
    def __check_index_format(self):
        index_columns = {
            "Question_Number": False,
            "Question": False,
            "Question_Type": False
        }
        for column in self.index_df.columns:
            index_col = index_columns.get(column)
            if index_col is None:
                error = QuestionIndexFormatNotValid("Column " + column + " is not valid")
                self.__error_logger(error)
            else:
                index_columns[column] = True
        self.index_columns = index_columns
    def get_all_questions(self):
        return self.results_dict['questions']
class CommentSectionLoader:
    def __init__(self, sectionDict, 
                 section_key, 
                 path_to_comments):
        #section paths are made this is under the comments folder consisting of section_ + the sectionKey (question index)
        self.path_to_section = os.path.join(path_to_comments, "section_" + section_key)
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
        self.path_to_comment = os.path.join(path_to_section, "comment_" + comment_key)
        self.comment = comment
        self.number_of_words = 0
        self.sentences_frames = []
        if os.path.isdir(self.path_to_comment) == False:
            os.mkdir(self.path_to_comment)
            self.__init_sentiment()
        elif os.path.isfile(os.path.join(self.path_to_comment,'comment_' + comment_key + '.csv')) == False:
            self.__init_sentiment()
        else:
            comment_df = pd.read_csv(os.path.join(self.path_to_comment, 'comment_' + comment_key + '.csv'),
            encoding = 'utf-8', index_col = 0)
            self.comment_frame = comment_df
            self.language = comment_df.loc[comment_key,'language']
            self.sentiment_score = comment_df.loc[comment_key,'sentiment_score']
            self.magnitude_score = comment_df.loc[comment_key,'magnitude_score']
            self.number_of_sentences =  int(comment_df.loc[comment_key,'number_of_sentences'])
            self.number_of_words = int(comment_df.loc[comment_key, 'number_of_words'])
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
        comment_df.to_csv(os.path.join(self.path_to_comment, 'comment_' + self.comment_key + '.csv')
        ,encoding = 'utf-8')
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
        self.path_to_sentence = os.path.join(path_to_comment, "sentence_" + sentence_key + ".csv")
        if os.path.isfile(self.path_to_sentence) == False:
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
            self.number_of_words = int(sentence_df.loc[sentence_key,'number_of_words'])
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
  