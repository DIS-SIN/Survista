
import pytest
from flask import Flask
import random
import string
import os
abc = set(string.ascii_letters)
numerics = set(string.digits)
special_symbols = set(string.punctuation.replace('"', '').replace("'", ''))
abns = list(abc.union(numerics.union(special_symbols)))


def test_create_app_development():
    """testing application factory in development environment"""
    from src import create_app
    # initially testing the create_app Flask app factory
    app = create_app(mode='development', static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')
    assert isinstance(app, Flask)
    assert app.static_folder == os.path.abspath('../static')
    assert app.instance_path == os.path.abspath('../instance')
    assert app.template_folder == os.path.abspath('../templates')
    assert app.config.get('SECRET_KEY') is not None
    assert app.config.get('SQLALCHEMY_DATABASE_URI') is not None

    # testing secret key setting from configs and environment var
    global abns

    secret_key = ''
    for i in range(0, 32):
        secret_key += abns[random.randint(0, len(abns) - 1)]

    os.environ['SURVISTA_SECRET_KEY'] = secret_key
    os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI'] = secret_key
    app = create_app(mode='development', static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')
    assert app.config['SECRET_KEY'] == secret_key
    assert app.config['SQLALCHEMY_DATABASE_URI'] == secret_key

    import configs.development_settings

    configs.development_settings.SECRET_KEY = None
    os.environ.pop('SURVISTA_SECRET_KEY')
    os.environ.pop('SURVISTA_SQLALCHEMY_DATABASE_URI')
    with pytest.raises(ValueError):
        app = create_app(mode='development', static_path='../static',
                         templates_path='../templates',
                         instance_path='../instance')

    configs.development_settings.SECRET_KEY = 'dev'

    # testing sqlalchemy uri setting from configs and environemnt var
    old_uri = configs.development_settings.SQLALCHEMY_DATABASE_URI

    configs.development_settings.SQLALCHEMY_DATABASE_URI = None

    with pytest.raises(ValueError):
        app = create_app(mode='development', static_path='../static',
                         templates_path='../templates',
                         instance_path='../instance')

    configs.development_settings.SQLALCHEMY_DATABASE_URI = old_uri

    # checking that errors are thrown for non existant static and templates
    # checking that instance folder is created if not exists
    with pytest.raises(FileNotFoundError):
        app = create_app(mode='development', static_path='nflwknfweknf',
                         templates_path='../templates',
                         instance_path='../instance')

    with pytest.raises(FileNotFoundError):
        app = create_app(mode='development', static_path='../static',
                         templates_path='svnsvnwknvw',
                         instance_path='../instance')

    app = create_app(mode='development', static_path='../static',
                     templates_path='../templates',
                     instance_path='../' + 'test_instance_creation')

    assert os.path.isdir('../' + 'test_instance_creation')

    os.rmdir('../' + 'test_instance_creation')


def test_create_app_production():
    """testing application factory in production environment"""
    from src import create_app
    with pytest.raises(ValueError):
        app = create_app(mode="production",
                         static_path="../static",
                         templates_path="../templates",
                         instance_path="../instance")

    secret_key = ''
    for i in range(0, 32):
        secret_key += abns[random.randint(0, len(abns) - 1)]
    os.environ['SURVISTA_SECRET_KEY'] = secret_key
    os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI'] = secret_key
    app = create_app(mode="production",
                     static_path="../static",
                     templates_path="../templates",
                     instance_path="../instance")

    os.environ.pop('SURVISTA_SECRET_KEY')
    with pytest.raises(ValueError):
        app = create_app(mode="production",
                         static_path="../static",
                         templates_path="../templates",
                         instance_path="../instance")

    os.environ['SURVISTA_SECRET_KEY'] = secret_key
    os.environ.pop('SURVISTA_SQLALCHEMY_DATABASE_URI')

    with pytest.raises(ValueError):
        app = create_app(mode="production",
                         static_path="../static",
                         templates_path="../templates",
                         instance_path="../instance")
