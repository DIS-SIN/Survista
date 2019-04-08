
from sqlalchemy import (Column, BigInteger, Text, DateTime,
                        text, Float, ForeignKey)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from .base_model import base
from .utils.utc_convert import utcnow


class SurveyModel(base.Model):
    __tablename__ = "surveys"
    id = Column(BigInteger, primary_key=True)
    slug = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    addedOn = Column(DateTime,
                     server_default=utcnow())
    updatetedOn = Column(DateTime,
                         onupdate=utcnow())
    language = Column(Text)
    sentimentScore = Column('sentiment_score', Float(precision=2))
    magnitudeScore = Column('magnitude_score', Float(precision=2))
    questions = association_proxy("surveyQuestions", "question")


class SurveyQuestionsModel(base.Model):
    __tablename__ = "survey_questions"
    surveyId = Column('survey_id',
                      BigInteger,
                      ForeignKey('surveys.id', ondelete="CASCADE",
                                 onupdate="CASCADE"),
                      primary_key=True)
    questionId = Column('question_id',
                        BigInteger,
                        ForeignKey('questions.id', ondelete="CASCADE",
                                   onupdate="CASCADE"),
                        primary_key=True)
    survey = relationship("SurveyModel", backref=backref(
        "surveyQuestions", passive_deletes=True), uselist=False)
    question = relationship("QuestionModel", backref=backref(
        "surveyQuestions", passive_deletes=True), uselist=False)
