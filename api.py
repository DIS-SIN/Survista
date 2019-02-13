from flask import Flask
from flask_restful import Resource, Api, output_json
import os
from celery_maker import make_celery
from utils.fileChecker import fileChecker
app = Flask(__name__)
# configuring application
if os.path.isfile('./configs/settings.cfg'):
    os.environ['APPLICATION_SETTINGS'] = os.path.realpath('./configs/settings.cfg')
    app.config.from_envvar('APPLICATION_SETTINGS')
    if app.config['ENV'] == 'development':
        app.config['SEND_FILE_MAX_AGE_DEFAULT '] = 0
        app.config['DEBUG'] = True
    else:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 600
    #getting user settings if they exist
    password_symbols_required = app.config.get('PASSWORD_SYMBOLS_REQUIRED')
    password_symbols = app.config.get('PASSWORD_SYMBOLS')
    password_uppercase_required = app.config.get('PASSWORD_UPPERCASE_REQUIRED')
    password_numbers_required = app.config.get('PASSWORD_NUMBERS_REQUIRED')
    password_length_min = app.config.get('PASSWORD_LENGTH_MIN')
    password_length_max = app.config.get('PASSWORD_LENGTH_MAX')
    reserved_usernames_delimeter = app.config.get('RESERVED_USERNAMES_DELIMETER')
    reserved_usernames = app.config.get('RESERVED_USERNAMES')
    username_length_min = app.config.get('USERNAME_LENGTH_MIN')
    username_length_max = app.config.get('USERNAME_LENGTH_MAX')
    ###password checks###
    if password_symbols_required is not None and password_symbols_required == True:
        if password_symbols is None:
            password_symbols = '@$%#*!&'
        app.config['PASSWORD_SYMBOLS'] = list(password_symbols)
    else:
        app.config['PASSWORD_SYMBOLS_REQUIRED'] = False
    if password_uppercase_required is None or not password_uppercase_required == True:
        app.config['PASSWORD_UPPERCASE_REQUIRED'] = False
    if password_uppercase_required is None or not password_numbers_required == True:
        app.config['PASSWORD_NUMBERS_REQUIRED'] = False 
    #password_length_min  
    if password_length_min is not None and type(password_length_min) != int:
        raise TypeError('PASSWORD_LENGTH_MIN must be of type int not ' + str(type(password_length_min)) )
    elif password_length_min is None:
        password_length_min = 8
        app.config['PASSWORD_LENGTH_MIN'] = 8
    elif password_length_min > 16 or password_length_min < 4:
        raise ValueError('PASSWORD_LENGTH_MIN must be between the values of 4 and 16')
    #password_length_max
    if password_length_max is not None and type(password_length_max) != int:
        raise TypeError('PASSWORD_LENGTH_MAX must be of type int ' + str(type(password_length_max)))
    elif password_length_max is None:
        password_length_max = 20
        app.config['PASSWORD_LENGTH_MAX'] = 20
    elif password_length_max > 32 or password_length_max < 8:
        raise ValueError('PASSWORD_LENGTH_MAX must be between the values of 8 and 32')
    elif password_length_max < password_length_min:
        raise ValueError('PASSWORD_LENGTH_MAX must not be less than PASSWORD_LENGTH_MIN')
    ###username checks###
    if reserved_usernames is not None:
        if reserved_usernames_delimeter is None:
            raise ValueError('RESERVED_USERNAMES provided but no RESERVED_USERNAMES_DELIMETER was provided')
        if type(reserved_usernames) != str:
            raise TypeError('RESERVED_USERNAMES must be of type str')
        elif type(reserved_usernames_delimeter) != str:
            raise TypeError("RESERVED_USERNAMES_DELIMETER must be of type str")
        app.config['RESERVED_USERNAMES'] = reserved_usernames.split(reserved_usernames_delimeter)
    else:
        reserved_usernames = 'admin,owner,chuck_norris'
        app.config['RESERVED_USERNAMES'] = reserved_usernames.split(',')
    #username length min
    if username_length_min is not None and type(username_length_min) != int:
        raise TypeError('USERNAME_LENGTH_MIN must be of type int not ' + str(type(username_length_min)))
    elif username_length_min is None:
        username_length_min = 5
        app.config['USERNAME_LENGTH_MIN'] = 5
    elif username_length_min > 8 or username_length_min < 4:
        raise ValueError('USERNAME_LENGTH_MIN must be between the values of 4 and 16')
    #username length max
    if username_length_max is not None and type(username_length_max) != int:
        raise TypeError('USERNAME_LENGTH_MAX must be of type int not '+ str(type(username_length_max)))
    elif username_length_max is None:
        username_length_max = 10
        app.config['USERNAME_LENGTH_MAX'] = 10
    elif username_length_max > 15 or username_length_max < 6:
        raise ValueError('USERNAME_LENGTH_MAX must be between the values of 8 and 32')
    elif username_length_max < username_length_min:
        raise ValueError('USERNAME_LENGTH_MAX must not be less than USERNAME_LENGTH_MIN')
