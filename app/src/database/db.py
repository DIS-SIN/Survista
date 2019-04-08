from flask import current_app, g, Flask
from src.models.base_model import base
from src.models import init_base


def get_db():
    """
    Used to load the sqlalchemy session in the g local proxy
    and then return the session
    """
    if 'scoped_session' not in g:
        # get the scoped_session registry from the SQLAlchemy object
        g.scoped_session = base.session
    if 'db' not in g:
        # get the current session from the scoped_session registry
        # >>> some_session = g.scoped_session()
        # >>> other_session = g.scoped_session()
        # >>> some_session is other_session
        # >>> True
        g.db = g.scoped_session()
    return g.db


def close_db(e=None):
    """
    Used to close the session and end the connection between the database
    and the client
    """
    scoped_session = g.pop('scoped_session', None)
    g.pop("db", None)
    if scoped_session is not None:
        # the remove function rollsback
        # then calls the close function on the session of the registry
        # >>> some_session = scoped_session()
        # >>> scoped_session.remove()
        # >>> new_session = scoped_session()
        # >>> some_session is new_session
        # >>> False
        scoped_session.remove()


def init_app(app: Flask):
    # register the close_db with the removal of the app context event
    app.teardown_appcontext(close_db)
    # init_base is used to initialise the global SQLAlchemy
    init_base(app)


def init_db(app):
    base.create_all()
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
