from sqlalchemy import Column, BigInteger, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from .base_model import base
from .utils.utc_convert import utcnow


class QuestionModel(base.Model):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True)
    slug = Column(Text, nullable=False, unique=True)
    question = Column(Text, nullable=False, unique=True)
    addedOn = Column("added_on", DateTime, server_default=utcnow())
    updatedOn = Column("updated_on", DateTime,
                       server_default=utcnow(),
                       onupdate=utcnow())
    questionTypeId = Column("question_type_id", Integer,
                            ForeignKey("question_types.id",
                                       ondelete="SET NULL",
                                       onupdate="CASCADE"))
    questionType = relationship("QuestionTypeModel",
                                backref=backref("questions",
                                                passive_deletes=True,
                                                cascade="all"),
                                uselist=False)
    surveys = association_proxy("surveyQuestions", "survey")


class QuestionTypeModel(base.Model):
    __tablename__ = "question_types"

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False, unique=True)
    addedOn = Column("added_on", DateTime, server_default=utcnow())

    def __init__(self, question_type=None):
        self.type = question_type
