DROP TABLE IF EXISTS index_table;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS erros;
DROP TABLE IF EXISTS log_types;
DROP TABLE IF EXISTS statuses;
CREATE TABLE index_table(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_name TEXT NOT NULL,
    raw_data_path TEXT UNIQUE NOT NULL,
    processed_data_path TEXT UNIQUE NOT NULL,
    json_path TEXT UNIQUE NOT NULL,
    status_id INTEGER NOT NULL,
    processing_date TEXT NOT NULL,
    CONSTRAINT fk_statuses
        FOREIGN KEY (status_id)
        REFERENCES statuses(id)
);
CREATE TABLE logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_id INTEGER,
    error_id INTEGER,
    log_type_id INTEGER NOT NULL,
    raw_data_path TEXT,
    log_text TEXT NOT NULL,
    date_of_log TEXT NOT NULL,
    CONSTRAINT fk_index
        FOREIGN KEY (index_id)
        REFERENCES index_table(id),
    CONSTRAINT fk_errors
        FOREIGN KEY (error_id)
        REFERENCES errors(id),
    CONSTRAINT fk_logTypes
        FOREIGN KEY (log_type_id)
        REFERENCES logTypes(id)
);
CREATE TABLE errors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error TEXT NOT NULL,
    error_description TEXT 
);
CREATE TABLE logTypes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_type TEXT NOT NULL,
    log_type_description TEXT
);
CREATE TABLE statuses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL,
    status_description TEXT
);
INSERT INTO errors (error, error_description)
VALUES ('FileNotFound', "The file is requested but could not be loaded or found"),
('MetadataFileNotExist', "The survey metadata file could not be found"),
('RawdataFolderNotExist', "The raw data folder was deleted while processing"),
('QuestionIndexNotExist', "The survey question index file could not be found"),
('MetadataFormatNotValid', "The survey_matadata.csv format is not valid"),
('QuestionIndexFormatNotValid',"The question_index.csv format is not valid"),
('UnknownError', "An unknown error has occured and could not be resolved");
INSERT INTO logTypes(log_type, log_type_description)
VALUES ('new_survey_processing', "Processing a new survey data folder"),
('survey_reprocessing', "Reprocessing an existing survey data folder"),
('completion_notice', "Survey data has been processed succesfully and is available to the API"),
('error', 'An error has occured while processing the survey data'),
('deletion', 'Survey raw_folder is not present and so has been removed from the index and API');
INSERT INTO statuses(status_name, status_description)
VALUES ('processing', 'The data for this survey is being processed'),
('completed', 'The data for this survey has completed processing'),
('erred', "Processing of this survey's data has resulted in an error");