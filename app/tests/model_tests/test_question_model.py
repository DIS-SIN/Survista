"""
Surveys have questions which is why we have the QuestionsModel. You will
however see that we implemented a many to many relationship between
surveys and questions. This is because a question can also be a part of
many surveys. This allows us to relate the answers of questions accross
the many surveys which it is a part of. Questions in different language
are considered different however there is the ability to relate questions
together
"""

import pytest
from src import create_app
import os
os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2:" + \
    "//postgres:password@" + \
    "localhost:5432/" + \
    "survista_test"


def test_create_row():

    from .utils.refresh_schema import drop_and_create
    from sqlalchemy.orm.session import make_transient
    from sqlalchemy.exc import IntegrityError

    drop_and_create()
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')

    with app.app_context():
        from src.database.db import init_db, get_db, close_db
        from sqltills import read_rows, create_rows
        init_db(app)

        # testing instatiating a QuestionModel object
        # testing inserting created QuestionModel object in db
        from src.models.question_model import QuestionModel, QuestionTypeModel
        current_sess = get_db()
        new_question = QuestionModel(slug="test_question_1",
                                     question="Test Question")
        new_question_2 = QuestionModel(slug="test_question_3",
                                       question="Test Question 3")
        q_type = read_rows(current_sess, QuestionTypeModel).first()
        new_question.questionType = q_type
        new_question_2.questionType = q_type
        create_rows(current_sess, new_question, new_question_2)

        # testing that row was actually created in db
        # we do this by closing the current session
        # testing to ensure that new session is != previous session
        # testing to see if information is the same
        # testing to ensure db populated fields are populated
        close_db()
        assert get_db() != current_sess
        current_sess = get_db()
        read_question = read_rows(current_sess, QuestionModel).first()
        assert read_question is not None
        assert read_question.id is not None
        assert read_question.addedOn is not None
        assert read_question.updatedOn is not None
        assert read_question.questionTypeId is not None
        assert read_question.question == "Test Question"
        assert read_question.slug == "test_question_1"
        assert read_question.questionTypeId == 1
        assert read_question.addedOn == read_question.updatedOn

        # testing the not null constraint for the question field
        # ensure integrity error is raised
        # ensure integrity error only raised because question is none
        no_question = QuestionModel(slug="test_question_2")
        assert no_question.question is None
        no_question.questionType = read_question.questionType
        with pytest.raises(IntegrityError):
            create_rows(current_sess, no_question)
        no_question.question = "Test Question 2"
        create_rows(current_sess, no_question)

        # testing unique constraint for the question field
        # ensure integrity error is raised
        # ensure integrity error is raised because question already exists
        same_question = QuestionModel(slug="test_question_4",
                                      question="Test Question 3")
        same_question.questionType = read_question.questionType
        with pytest.raises(IntegrityError):
            create_rows(current_sess, same_question)
        same_question.question = "Test Question 4"
        create_rows(current_sess, same_question)

        # testing not null constraint for the slug field
        # ensure integrity error is raised
        # ensure integrity error is only raisef because slug field is none
        no_slug = QuestionModel(question="Test Question 5")
        assert no_slug.slug is None
        no_slug.questionType = read_question.questionType
        with pytest.raises(IntegrityError):
            create_rows(current_sess, no_slug)
        no_slug.slug = "test_question_5"
        create_rows(current_sess, no_slug)

        # testing unique constraint for the slug field
        # ensure integrity error is raised
        # ensure integrity error is only raised because the slug already exists
        same_slug = QuestionModel(question="Test Question 6",
                                  slug="test_question_3")
        with pytest.raises(IntegrityError):
            create_rows(current_sess, same_slug)
        same_slug.slug = "test_question_6"
        create_rows(current_sess, same_slug)


def test_update_row():
    """used to test updating questions table rows"""
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from sqltills import update_rows, read_rows
        from src.models.question_model import QuestionModel

        # test updating a row in the questions table
        # test that onupdate fields are updated
        current_sess = get_db()
        test_quetion_7 = read_rows(current_sess, QuestionModel, [{
            'slug': {
                'comparitor': '==',
                'data': 'test_question_7'
            }
        }]).one_or_none()
        assert test_quetion_7 is None
        update_rows(get_db(), QuestionModel, {
            'slug': 'test_question_7'
        },
            [{
                'slug': {
                    'comparitor': '==',
                    'data': 'test_question_1'
                }
            }])
        close_db()
        assert get_db() != current_sess
        updated_row = read_rows(get_db(), QuestionModel, [{
            'slug': {
                'comparitor': '==',
                'data': 'test_question_7'
            }
        }]).one_or_none()
        assert updated_row.slug == "test_question_7"
        assert updated_row.updatedOn > updated_row.addedOn


