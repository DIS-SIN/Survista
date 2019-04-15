
from sqlalchemy import (Column, BigInteger, Text, DateTime,
                        text, Float, ForeignKey)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint, Sequence
from sqlalchemy.ext.associationproxy import association_proxy
from .base_model import base
from .utils.utc_convert import utcnow
from .utils.primary_key_specifier import pkeyspec, SerialId


class SurveyModel(base.Model):
    __tablename__ = "surveys"
    id = Column(BigInteger, primary_key=True)
    slug = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    addedOn = Column(DateTime,
                     server_default=utcnow())
    updatedOn = Column(DateTime,
                       server_default=utcnow(),
                       onupdate=utcnow())
    language = Column(Text)
    sentimentScore = Column('sentiment_score', Float(precision=2))
    magnitudeScore = Column('magnitude_score', Float(precision=2))
    questions = association_proxy("surveyQuestions", "question")


class SurveyQuestionsModel(base.Model):
    __tablename__ = "survey_questions"
    id = Column(BigInteger, primary_key=True)
    surveyId = Column('survey_id',
                      BigInteger,
                      ForeignKey('surveys.id', ondelete="CASCADE",
                                 onupdate="CASCADE"),
                      nullable=False)
    questionId = Column('question_id',
                        BigInteger,
                        ForeignKey('questions.id', ondelete="CASCADE",
                                   onupdate="CASCADE"),
                        nullable=False)
    addedOn = Column('added_on', DateTime, server_default=utcnow())
    survey = relationship("SurveyModel",
                          backref=backref(
                              "surveyQuestions",
                              passive_deletes=True,
                              cascade="all, delete-orphan"),
                          uselist=False)
    question = relationship("QuestionModel",
                            backref=backref(
                                "surveyQuestions",
                                passive_deletes=True,
                                cascade="all, delete-orphan"),
                            uselist=False)
    __table_args__ = (UniqueConstraint('survey_id', 'question_id',
                                       name="unique_survey_questions"),)

    def __init__(self, survey=None, question=None, **kwargs):
        super(SurveyQuestionsModel, self).__init__(**kwargs)

        if isinstance(survey, SurveyModel):
            self.survey = survey
            self.question = question
        elif survey is not None and question is not None:
            self.question = survey
            self.survey = question
        elif survey is not None:
            self.question = survey
