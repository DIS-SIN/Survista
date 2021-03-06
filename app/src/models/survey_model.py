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
from .relationships.survey_relationships import Survey_Survey_Rel


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
    addedOn = DateTimeProperty(default_now=True)
    survey = RelationshipFrom(
        Survey,
        'SURVEY_VERSION',
        cardinality=One
    )
    previousVersion = RelationshipTo(
        'SurveyVersion',
        'PREVIOUS_VERSION',
        cardinality=One
    )
    questions = RelationshipTo(
        '.question_model.Question',
        "SURVEY_QUESTION"
    )
    preQuestions = RelationshipTo(
        '.question_model.PreQuestion',
        "SURVEY_PREQUESTION"
    )