from sqltills import *
from datetime import datetime
"""
The role of the SurveyModel is to capture high level metadata
around a survey. This metadata includes when the survey was
first added to the database, it's language, the title ect. We
are considering french and english serveys to be different surveys,
there is the ability to relate different surveys together through the
survey_associations (SurveyAssociationsModel) mapper model between two
surveys and the survey_association_reasons (SurveyAssociationReasonsModel).
"""
import pytest
from src import create_app
import os
os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2:" + \
    "//postgres:password@" + \
    "localhost:5432/" + \
    "survista_test"


def test_create_row():
    """
    Test the creation of the row in the surveys table

    Test Criteria
    --------------
    1- status: Satisfied
      The SurveyModel object must be able to be able instatiated with
      the following attributes as arguments
          - language
          - title
          - slug
    2- status: Satisfied
      The language attribute must not be empty when adding and commiting
      the object to the database
    3- status: Satisfied
      The title attribute must not be empty when adding and commiting
      the object to the database
    4- status: Satisfied
      a- status: Satisfied
         The slug attribute must not be empty when adding and committing
         the object to the database.
      b- status: Satisfied
         The slug attribute must be unique
         from what is currently in the database. The slug should be a
         maximum of 20 characters
    5- status: Satisfied
      When added and committed to the database the id field should
      be automatically generated with the unique primary key
    6- status: Satisfied
      When added and committed to the database the addedOn field
      should be automatically generated with the date and time
      in UTC according to when it was added to the database
    """

    from .utils.refresh_schema import drop_and_create
    from sqlalchemy.orm.session import make_transient
    from sqlalchemy.exc import IntegrityError

    # resetting database
    drop_and_create()
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')

    with app.app_context():
        from src.database.db import init_db, get_db
        init_db(app)
        current_session = get_db()

        # Testing Criteria 1
        from src.models.survey_model import SurveyModel
        new_survey_1 = SurveyModel(
            slug="test_survey_1",
            language="en",
            title="Test Survey 1")
        create_rows(current_session, new_survey_1)

        # Testing Criteria 5
        assert new_survey_1.id == 1

        # Testing Criteria 6
        assert new_survey_1.addedOn is not None
        assert isinstance(new_survey_1.addedOn, datetime)
        assert new_survey_1.addedOn < datetime.utcnow()

        # Testing Criteria 2
        new_survey_2 = SurveyModel(
            slug="test_survey_2",
            title="Test Survey 2"
        )
        with pytest.raises(IntegrityError):
            create_rows(current_session, new_survey_2)
        new_survey_2.language = "fr"
        create_rows(current_session, new_survey_2)

        # Testing Criteria 3
        new_survey_3 = SurveyModel(
            slug="test_survey_3",
            language="en"
        )
        with pytest.raises(IntegrityError):
            create_rows(current_session, new_survey_3)
        new_survey_3.title = "Test Survey 3"
        create_rows(current_session, new_survey_3)

        # Testing Criteria 4 a
        new_survey_4 = SurveyModel(
            title="Test Survey 4",
            language="fr"
        )
        with pytest.raises(IntegrityError):
            create_rows(current_session, new_survey_4)
        new_survey_4.slug = "test_survey_4"
        create_rows(current_session, new_survey_4)

        # Testing Criteria 4 b
        new_survey_5 = SurveyModel(
            slug="test_survey_4",
            title="Test Survey 5",
            language="en"
        )
        with pytest.raises(IntegrityError):
            create_rows(current_session, new_survey_5)
        new_survey_5.slug = "test_survey_5"
        create_rows(current_session, new_survey_5)


def test_delete_row():
    """
    Testing deleting row from surveys table

    TESTING CRITERIA
    ----------------
    1-
       Must be able to delete a survey outside of a session
       context
    2- Must be able to delete a survey when loaded in session
       context
    """
    from sqlalchemy import inspect

    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')
    with app.app_context():
        from src.models.survey_model import SurveyModel
        from src.database.db import get_db, close_db

        # Testing Criteria 1
        current_session = get_db()
        test_survey_5 = read_rows(
            current_session,
            SurveyModel,
            filters=[
                {
                    'slug': {
                        'comparitor': '==',
                        'data': 'test_survey_5'
                    }
                }
            ]
        ).one()
        assert test_survey_5 is not None
        close_db()
        old_session = current_session
        current_session = get_db()
        assert current_session != old_session
        delete_rows(
            current_session,
            SurveyModel,
            filters=[
                {
                    'slug': {
                        'comparitor': '==',
                        'data': 'test_survey_5'
                    }
                }
            ]
        )
        test_survey_5 = read_rows(
            current_session,
            SurveyModel,
            filters=[
                {
                    'slug': {
                        'comparitor': '==',
                        'data': 'test_survey_5'
                    }
                }
            ]
        ).one_or_none()
        assert test_survey_5 is None
        # Testing Criteria 2
        test_survey_4 = read_rows(
            current_session,
            SurveyModel,
            filters=[
                {
                    'slug': {
                        'comparitor': '==',
                        'data': 'test_survey_4'
                    }
                }
            ]
        ).one()
        delete_rows(
            current_session,
            SurveyModel,
            filters=[
                {
                    'slug': {
                        'comparitor': '==',
                        'data': 'test_survey_4'
                    }
                }
            ]
        )
        assert inspect(test_survey_4).detached is True


