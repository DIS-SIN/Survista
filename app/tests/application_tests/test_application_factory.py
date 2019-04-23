
from src import create_app
import pytest
import os
import shutil
import string
import random

punct_set = set(string.punctuation)
punct_set.remove("'")
punct_set.remove('"')

chars = list(set(string.ascii_letters).union(
    set(string.digits)).union(punct_set))

random_secret_key = ''

for i in range(0, 32):
    random_secret_key += chars[random.randint(0,
                                              len(chars)-1)]


class Test_Application_Factory_Production():

    def test_production_mode(self):
        with pytest.raises(ValueError):
            app = create_app(mode="production",
                             static_path='../static',
                             templates_path='../templates',
                             instance_path='../instance')
        os.environ['SURVISTA_SECRET_KEY'] = random_secret_key
        os.environ['SURVISTA_NEOMODEL_DATABASE_URI'] = random_secret_key
        app = create_app(mode="production",
                         static_path='../static',
                         templates_path='../templates',
                         instance_path='../instance')

    def test_absolute_static_path(self):
        app = create_app(
            mode='production',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )
        assert os.path.isabs(app.static_folder) is True

    def test_setting_bad_static_path(self):
        with pytest.raises(FileNotFoundError):
            app = create_app(
                mode='production',
                static_path='../this_path_dne',
                templates_path='../templates',
                instance_path='../instance'
            )

        app = create_app(
            mode='production',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )

    def test_absolute_templates_path(self):
        app = create_app(
            mode='production',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )
        assert os.path.isabs(app.template_folder) is True

    def test_setting_bad_templates_path(self):
        with pytest.raises(FileNotFoundError):
            app = create_app(
                mode='production',
                static_path='../static',
                templates_path='../this_path_dne',
                instance_path='../instance'
            )

        app = create_app(
            mode='production',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )

    def test_absolute_instance_path(self):
        app = create_app(
            mode='production',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )

        assert os.path.isabs(app.instance_path) is True

    def test_setting_new_instance_path(self):
        app = create_app(
            mode='production',
            static_path='../static',
            templates_path='../templates',
            instance_path='../new_instance_folder'
        )

        assert os.path.isdir(app.instance_path) is True
        shutil.rmtree(app.instance_path)
        assert os.path.isdir(app.instance_path) is False

    def test_not_setting_secret_key(self):
        os.environ.pop('SURVISTA_SECRET_KEY')
        with pytest.raises(ValueError):
            app = create_app(
                mode='production',
                static_path='../static',
                templates_path='../templates',
                instance_path='../new_instance_folder'
            )
        os.environ['SURVISTA_SECRET_KEY'] = random_secret_key
        app = create_app(
            mode='production',
            static_path='../static',
            templates_path='../templates',
            instance_path='../new_instance_folder'
        )
        assert app.config['SECRET_KEY'] == random_secret_key

    def test_not_setting_database_uri(self):
        os.environ.pop('SURVISTA_NEOMODEL_DATABASE_URI')
        with pytest.raises(ValueError):
            app = create_app(
                mode='production',
                static_path='../static',
                templates_path='../templates',
                instance_path='../new_instance_folder'
            )
        os.environ['SURVISTA_NEOMODEL_DATABASE_URI'] = \
            "bolt://test:test@localhost:7687"
        app = create_app(
            mode='production',
            static_path='../static',
            templates_path='../templates',
            instance_path='../new_instance_folder'
        )
        assert app.config['NEOMODEL_DATABASE_URI'] == "bolt://test:test@localhost:7687"


class Test_Application_Factory_Development():

    def test_development_mode(self):
        app = create_app(mode="development",
                         static_path='../static',
                         templates_path='../templates',
                         instance_path='../instance')
        assert app.config['SECRET_KEY'] is not None
        assert app.config['NEOMODEL_DATABASE_URI'] is not None

    def test_absolute_static_path(self):
        app = create_app(
            mode='development',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )
        assert os.path.isabs(app.static_folder) is True

    def test_setting_bad_static_path(self):
        with pytest.raises(FileNotFoundError):
            app = create_app(
                mode='development',
                static_path='../this_path_dne',
                templates_path='../templates',
                instance_path='../instance'
            )

        app = create_app(
            mode='development',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )

    def test_absolute_templates_path(self):
        app = create_app(
            mode='development',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )
        assert os.path.isabs(app.template_folder) is True

    def test_setting_bad_templates_path(self):

        with pytest.raises(FileNotFoundError):
            app = create_app(
                mode='development',
                static_path='../static',
                templates_path='../this_path_dne',
                instance_path='../instance'
            )

        app = create_app(
            mode='development',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )

    def test_absolute_instance_path(self):
        app = create_app(
            mode='development',
            static_path='../static',
            templates_path='../templates',
            instance_path='../instance'
        )

        assert os.path.isabs(app.instance_path) is True

    def test_setting_new_instance_path(self):
        app = create_app(
            mode='development',
            static_path='../static',
            templates_path='../templates',
            instance_path='../new_instance_folder'
        )

        assert os.path.isdir(app.instance_path) is True
        shutil.rmtree(app.instance_path)
        assert os.path.isdir(app.instance_path) is False

    def test_overiding_default_secret_key(self):
        os.environ['SURVISTA_SECRET_KEY'] = random_secret_key
        app = create_app(
            mode='development',
            static_path='../static',
            templates_path='../templates',
            instance_path='../new_instance_folder'
        )
        assert app.config['SECRET_KEY'] == random_secret_key

    def test_overiding_default_database_uri(self):
        os.environ['SURVISTA_NEOMODEL_DATABASE_URI'] = \
            "bolt://test:test@localhost:7687"
        app = create_app(
            mode='development',
            static_path='../static',
            templates_path='../templates',
            instance_path='../new_instance_folder'
        )
        assert app.config['NEOMODEL_DATABASE_URI'] == "bolt://test:test@localhost:7687"
