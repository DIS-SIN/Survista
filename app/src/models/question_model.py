from neomodel.contrib import SemiStructuredNode
from neomodel import (
    UniqueIdProperty,
    StringProperty,
    DateTimeProperty,
    BooleanProperty
)
from datetime import datetime

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