else:
    if os.environ.get("SURVISTA_SECRET_KEY") is None:
        raise ValueError("SURVISTA_SECRET_KEY must be set as an environment variable")
    app.config['SECRET_KEY'] = os.environ['SURVISTA_SECRET_KEY']
    app.config['MAIN_API_ROUTE'] = "api"
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 600
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 600
    app.config['PASSWORD_SYMBOLS_REQUIRED'] = True
    app.config['PASSWORD_SYMBOLS'] = list('@$%#*!&')
    app.config['PASSWORD_NUMBERS_REQUIRED'] = True
    app.config['PASSWORD_UPPERCASE_REQUIRED'] = True
    app.config['PASSWORD_LENGTH_MIN'] = 8
    app.config['PASSWORD_LENGTH_MAX'] = 20
    app.config['RESERVED_USERNAMES'] = 'admin,owner,chuck_norris'.split(',')
    app.config['USERNAME_LENGTH_MIN'] = 5
    app.config['USERNAME_LENGTH_MAX'] = 10     
#configure database path using absolute path so that it is accessible from any package
app.config['INDEX_DATABASE'] = os.path.realpath('./database/index.sqlite')
app.config['USERS_DATABASE'] = os.path.realpath('./database/users.sqlite')
app.config['DATABASE_SCHEMAS'] = os.path.realpath('./database')
app.config['ALLOWED_EXTENSIONS'] = set(['zip'])
app.config['TEMP_PATH'] = os.path.realpath('./temps')
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
try:
    os.mkdir(app.config['TEMP_PATH'])
except:
    pass
import db
with app.app_context():
    db.init_app()
import basicauth
basicauth.init_app(app)
#create api
import auth
app.register_blueprint(auth.bp)
import index
app.register_blueprint(index.bp)
celery = make_celery(app)
app.add_url_rule('/', endpoint = '/index')
class UnicodeApi(Api):
    def __init__(self, *args, **kwargs):
        super(UnicodeApi, self).__init__(*args, **kwargs)
        self.app.config['RESTFUL_JSON'] = {
            'ensure_ascii': False
        }
        self.representations = {
            'application/json; charset=utf-8': output_json,
        }
api = UnicodeApi(app, prefix= '/' +  app.config['MAIN_API_ROUTE'])
class ApiInfo(Resource):
    def get(self):
        return {"versionsAvailable" : [
            "V1.0"
        ]}
api.add_resource(ApiInfo,'/')
from api_v1.api_version_info import V1
api.add_resource(V1,'/V1.0')
from api_v1.surveys import Surveys
api.add_resource(Surveys,'/V1.0/surveys')
from api_v1.survey import Survey
api.add_resource(Survey,
'/V1.0/surveys/<int:surveyId>',
'/V1.0/surveys/slug/<string:slugName>')
@celery.task()
def run_check():
    try:
        os.chdir('./utils')
    except:
        pass
    fileChecker()
if __name__ == "__main__":
    app.run()
      
