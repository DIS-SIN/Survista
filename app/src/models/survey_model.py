from neomodel.contrib import SemiStructuredNode
from neomodel import(
    StructuredRel,
    StringProperty,
    UniqueIdProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty,
    RelationshipTo,
    RelationshipFrom,
    One,
    OneOrMore
)
from datetime import datetime
import pytz

class Survey_SurveyVersion_Rel(StructuredRel):
    addedOn = DateTimeProperty(default_now=True)

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


class SurveyVersion(SemiStructuredNode):

    nodeId = UniqueIdProperty()
    title = StringProperty(required=True)
    currentVersion = BooleanProperty(default=False)
    survey = RelationshipFrom(
        'Survey',
        'SURVEY_VERSION',
        model=Survey_SurveyVersion_Rel,
        cardinality=One
    )