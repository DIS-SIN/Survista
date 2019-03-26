
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
    
    #if the secret key is none or the mode is production we want to get the secret key from the environment variable 
    if app.config.get('SECRET_KEY') is None or mode == "production":
        if os.environ.get("SURVISTA_SECRET_KEY") is None:
            raise ValueError("SURVISTA_SECRET_KEY must be set as an environment variable")
        app.config['SECRET_KEY'] = os.environ['SURVISTA_SECRET_KEY']
    #call in the verify function to validate application configuration

    verify(app)
    celery = make_celery(app)
    @celery.task()
    def run_check():
        try:
            os.chdir('./utils')
        except:
            pass
        fileChecker()
    return app, celery