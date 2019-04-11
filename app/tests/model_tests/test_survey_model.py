
import pytest
from src import create_app


def test_create_row():
    """test the creation of the row in the surveys table"""

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

        from src.database.db import init_db
        init_db(app)
        from src.models.survey_model import SurveyModel

        # instantiating a new SurveModel rows with data
        # Using constructor arguments
        new_model = SurveyModel(title="TestSurvey1", slug="test_survey_1",
                                language='en')

        # creating the row on the database
        from sqltills import create_rows
        from src.database.db import get_db
        create_rows(get_db(), new_model)

        old_session = get_db()
        # closing the session using the close_db method
        from src.database.db import close_db
        close_db()
        # test to see that the new session
        # is not the same as the closed session
        assert old_session != get_db()

        # testing reading of the data from created row in the database
        from sqltills import read_rows
        row = read_rows(get_db(), SurveyModel).one()
        assert row.title == "TestSurvey1"
        assert row.slug == "test_survey_1"
        assert row.language == "en"
        assert row.addedOn == row.updatedOn

        # transitioning the initially created instance to the transient state
        make_transient(new_model)

        # checking to ensure defined constraints are honoured
        with pytest.raises(IntegrityError):
            create_rows(get_db(), new_model)

        # testing to ensure constraints work properly
        new_model.slug = "test_survey_2"
        new_model.title = "TestSurvey1"
        create_rows(get_db(), new_model)


def test_delete_row():

    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')
    with app.app_context():
        from src.models.survey_model import SurveyModel
        from src.database.db import get_db
        from sqltills import delete_rows, read_rows

        res = read_rows(get_db(), SurveyModel, filters=[{
            'slug': {
                'comparitor': '==',
                'data': 'test_survey_2'
            }
        }]).one_or_none()

        assert res is not None

        delete_rows(get_db(), SurveyModel, filters=[{
            'slug': {
                'comparitor': '==',
                'data': 'test_survey_2'
            }
        }])

        res = read_rows(get_db(), SurveyModel, filters=[{
            'slug': {
                'comparitor': '==',
                'data': 'test_survey_2'
            }
        }]).one_or_none()

        assert res is None


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
