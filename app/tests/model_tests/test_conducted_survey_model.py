from datetime import datetime
import pytest
from src import create_app
from sqlalchemy.exc import IntegrityError
import os
os.environ['SURVISTA_SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2:" + \
    "//postgres:password@" + \
    "localhost:5432/" + \
    "survista_test"


def test_create_row():
    from .utils.refresh_schema import drop_and_create

    drop_and_create()
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import init_db, get_db, close_db
        init_db(app)

        from src.models.conducted_survey_model import ConductedSurveyModel
        from sqltills import create_rows, read_rows

        # testing instatiation of ConductedSurveyModel row
        conducted_survey_1 = ConductedSurveyModel(slug="conducted_survey_1",
                                                  conductedOn=datetime(2019, 4,
                                                                       21, 15,
                                                                       2))
        # testing the insertion of the ConductedSurveyModel row
        current_sess = get_db()
        create_rows(current_sess, conducted_survey_1)
        assert conducted_survey_1.id is not None
        assert conducted_survey_1.slug is not None
        assert conducted_survey_1.addedOn is not None
        assert conducted_survey_1.updatedOn is not None
        assert conducted_survey_1.conductedOn is not None
        assert conducted_survey_1.addedOn == conducted_survey_1.updatedOn
        close_db()

        # ensure that the row is actually created
        assert current_sess != get_db()
        current_sess = get_db()
        conducted_survey_row = read_rows(current_sess, ConductedSurveyModel,
                                         filters=[
                                             {
                                                 'slug': {
                                                     'comparitor':
                                                     '==',
                                                     'data':
                                                     'conducted_survey_1'
                                                 }
                                             }
                                         ]).one()
        assert conducted_survey_row.id is not None
        assert conducted_survey_row.slug == "conducted_survey_1"
        assert conducted_survey_row.conductedOn == datetime(2019, 4, 21, 15, 2)

        # test slug not null constraint
        # ensure integrity error is raised
        # ensure that intergrity error is raised bacause of null slug
        conducted_survey_2 = ConductedSurveyModel(conductedOn=datetime(2019, 4,
                                                                       21, 15,
                                                                       2))
        with pytest.raises(IntegrityError):
            create_rows(current_sess, conducted_survey_2)

        conducted_survey_2.slug = "conducted_survey_2"
        create_rows(current_sess, conducted_survey_2)

        # test slug unique constraint
        # ensure integrity error is raised
        # ensure integrity error is raised because slug is not unique
        conducted_survey_3 = ConductedSurveyModel(slug='conducted_survey_2',
                                                  conductedOn=datetime(2019, 4,
                                                                       21, 15,
                                                                       2))
        assert conducted_survey_3.slug is not None
        with pytest.raises(IntegrityError):
            create_rows(current_sess, conducted_survey_3)
        conducted_survey_3.slug = "conducted_survey_3"
        create_rows(current_sess, conducted_survey_3)


def test_update_row():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db
        from src.models.conducted_survey_model import ConductedSurveyModel
        from sqltills import update_rows, read_rows

        update_rows(get_db(), ConductedSurveyModel, {
            'slug': 'conducted_survey_101'
        },
            [{
                'slug': {
                    'comparitor': '==',
                    'data': 'conducted_survey_3'
                }
            }])

        update_row = read_rows(get_db(), ConductedSurveyModel, filters=[
            {
                'slug': {
                    'comparitor': '==',
                    'data': 'conducted_survey_101'
                }
            }
        ]).one()

        assert update_row.updatedOn > update_row.addedOn


def test_delete_row():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from sqltills import delete_rows, read_rows
        from src.models.conducted_survey_model import ConductedSurveyModel

        # test deleting a row outside of the session scope
        # ensure what we are deleting is actually there
        current_sess = get_db()
        conducted_survey = read_rows(current_sess, ConductedSurveyModel,
                                     filters=[{
                                         'slug': {
                                             'comparitor': '==',
                                             'data': 'conducted_survey_101'
                                         }
                                     }]).one_or_none()
        assert conducted_survey is not None
        close_db()
        assert get_db() != current_sess
        current_sess = get_db()
        delete_rows(current_sess, ConductedSurveyModel, filters=[{
            'slug': {
                'comparitor': '==',
                'data': 'conducted_survey_101'
            }
        }])
        close_db()
        assert get_db() != current_sess
        current_sess = get_db()
        conducted_survey = read_rows(current_sess, ConductedSurveyModel,
                                     filters=[{
                                         'slug': {
                                             'comparitor': '==',
                                             'data': 'conducted_survey_101'
                                         }
                                     }]).one_or_none()
        assert conducted_survey is None


def test_create_survey_relationship():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from src.models.survey_model import SurveyModel
        from src.models.conducted_survey_model import ConductedSurveyModel
        from sqltills import create_rows, read_rows

        # test the creation of the relationship outside of session scope
        current_sess = get_db()
        test_survey_1 = SurveyModel(title="Test Survey 1", slug="test_survey")
        conducted_survey_3 = ConductedSurveyModel(slug="conducted_survey_3",
                                                  conductedOn=datetime(2019, 4,
                                                                       21))
        conducted_survey_3.survey = test_survey_1
        create_rows(current_sess, conducted_survey_3)
        assert conducted_survey_3.surveyId is not None
        assert test_survey_1.conductedSurveys[0].id == conducted_survey_3.id

        # test the creation of the relationship inside of session scope
        conducted_survey_2 = read_rows(current_sess, ConductedSurveyModel,
                                       filters=[{
                                           'slug': {
                                               'comparitor': '==',
                                               'data': 'conducted_survey_2'
                                           }
                                       }]).one()
        conducted_survey_2.survey = test_survey_1
        current_sess.commit()
        assert conducted_survey_2.surveyId is not None
        assert test_survey_1.conductedSurveys[1].id == conducted_survey_2.id


def test_update_survey_relationship():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from src.models.survey_model import SurveyModel
        from src.models.conducted_survey_model import ConductedSurveyModel
        from sqltills import read_rows, update_rows

        # test update relationship outside session scope
        current_sess = get_db()
        update_rows(current_sess, SurveyModel,
                    {'id': '101'},
                    filters=[{
                        'slug': {
                            'comparitor': '==',
                            'data': 'test_survey'
                        }
                    }])
        conducted_surveys = read_rows(current_sess, ConductedSurveyModel,
                                      filters=[{
                                          'slug': {
                                              'comparitor': '==',
                                              'data': 'conducted_survey_2'
                                          },
                                          'join': 'or'
                                      },
                                          {
                                          'slug': {
                                              'comparitor': '==',
                                              'data': 'conducted_survey_3'
                                          }
                                      }]).all()
        for row in conducted_surveys:
            assert row.surveyId == 101

        close_db()
        assert current_sess != get_db()
        current_sess = get_db()

        # test update row within session scope
        survey = read_rows(current_sess, SurveyModel,
                           filters=[{
                               'slug': {
                                   'comparitor': '==',
                                   'data': 'test_survey'
                               }
                           }]).one()
        conducted_survey_2 = read_rows(current_sess, ConductedSurveyModel,
                                       filters=[{
                                           'slug': {
                                               'comparitor': '==',
                                               'data': 'conducted_survey_2'
                                           }
                                       }]).one()
        conducted_survey_3 = read_rows(current_sess, ConductedSurveyModel,
                                       filters=[{
                                           'slug': {
                                               'comparitor': '==',
                                               'data': 'conducted_survey_3'
                                           }
                                       }]).one()
        survey.id = 102
        current_sess.commit()
        assert conducted_survey_2.survey.id == 102
        assert conducted_survey_3.survey.id == 102


def test_delete_survey_relationship():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from src.models.survey_model import SurveyModel
        from src.models.conducted_survey_model import ConductedSurveyModel
        from sqltills import delete_rows, read_rows

        # test delete relationship inside of session context
        current_sess = get_db()
        conducted_survey_2 = read_rows(current_sess, ConductedSurveyModel,
                                       filters=[{
                                           'slug': {
                                               'comparitor': '==',
                                               'data': 'conducted_survey_2'
                                           }
                                       }]).one()
        conducted_survey_2.survey = None
        current_sess.commit()
        assert conducted_survey_2.surveyId is None

        # test delete relationship outside of session context
        # ensure that the relationship exists before deleting
        conducted_survey_3 = read_rows(current_sess, ConductedSurveyModel,
                                       filters=[{
                                           'slug': {
                                               'comparitor':
                                               '==',
                                               'data':
                                               'conducted_survey_3'
                                           }
                                       }]).one()
        close_db()
        assert current_sess != get_db()
        current_sess = get_db()
        delete_rows(current_sess, SurveyModel, filters=[{
            'slug': {
                'comparitor': '==',
                'data': 'test_survey'
            }
        }])
        conducted_survey_3 = read_rows(current_sess, ConductedSurveyModel,
                                       filters=[
                                           {
                                               'slug': {
                                                   'comparitor': '==',
                                                   'data': 'conducted_survey_3'
                                               }
                                           }
                                       ]).one()
        assert conducted_survey_3.surveyId is None
