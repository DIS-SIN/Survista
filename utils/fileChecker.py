import sqlite3 as sq
import pandas as pd
import os
import shutil
from surveyDataLoader import SurveyDataLoader
from datetime import datetime
databaseFolder = '../database'
staticFolder = '../static'
rawDataFolder = staticFolder + '/raw_data'
processedDataFolder = staticFolder + '/processed_data'
jsonDataFolder = staticFolder + '/json'
if not os.path.isdir(databaseFolder):
    raise FileNotFoundError('database folder required')
if not os.path.isdir(staticFolder) :
    raise FileNotFoundError('static folder required')
try:
    os.makedirs(rawDataFolder)
except OSError:
    pass
try: 
    os.makedirs(processedDataFolder)
except OSError:
    pass
try:
    os.makedirs(jsonDataFolder)
except OSError:
    pass
def get_db(database_path):
    db = sq.connect(database_path, detect_types= sq.PARSE_DECLTYPES)
    db.row_factory = sq.Row
    return db
def load_survey(raw_path, processed_path, json_path, db, survey_processed= False):
    try:
        SurveyDataLoader(raw_path,processedDataFolder,jsonDataFolder, db, survey_processed)
    except:
        pass 
db = get_db(databaseFolder + '/index.sqlite')
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type = 'table'", db)
if tables.shape[0] == 0:
    with open(databaseFolder + '/schema.sql') as f:
       db.executescript(f.read())
    for name in os.listdir(processedDataFolder):
        name = os.path.join(processedDataFolder, name)
        if os.path.isdir(name):
            shutil.rmtree(name)
    for name in os.listdir(jsonDataFolder):
        name = os.path.join(jsonDataFolder, name)
        if os.path.isfile(name):
            os.remove(name) 
    for name in os.listdir(rawDataFolder):
        name = os.path.join(rawDataFolder, name)
        if os.path.isdir(name):
            load_survey(name, processedDataFolder, jsonDataFolder, db)
    db.close()    
else:
    for name in os.listdir(rawDataFolder):
        name = os.path.join(rawDataFolder, name)
        if os.path.isdir(name):
            query = "SELECT (SELECT status_name FROM statuses WHERE id = it.status_id) survey_status, processed_data_path, json_path FROM index_table AS it WHERE raw_data_path = '{path}'".format(path = name)
            res = db.execute(query).fetchone()
            if res is None:
                load_survey(name, processedDataFolder, jsonDataFolder, db)
            elif res['survey_status'] != 'processing':
                if not os.path.isdir(res['processed_data_path']):
                    load_survey(name, processedDataFolder, jsonDataFolder, db)
                elif not os.path.isfile(res['json_path']):
                    load_survey(name, processedDataFolder, jsonDataFolder, db, True)
    query = "SELECT raw_data_path, processed_data_path, json_path FROM index_table"
    res = db.execute(query).fetchall()
    for row in res:
        if not os.path.isdir(row['raw_data_path']):
            if os.path.isfile(row['json_path']):
                os.remove(row['json_path'])
            if os.path.isdir(row['processed_data_path']):
                shutil.rmtree(row['processed_data_path'])
            query = "DELETE FROM index_table WHERE raw_data_path = '{path}'".format(path = row['raw_data_path'])
            db.execute(query)
            query = "INSERT INTO logs(log_type_id, raw_data_path, log_text, date_of_log) VALUES ({lti},'{rdp}','{lt}','{dol}')".format(
                lti = "(SELECT id FROM logTypes WHERE log_type = 'deletion')",
                rdp = row['raw_data_path'],
                lt = "Survey deleted from repository",
                dol = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            )
            db.execute(query)
            db.commit()
    db.close()




   