def test_update_row():

    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')
    with app.app_context():
        from src.models.survey_model import SurveyModel
        from src.database.db import get_db, close_db
        from sqltills import read_rows, update_rows

        update_rows(get_db(), SurveyModel,
                    {'slug': 'test_survey_2', 'language': 'fr'},
                    [{
                        'slug': {
                            'comparitor': '==',
                            'data': 'test_survey_1'
                        }
                    }])

        close_db()

        res = read_rows(get_db(), SurveyModel, filters=[{
            'slug': {
                'comparitor': '==',
                'data': 'test_survey_2'
            }
        }]).one_or_none()

        assert res is not None
        assert res.updatedOn > res.addedOn


def test_question_relationship_creation():
    """test the many and many between surveys and questions"""
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')

    with app.app_context():
        from src.database.db import get_db
        from src.models.survey_model import (SurveyModel,
                                             SurveyQuestionsModel)
        from src.models.question_model import (QuestionModel,
                                               QuestionTypeModel)
        from sqltills import create_rows, read_rows, update_rows

        q_type = read_rows(get_db(), QuestionTypeModel).first()
        new_question = QuestionModel(slug="test_question_1",
                                     question="Test Question 1")
        new_question.questionType = q_type

        survey = read_rows(get_db(), SurveyModel).first()

        survey.questions.append(new_question)

        get_db().commit()


def test_question_relationship_update():
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')
    with app.app_context():
        from src.database.db import get_db
        from sqltills import update_rows, read_rows
        from src.models.survey_model import SurveyModel

        update_rows(get_db(), SurveyModel, {'id': 2}, [{
            'slug': {
                'comparitor': '==',
                'data': 'test_survey_2'
            }
        }])

        update_rows(get_db(), SurveyModel, {'id': 1}, [{
            'slug': {
                'comparitor': '==',
                'data': 'test_survey_2'
            }
        }])

        survey = read_rows(get_db(), SurveyModel).first()

        question = survey.questions[0]

        survey.id = 3

        assert question.surveys[0].id == 3
        get_db().commit()

        survey.id = 1

        get_db().commit()


def test_question_relationship_delete():
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')
    with app.app_context():
        from src.database.db import get_db
        from sqltills import read_rows, delete_rows
        from src.models.survey_model import SurveyModel, SurveyQuestionsModel

        survey = read_rows(get_db(), SurveyModel).first()

        question = survey.questions.pop(0)

        get_db().commit()

        assert read_rows(get_db(),
                         SurveyQuestionsModel).one_or_none() is None

        survey.questions.append(question)

        get_db().commit()

        assert (read_rows(get_db(), SurveyQuestionsModel).one_or_none()
                is not None)

        delete_rows(get_db(), SurveyModel)


def test_many_survey_one_question():
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')
    with app.app_context():
        from sqltills import delete_rows, read_rows, create_rows
        from src.database.db import get_db, close_db
        from src.models.question_model import QuestionModel, QuestionTypeModel
        from src.models.survey_model import SurveyModel

        # initially create the survey rows and close the session
        survey_1 = SurveyModel(title="TestSurvey1", slug="test_survey_1",
                               language='en')
        survey_2 = SurveyModel(title="TestSurvey2", slug="test_survey_2",
                               language='en')
        survey_3 = SurveyModel(title="TestSurvey3", slug="test_survey_3",
                               language='en')
        create_rows(get_db(), survey_1, survey_2, survey_3)

        question = read_rows(get_db(), QuestionModel).first()

        survey_1.questions.append(question)
        survey_2.questions.append(question)
        survey_3.questions.append(question)

        get_db().commit()

        delete_rows(get_db(), SurveyModel, [{
            'slug': {
                'comparitor': '==',
                'data': 'test_survey_1'
            }
        }])
        delete_rows(get_db(), QuestionModel)
