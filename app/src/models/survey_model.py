from neomodel.contrib import SemiStructuredNode
from neomodel import(
    StringProperty,
    UniqueIdProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty
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


class SurveyVersion(SemiStructuredNode):

    nodeId = UniqueIdProperty()
    title = StringProperty(required=True)
    currentVersion = BooleanProperty(default=False)
    addedOn = DateTimeProperty(default_now=True)