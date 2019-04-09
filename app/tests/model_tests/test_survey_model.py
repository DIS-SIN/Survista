
import pytest
from src import create_app


def test_create_row():
    """test the creation of the row in the surveys table"""

    from .utils.refresh_schema import drop_and_create
    from sqlalchemy.orm.session import make_transient
    from sqlalchemy.exc import IntegrityError
    drop_and_create()
    app = create_app(mode='development',
                     static_path='../static',
                     templates_path='../templates',
                     instance_path='../instance')

    with app.app_context():
        from src.database.db import init_db
        init_db(app)
        from src.models.survey_model import SurveyModel
        new_model = SurveyModel(title="TestSurvey1", slug="test_survey_1",
                                language='en')
        from sqltills import create_rows
        from src.database.db import get_db
        create_rows(get_db(), new_model)
        from src.database.db import close_db
        close_db()
        from sqltills import read_rows
        row = read_rows(get_db(), SurveyModel).one()
        assert row.title == "TestSurvey1"
        assert row.slug == "test_survey_1"
        assert row.language == "en"
        assert row.addedOn == row.updatedOn

        make_transient(new_model)

        with pytest.raises(IntegrityError):
            create_rows(get_db(), new_model)

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
