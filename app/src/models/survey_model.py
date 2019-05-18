from neomodel.contrib import SemiStructuredNode
from neomodel import(
    StringProperty,
    UniqueIdProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty,
    RelationshipTo,
    RelationshipFrom,
    Relationship,
    One,
    OneOrMore
)
from .relationships.survey_relationships import (
    Survey_Survey_Rel, 
    SurveyVersion_Question_Rel, 
    Survey_SurveyVersion_Rel,
    SurveyVersion_PreQuestion_Rel
)

from datetime import datetime
import pytz

class Survey(SemiStructuredNode):
    nodeId = UniqueIdProperty()
    slug = StringProperty(unique_index=True)
    language = StringProperty(
        required=True,
        choices={
            'en': 'English',
            'fr': 'French'
        }
    )
    addedOn = DateTimeProperty(default_now=True)
    versions = RelationshipTo(
        'SurveyVersion',
        'SURVEY_VERSION',
        model=Survey_SurveyVersion_Rel,
        cardinality=OneOrMore
    )
    related_surveys = Relationship(
        'Survey',
        "RELATED_SURVEY",
        model = Survey_Survey_Rel
    )
    randomize = BooleanProperty(
        default=True
    )


class SurveyVersion(SemiStructuredNode):

    nodeId = UniqueIdProperty()
    title = StringProperty(required=True)
    currentVersion = BooleanProperty(default=False)
    survey = RelationshipFrom(
        Survey,
        'SURVEY_VERSION',
        model=Survey_SurveyVersion_Rel,
        cardinality=One
    )
    questions = RelationshipTo(
        '.question_model.Question',
        "SURVEY_QUESTION",
        model=SurveyVersion_Question_Rel
    )
    prequestions = RelationshipTo(
        '.question_model.PreQuestion',
        "SYRVEY_PRE_QUESTION",
        model=SurveyVersion_PreQuestion_Rel
    )