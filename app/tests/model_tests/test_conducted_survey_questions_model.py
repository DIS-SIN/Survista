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
        from src.database.db import init_db, get_db
        from sqltills import read_rows, create_rows
        init_db(app)

        from src.models.conducted_survey_model import (
            ConductedSurveyModel,
            ConductedSurveyQuestionModel)
        from src.models.survey_model import SurveyModel, SurveyQuestionsModel
        from src.models.question_model import QuestionModel

        current_sess = get_db()
        test_survey_1 = SurveyModel(slug="test_survey_1",
                                    title="Test Survey 1")
        test_question_1 = QuestionModel(slug="test_question_1",
                                        question="Test Question 1")
        test_survey_1.questions.append(test_question_1)
        create_rows(current_sess, test_question_1)
        survey_question_1 = read_rows(current_sess, SurveyQuestionsModel,
                                      filters=[{
                                          'surveyId': {
                                              'comparitor': '==',
                                              'data': test_survey_1.id
                                          },
                                          'join': 'and'
                                      },
                                          {
                                          'questionId': {
                                              'comparitor': '==',
                                              'data': test_question_1.id
                                          }
                                      }]).one()
        conducted_survey_1 = ConductedSurveyModel(slug="conducted_survey_1",
                                                  conductedOn=datetime(2019, 4,
                                                                       21))
        create_rows(current_sess, conducted_survey_1)
        cs_question_1 = ConductedSurveyQuestionModel(
            surveyQuestionId=survey_question_1.id,
            conductedSurveyId=conducted_survey_1.id)
        create_rows(current_sess, cs_question_1)
        assert cs_question_1.addedOn is not None

        # test not null constraint of surveyQuestionId
        cs_question_2 = ConductedSurveyQuestionModel(
            conductedSurveyId=conducted_survey_1.id)
        with pytest.raises(IntegrityError):
            create_rows(current_sess, cs_question_2)
        test_question_2 = QuestionModel(slug="test_question_2",
                                        question="Test Question 2")
        test_survey_1.questions.append(test_question_2)
        current_sess.commit()
        survey_question_2 = read_rows(current_sess, SurveyQuestionsModel,
                                      filters=[
                                          {
                                              'surveyId': {
                                                  'comparitor': '==',
                                                  'data': test_survey_1.id
                                              },
                                              'join': 'and'
                                          },
                                          {
                                              'questionId': {
                                                  'comparitor': '==',
                                                  'data': test_question_2.id
                                              }
                                          }
                                      ]).one()
        cs_question_2.surveyQuestionId = survey_question_2.id
        create_rows(current_sess, survey_question_2)

        # test not null constraint of conductedSurveyId
        cs_question_3 = ConductedSurveyQuestionModel(
            surveyQuestionId=survey_question_2.id
        )
        with pytest.raises(IntegrityError):
            create_rows(current_sess, cs_question_3)
        conducted_survey_2 = ConductedSurveyModel(
            slug="conducted_survey_2",
            conductedOn=datetime(2019, 4,
                                 21)
        )
        create_rows(current_sess, conducted_survey_2)
        cs_question_3.conductedSurveyId = conducted_survey_2.id
        create_rows(current_sess, cs_question_3)

        # test unique composite unique constraint of both cols
        cs_question_4 = ConductedSurveyQuestionModel(
            conductedSurveyId=conducted_survey_1.id,
            surveyQuestionId=survey_question_1.id
        )
        with pytest.raises(IntegrityError):
            create_rows(current_sess, cs_question_4)
        cs_question_4.conductedSurveyId = conducted_survey_2.id
        cs_question_4.surveyQuestionId = survey_question_1.id
        create_rows(current_sess, cs_question_4)
