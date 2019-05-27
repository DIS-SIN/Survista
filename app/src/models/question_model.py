from neomodel.contrib import StructuredNode
from neomodel import (
    UniqueIdProperty,
    StringProperty,
    DateTimeProperty,
    BooleanProperty,
    ArrayProperty,
    Relationship,
    RelationshipFrom,
    RelationshipTo
)
from datetime import datetime

from .relationships.question_relationships import (
    Question_Question_Rel,
    PreQuestion_PreQuestion_Rel
)

class Question(StructuredNode):
    nodeId = UniqueIdProperty()
    slug = StringProperty(unique_index=True)
    language = StringProperty(required=True, choices={
                              'en': 'English',
                              'fr': 'French'
                            }
                        )
    question = StringProperty(unique_index=True)
    addedOn = DateTimeProperty(default_now=True)
    options = ArrayProperty(base_property= StringProperty())
    type = StringProperty(
        choices={
            'text': 'text',
            'mcq': 'mcq',
            'dropdown': 'dropdown'
        }
    )
    related_questions = Relationship(
        'Question',
        'RELATED_QUESTION',
        model= Question_Question_Rel
    )
    preQuestions = RelationshipFrom(
        'PreQuestion',
        'PREQUESTION_QUESTION'
    )
    surveyVersions = RelationshipFrom(
        ".survey_model.SurveyVersion",
        "SURVEY_QUESTION"
    )

class PreQuestion(StructuredNode):
    nodeId = UniqueIdProperty()
    slug = StringProperty(unique_index=True)
    language = StringProperty(required=True, choices={
        'en': 'English',
        'fr': 'French'
      }
    )
    text = StringProperty(required=True)
    randomize = BooleanProperty(default=False)
    addedOn = DateTimeProperty(default_now=True)
    related_prequestions = Relationship(
        'PreQuestion',
        'RELATED_PREQUESTION',
        model= PreQuestion_PreQuestion_Rel
    )
    questions = RelationshipTo(
        Question,
        'PREQUESTION_QUESTION'
    )
    surveyVersions = RelationshipFrom(
        '.survey_model.SurveyVersion',
        'SURVEY_PREQUESTION'
    )


