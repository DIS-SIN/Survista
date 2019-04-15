"""
The role of the ConductedSurveyQuestionModel id to link the
conducted survey (ConductedSurveyModel) and the actual survey
questions (SurveyQuestionsModel). This may seem weird in that we
are essentially building a relationship between the association table
of the many to many relationship between the surveys (SurveyModel) and
the questions (QuestionModel). The reason we are doing this is to allow
for an aggregate view and a granular view of the survey as well as being
able to track the changes to a survey over time. We have are able to see
any question that has ever been put on a survey but we can also focus on
the questions that have been on the survey at a specific time.

This test suit is also different in that I am considering this association
table as a normal table rather than just writing relationship tests in the
test_conducted_survey_model test suite. The reason for this is that this
association is the crux to the whole database so I am considering it as a
seperate entity.
"""

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
    """
    Test instatiating a ConductedSurveyQuestionModel object.
    This is equivalent to a row on the conducted_survey_questions
    table. 
    """
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

        # test creation of the row through relationships
        """
        I want to be able to fill the foriegn key columns
        through passing the instatiated SurveyQuestionModel
        and the ConductedSurveyModel objects as arguments
        in the constructor of the ConductedSurveyQuestionModel.

        This should be accomplished through instatiating relationships
        """


def test_update_row():
    app = create_app(mode="development",
                     static_path='../static',
                     instance_path='../instance',
                     templates_path='../templates')
    with app.app_context():
        from src.database.db import get_db, close_db
        from sqltills import update_rows, read_rows
        from src.models.survey_model import SurveyQuestionsModel
        from src.models.question_model import QuestionModel
        from src.models.conducted_survey_model import (
            ConductedSurveyQuestionModel,
            ConductedSurveyModel
        )

        # test updating the row outside of the session context
