from flask import current_app, g, Flask
from src.models import init_base
from neomodel.util import Database


def get_db() -> Database:
    """
    Get the loaded db object from neomodel
    """
    if "db" not in g:
        from neomodel import db
        if "db" not in g:
            g.db = db
    return g.db


def close_db(e=None):
    """
    Used to close the session and end the connection between the database
    and the client
    """
    db = g.pop('db', None)
    if db is not None:
        del db


def init_app(app: Flask):
    # register the close_db with the removal of the app context event
    app.teardown_appcontext(close_db)
    # init_base is used to initialise the global SQLAlchemy
    init_base(app)


def init_db(app):

    from neomodel import install_all_labels
    install_all_labels()

    from .utils.detect_loaders import detect
    import importlib
    try:
        loaders = importlib.import_module('src.database.loaders')
        mods = detect(loaders)
        for mod in mods:
            mod_obj = getattr(loaders, mod)
            run_method = getattr(mod_obj, 'run')
            print(run_method)
            run_method(app)
    except ImportError:
        pass


def distroy_db(app):
    """
    wipe the database
    """
    from neomodel.util import clear_neo4j_database
    from neomodel import db
    clear_neo4j_database(db)
    from neomodel import remove_all_labels
    remove_all_labels()
