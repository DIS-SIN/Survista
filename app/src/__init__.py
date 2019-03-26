
def create_app(mode = "production", 
    static_path = "./static", 
    templates_path = "./templates", 
    instance_path = "./instance"):
    from flask import Flask
    import os
    import settings
    from .utils.celery_maker import make_celery
    from .utils.fileChecker import fileChecker
    from .utils.verify_user_constrains import verify
    from src.database.db import init_app, init_db
    app = Flask(__name__)
    # configuring application
    app.config.from_object("settings.default_settings")

    if mode == "production":
        try:
            app.config.from_object("settings.production_settings")
        except ModuleNotFoundError:
            pass   
    elif mode == "development":
        try:
            app.config.from_object("settings.development_settings")
        except ModuleNotFoundError:
            pass
    else:
        raise ValueError("mode must either be production or development")

    #call in the verify function to validate application configuration
    verify(app)

    #if the secret key is none or the mode is production we want to get the secret key from the environment variable 
    if app.config.get('SECRET_KEY') is None or mode == "production":
        if os.environ.get("SURVISTA_SECRET_KEY") is None:
            if mode == "production":
                raise ValueError("SURVISTA_SECRET_KEY must be set as an environment \
                    variable for production environments")
            else:
                raise ValueError("SECRET_KEY was not set in the settings \
                    thus must be provided in the SURVISTA_SECRET_KEY environment variable")
        app.config['SECRET_KEY'] = os.environ['SURVISTA_SECRET_KEY']

    if app.config.get("SQLALCHEMY_DATABASE_URI") is None or mode == "production":
        if os.environ.get('SURVISTA_SQLALCHEMY_DATABASE_URI') is None:
            if mode == "production":
                raise ValueError("SURVISTA_SQLALCHEMY_DATABASE_URI must be set as an environment \
                    variable for production environments")
            else:
                raise ValueError("SECRET_KEY was not set in the settings \
                    thus must be provided in the SURVISTA_SECRET_KEY environment variable")
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI']
    
    init_app(app)
    
    @app.cli.command("-initdb")
    def initialise_database():
        init_db()

    #call in the verify function to validate application configuration

    celery = make_celery(app)
    @celery.task()
    def run_check():
        try:
            os.chdir('./utils')
        except:
            pass
        fileChecker()
    return app, celery