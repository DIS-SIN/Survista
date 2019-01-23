DROP TABLE IF EXISTS index;
DROP TABLE IF EXISTS logs;

CREATE TABLE index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_name TEXT NOT NULL,
    raw_data_path TEXT UNIQUE NOT NULL,
    processed_data_path TEXT UNIQUE NOT NULL,
    json_path TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    processing_date TEXT NOT NULL
);
CREATE TABLE logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_id INTEGER,
    log_type TEXT NOT NULL,
    log_text TEXT NOT NULL,
    date_of_log TEXT NOT NULL
    CONSTRAINT fk_index
        FOREIGN KEY (index_id)
        REFERENCES index(id)
);