import sqlite3
from flask import current_app, g
import os
import random
import string
from datetime import datetime
from werkzeug.security import generate_password_hash
def get_db():
    if 'db' not in g:
        g.index_db = sqlite3.connect(
            current_app.config['INDEX_DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.index_db.row_factory = sqlite3.Row
        g.user_db = sqlite3.connect(
            current_app.config['USERS_DATABASE'],
            detect_types= sqlite3.PARSE_DECLTYPES
        )
        g.user_db.row_factory = sqlite3.Row
    return g.user_db, g.index_db
def close_db(e=None):
    index_db = g.pop('index_db', None)
    if index_db is not None:
        index_db.close()
    user_db = g.pop('user_db', None)
    if user_db is not None:
        user_db.close()
def init_app():
    current_app.teardown_appcontext(close_db)
    user_db, _ = get_db()
    query = "SELECT * FROM sqlite_master WHERE type='table' AND  name = 'users'"
    res = user_db.execute(query).fetchone()
    if res == None:
        user_schema_path = os.path.join(current_app.config['DATABASE_SCHEMAS'], 'users_schema.sql')
        if not os.path.isfile(user_schema_path):
            raise FileNotFoundError("unable to find users_schema.sql to initialise user database")
        with open(user_schema_path) as f:
            user_db.executescript(f.read())
        #generate cryptographically secure username and password which will be changed upon first login
        temp_admin_username = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = 8))
        temp_admin_pass = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = 32))
        #should the username and password of all admin be lost recovery key can be used for access this will change every 15 minutes 
        recovery_key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = 32))
        query = """INSERT INTO recovery(recovery_key, date_generated) VALUES ('{r}', '{d}')""".format(
            r = recovery_key,
            d = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
        user_db.execute(query)
        user_db.commit()
        query = """INSERT INTO users (username, password, username_change_required, password_change_required, access_level_id, created_on)
         VALUES ('{un}', '{ps}' , {ucr}, {pcr}, {ali}, '{co}') """.format(
             un = temp_admin_username,
             ps = generate_password_hash(temp_admin_pass),
             ucr = 1,
             pcr = 1,
             ali = "(SELECT id FROM accessLevels WHERE access_level = 'owner')",
             co = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
         )
        user_db.execute(query)
        user_db.commit()
        if not os.path.isdir("./recovery"):
            os.mkdir("./recovery")
        with open("./recovery/temp_owner_credentials.txt", 'w+') as f:
            f.write("username : " + temp_admin_username + "\n")
            f.write("password : " + temp_admin_pass + "\n")
            f.write("recovery_key : " + recovery_key)
            f.close()
