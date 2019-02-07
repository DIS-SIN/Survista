from flask import Flask
from flask_restful import Resource, Api
import os

def create_api():
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
            app.config['PASSWORD_SYMBOLS'] = password_symbols.split()
        else:
            app.config['PASSWORD_SYMBOLS_REQUIRED'] = False
        if password_uppercase_required is None or not password_uppercase_required == True:
            app.config['PASSWORD_UPPERCASE_REQUIRED'] = False
        if password_uppercase_required is None or not password_numbers_required == True:
            app.config['PASSWORD_NUMBERS_REQUIRED'] = False 
        #password_length_min  
        if password_length_min is not None and type(password_length_min) != int():
            raise TypeError('PASSWORD_LENGTH_MIN must be of type int')
        elif password_length_min is None:
            password_length_min = 8
            app.config['PASSWORD_LENGTH_MIN'] = 8
        elif password_length_min > 16 or password_length_min < 4:
            raise ValueError('PASSWORD_LENGTH_MIN must be between the values of 4 and 16')
        #password_length_max
        if password_length_max is not None and type(password_length_max) != int():
            raise TypeError('PASSWORD_LENGTH_MAX must be of type int')
        elif password_length_max is None:
            password_length_max = 20
            app.config['PASSWORD_LENGTH_MAX'] = 20
        elif password_length_max > 32 or password_length_max < 8:
            raise ValueError('PASSWORD_LENGTH_MAX must be between the values of 8 and 32')
        elif password_length_max < password_length_min:
            raise ValueError('PASSWORD_LENGTH_MAX must not be less than PASSWORD_LENGTH_MIN')
        ###username checks###
        
    else:
        if os.environ.get("SURVISTA_SECRET_KEY") is None:
            raise ValueError("SURVISTA_SECRET_KEY must be set as an environment variable")
        app.config['SECRET_KEY'] = os.environ['SURVISTA_SECRET_KEY']
        app.config['MAIN_API_ROUTE'] = "api"
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['PERMANENT_SESSION_LIFETIME'] = 600
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 600
        app.config['PASSWORD_SYMBOLS_REQUIRED'] = True
        app.config['PASSWORD_SYMBOLS'] = '@$%#*!&'.split()
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
    import db
    with app.app_context():
        db.init_app()
    #create api
    import auth
    app.register_blueprint(auth.bp)
    api = Api(app, prefix= app.config['MAIN_API_ROUTE'])
    #register routes
    return api, app
if __name__ == "__main__":
    api, app = create_api()
    app.run()
      
