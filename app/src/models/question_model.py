from neomodel.contrib import SemiStructuredNode
from neomodel import (
    UniqueIdProperty,
    StringProperty,
    DateTimeProperty,
    BooleanProperty,
    Relationship,
    RelationshipFrom,
    RelationshipTo
)
from datetime import datetime

from .relationships.survey_relationships import SurveyVersion_Question_Rel
from .relationships.question_relationships import (
    Question_Question_Rel,
    PreQuestion_PreQuestion_Rel,
    PreQuestion_Question_Rel
)

class Question(SemiStructuredNode):
    nodeId = UniqueIdProperty()
    slug = StringProperty(unique_index=True)
    language = StringProperty(required=True, choices={
                              'en': 'English',
                              'fr': 'French'
                            }
                        )
    question = StringProperty(unique_index=True)
    addedOn = DateTimeProperty(default_now=True)
    related_questions = Relationship(
        'Question',
        'RELATED_QUESTION',
        model= Question_Question_Rel
    )
    related_surveys = RelationshipFrom(
        ".survey_model.SurveyVersion",
        "SURVEY_QUESTION",
        model=SurveyVersion_Question_Rel
    )
class PreQuestion(SemiStructuredNode):
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
        'RELATED_PRE_QUESTION',
        model= PreQuestion_PreQuestion_Rel
    )
    questions = RelationshipTo(
        Question,
        'PREQUESTION_QUESTION',
        model= PreQuestion_Question_Rel
    )

