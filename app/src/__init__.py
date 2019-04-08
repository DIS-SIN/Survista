

def create_app(mode="production",
               static_path="./static",
               templates_path="./templates",
               instance_path="./instance"):
    from flask import Flask
    import os
    # from .utils.celery_maker import make_celery
    # from .utils.fileChecker import fileChecker
    from .utils.verify_user_constrains import verify
    from src.database.db import init_app, init_db
    from warnings import warn
    from werkzeug.utils import ImportStringError
    app = Flask(__name__)
    # configuring application
    app.config.from_object("configs.default_settings")

    if mode == "development":
        app.config.from_object("configs.development_settings")
    else:
        if mode != "production":
            warn("FLASK_ENV was set as an unrecognized value, " +
                 "application is falling back on production mode")
        try:
            app.config.from_object("configs.production_settings")
        except ImportStringError:
            pass

    # call in the verify function to validate application configuration
    verify(app)

    # if the secret key is none or the mode is production
    # we want to get the secret key from the environment variable
    if app.config.get('SECRET_KEY') is None \
            or mode == "production":
        if os.environ.get("SURVISTA_SECRET_KEY") is None:
            if mode == "production":
                raise ValueError(
                    "SURVISTA_SECRET_KEY must be set as an environment " +
                    "variable for production environments")
            else:
                raise ValueError(
                    "SECRET_KEY was not set in the settings thus must be " +
                    "provided in the SURVISTA_SECRET_KEY environment variable")
        app.config['SECRET_KEY'] = os.environ['SURVISTA_SECRET_KEY']
    elif os.environ.get('SURVISTA_SECRET_KEY') is not None:
        app.config['SECRET_KEY'] = os.environ['SURVISTA_SECRET_KEY']

    if app.config.get("SQLALCHEMY_DATABASE_URI") is None \
            or mode == "production":
        if os.environ.get('SURVISTA_SQLALCHEMY_DATABASE_URI') is None:
            if mode == "production":
                raise ValueError(
                    "SURVISTA_SQLALCHEMY_DATABASE_URI must be set as an " +
                    "environment variable for production environments")
            else:
                raise ValueError(
                    "SQLALCHEMY_DATABAST_URI was not set in the settings " +
                    "thus must be provided in the " +
                    "SURIVITA_SQLALCHEMY_DATABASE_URI environment variable")

        app.config['SQLALCHEMY_DATABASE_URI'] = \
            os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI']
    elif os.environ.get("SURVISTA_SQLALCHEMY_DATABASE_URI") is not None:
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI']

    if not os.path.isabs(static_path):
        static_path = os.path.abspath(static_path)
    if not os.path.isdir(static_path):
        raise FileNotFoundError('static folder was not able to be found')

    app.static_folder = static_path

    if not os.path.isabs(templates_path):
        templates_path = os.path.abspath(templates_path)
    if not os.path.isdir(templates_path):
        raise FileNotFoundError('templates folder was not able to be found')

    app.template_folder = templates_path

    if not os.path.isabs(instance_path):
        instance_path = os.path.abspath(instance_path)
    if not os.path.isdir(instance_path):
        os.mkdir(instance_path)

    app.instance_path = instance_path

    init_app(app)

    @app.cli.command("initdb")
    def initialise_database():
        init_db(app)

    # Celery configuration area
    return app