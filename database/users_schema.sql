DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS logTypes;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS accessLevels;
DROP TABLE IF EXISTS recovery;
CREATE TABLE recovery(
   recovery_key TEXT NOT NULL,
   date_generated TEXT NOT NULL 
);
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    username_change_required INTEGER DEFAULT 0,
    password_change_required INTEGER DEFAULT 0,
    access_level_id INTEGER NOT NULL,
    access_decomission_on TEXT,
    access_decomission_to TEXT, 
    created_on TEXT NOT NULL,
    last_login TEXT,
    CONSTRAINT fk_accessLevels
        FOREIGN KEY (access_level_id)
        REFERENCES accessLevels(id)
);
CREATE TABLE resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_table_id INTEGER UNIQUE NOT NULL,
    access_level_id INTGER NOT NULL,
    set_on TEXT NOT NULL,
    CONSTRAINT fk_accessLevels
        FOREIGN KEY (access_level_id)
        REFERENCES accessLevels(id)
);
CREATE TABLE logs(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   index_table_id INTEGER,
   user_id INTEGER NOT NULL,
   log_type_id INTEGER NOT NULL,
   log_text TEXT
);
CREATE TABLE accessLevels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    access_level TEXT UNIQUE NOT NULL,
    created_on TEXT NOT NULL,
    equivelent_to INTEGER,
    decomission_on TEXT,
    decomission_to INTEGER,
    CONSTRAINT fk_decomissionTo
       FOREIGN KEY (decomission_to)
       REFERENCES accessLevels(id),
    CONSTRAINT fk_equivelent_to
       FOREIGN KEY (equivelent_to)
       REFERENCES accessLevels(id)
);
CREATE TABLE logtypes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_type TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL
);
INSERT INTO logtypes(log_type, description) 
VALUES ('user_created', 'a user has been created'),
('user_deactivated', 'a user has been deactivated'),
('access_level_set', 'a access level has been set for a resource'),
('access_level_decomissioned', 'an access level has been decomissioned'),
('access_level_created', 'a new access level has been created');

INSERT INTO accessLevels(access_level, created_on)
VALUES ('owner', strftime('%Y-%m-%d %H:%M:%S', date('now'))),
('deactivated', strftime('%Y-%m-%d %H:%M:%S', date('now'))),
('admin',  strftime('%Y-%m-%d %H:%M:%S', date('now'))),
('restricted', strftime('%Y-%m-%d %H:%M:%S', date('now'))),
('open',  strftime('%Y-%m-%d %H:%M:%S', date('now')));