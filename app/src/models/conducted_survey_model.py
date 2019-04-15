from sqlalchemy import (Column, BigInteger, Text, DateTime,
                        text, Float, ForeignKey)
from sqlalchemy.orm import relationship, backref
from .base_model import base
from .utils.utc_convert import utcnow


class ConductedSurveyModel(base.Model):
    __tablename__ = "conducted_surveys"
    id = Column(BigInteger, primary_key=True)
    slug = Column(Text, nullable=False, unique=True)
    addedOn = Column('added_on', DateTime,
                     server_default=utcnow())
    updatedOn = Column('updated_on', DateTime,
                       server_default=utcnow(),
                       onupdate=utcnow())
    conductedOn = Column('conducted_on', DateTime)
    sentimentScore = Column('sentiment_score', Text)
    magnitudeScore = Column('magnitude_score', Text)
    surveyId = Column('survey_id', BigInteger,
                      ForeignKey("surveys.id",
                                 ondelete="SET NULL",
                                 onupdate="CASCADE"))
    survey = relationship("SurveyModel",
                          backref=backref('conductedSurveys',
                                          cascade="all",
                                          passive_deletes=True),
                          uselist=False)
