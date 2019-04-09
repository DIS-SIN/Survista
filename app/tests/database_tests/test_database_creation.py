
import os
import psycopg2


def test_application_database_initialisation():
    """testing initialising the application initialisation"""
    from src import create_app
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')

    from src.models.base_model import base
    with app.app_context():
        assert base.get_app() == app
        from src.models.question_model import QuestionModel, QuestionTypeModel
        from src.models.survey_model import SurveyModel, SurveyQuestionsModel
        assert QuestionModel.__tablename__ in base.metadata.tables
        assert SurveyModel.__tablename__ in base.metadata.tables
        assert QuestionTypeModel.__tablename__ in base.metadata.tables
        assert SurveyQuestionsModel.__tablename__ in base.metadata.tables


def test_application_database_creation():
    """testing the initialisation of the database with the schema"""

    os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2:" + \
                                                     "//postgres:password@" + \
                                                     "localhost:5432/" + \
                                                     "survista_test"
    connection = psycopg2.connect(dbname="survista_test",
                                  user="postgres",
                                  password="password",
                                  host="127.0.0.1",
                                  port=5432)
    cur = connection.cursor()
    cur.execute("DROP SCHEMA IF EXISTS public CASCADE")
    connection.commit()
    cur.execute("CREATE SCHEMA public")
    connection.commit()

    from src import create_app
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')

    from src.models.base_model import base

    with app.app_context():
        base.create_all()

    connection = psycopg2.connect(dbname="survista_test",
                                  user="postgres",
                                  password="password",
                                  host="127.0.0.1",
                                  port=5432)

    cur.execute("SELECT table_name FROM information_schema.tables " +
                "WHERE table_type= 'BASE TABLE' " +
                "AND table_schema='public'")

    res = cur.fetchall()
    tables = [row[0] for row in res]
    assert len(tables) > 0

    cur.execute("DROP SCHEMA IF EXISTS public CASCADE")
    connection.commit()
    cur.execute("CREATE SCHEMA public")
    connection.commit()

    from src.models.question_model import QuestionModel, QuestionTypeModel
    from src.models.survey_model import SurveyModel, SurveyQuestionsModel

    assert QuestionModel.__tablename__ in tables
    assert QuestionTypeModel.__tablename__ in tables
    assert SurveyModel.__tablename__ in tables
    assert SurveyQuestionsModel.__tablename__ in tables

    cur.close()
    connection.close()


def test_application_database_creation_function():
    """testing the function used to initialise the database"""
    from src import create_app
    os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2:" + \
                                                     "//postgres:password@" + \
                                                     "localhost:5432/" + \
                                                     "survista_test"
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')

    from src.database.db import init_db

    with app.app_context():
        init_db(app)

    connection = psycopg2.connect(dbname="survista_test",
                                  user="postgres",
                                  password="password",
                                  host="127.0.0.1",
                                  port=5432)

    cur = connection.cursor()

    cur.execute("SELECT table_name FROM information_schema.tables " +
                "WHERE table_type= 'BASE TABLE' " +
                "AND table_schema='public'")

    res = cur.fetchall()
    tables = [row[0] for row in res]

    assert len(tables) > 0

    cur.execute("SELECT * FROM question_types")

    res = cur.fetchall()

    assert len(res) > 0

    cur.execute("DROP SCHEMA IF EXISTS public CASCADE")
    connection.commit()
    cur.execute("CREATE SCHEMA public")

    cur.close()
    connection.close()