def test_delete_row():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from sqltills import read_rows, delete_rows
        from src.models.question_model import QuestionModel

        # test deleting a row from the questions db
        current_sess = get_db()
        test_question_7 = read_rows(current_sess, QuestionModel, [{
            'slug': {
                'comparitor': '==',
                'data': 'test_question_7'
            }
        }]).one_or_none()
        assert test_question_7 is not None
        delete_rows(current_sess, QuestionModel, [{
            'slug': {
                'comparitor': '==',
                'data': 'test_question_7'
            }
        }])
        close_db()
        assert get_db() != current_sess
        current_sess = get_db()
        test_question_7 = read_rows(current_sess, QuestionModel, [{
            'slug': {
                'comparitor': '==',
                'data': 'test_question_7'
            }
        }]).one_or_none()
        assert test_question_7 is None


def test_survey_relationship_creation():
    """test the creation of a relationship between question and survey"""
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from sqlalchemy.exc import IntegrityError
        from src.database.db import get_db, close_db
        from src.models.survey_model import SurveyModel, SurveyQuestionsModel
        from src.models.question_model import QuestionModel
        from sqltills import create_rows, read_rows

        # test the creation of relationship between question and survey
        # test the many to many outside the scope of the session
        current_sess = get_db()
        survey_1 = SurveyModel(title="Test Survey 1", slug="test_survey_1")
        survey_2 = SurveyModel(title="Test Survey 2", slug="test_survey_2")
        survey_3 = SurveyModel(title="Test Survey 3", slug="test_survey_3")
        survey_4 = SurveyModel(title="Test Survey 4", slug="test_survey_4")
        test_question_7 = QuestionModel(question="Test Question 7",
                                        slug="test_question_7")
        test_question_8 = QuestionModel(question="Test Question 8",
                                        slug="test_question_8")
        test_question_9 = QuestionModel(question="Test Question 9",
                                        slug="test_question_9")
        test_question_10 = QuestionModel(question="Test Question 10",
                                         slug="test_question_10")
        test_question_7.surveys.append(survey_1)
        test_question_8.surveys.extend([survey_1, survey_2])
        test_question_9.surveys.extend([survey_1, survey_2, survey_3])
        # test unique constraint out of session scope
        test_question_10.surveys.extend([survey_4, survey_4])
        create_rows(current_sess, test_question_7, test_question_8,
                    test_question_9)
        with pytest.raises(IntegrityError):
            create_rows(current_sess, test_question_10)
        relationships = read_rows(current_sess, SurveyQuestionsModel).all()
        assert len(relationships) == 6
        current_id = 1
        for relation in relationships:
            assert relation.id is not None
            assert isinstance(relation.id, int)
            assert current_id == relation.id
            current_id += 1

        # test the composite unique constraint in session scope
        test_question_7.surveys.append(survey_1)
        with pytest.raises(IntegrityError):
            current_sess.commit()

        # test the creation of relationships between question and survey
        # test many to many inside the scope of the session
        close_db()
        assert current_sess != get_db()
        current_sess = get_db()
        questions = read_rows(current_sess, QuestionModel, filters=[{
            'slug': {
                'comparitor': '==',
                'data': 'test_question_2'
            },
            'join': 'or'
        },
            {
            'slug': {
                'comparitor': '==',
                'data': 'test_question_3'
            },
            'join': 'or'
        },
            {
            'slug': {
                'comparitor': '==',
                'data': 'test_question_4'
            }
        }
        ]).all()
        assert len(questions) == 3
        surveys = read_rows(current_sess, SurveyModel).all()
        assert len(surveys) > 1
        for question in questions:
            for survey in surveys:
                question.surveys.append(survey)
        current_sess.commit()


def test_survey_relationship_update():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from sqltills import update_rows
        from src.models.question_model import QuestionModel

        question = update_rows(get_db(), QuestionModel, {
            'id': 101
        },
            filters=[
            {
                'slug': {
                    'comparitor': '==',
                    'data': 'test_question_9'
                }
            }
        ])


def test_survey_relationship_delete():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from sqltills import delete_row_by_id, read_rows
        from src.models.question_model import QuestionModel

        # test delete outside of session scope
        delete_row_by_id(get_db(), QuestionModel, 101)

        # test delete inside of session scope
        question = read_rows(get_db(), QuestionModel, filters=[{
            'slug': {
                'comparitor': '==',
                'data': 'test_question_8'
            }
        }]).one()

        question.surveys.pop(0)
        get_db().commit()
