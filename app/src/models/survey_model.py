from neomodel.contrib import SemiStructuredNode
from neomodel import(
    StringProperty,
    UniqueIdProperty,
    IntegerProperty,
    DateTimeProperty
)
import datetime


class Survey(SemiStructuredNode):

    surveyId = UniqueIdProperty()
    slug = StringProperty(unique_index=True)
    title = StringProperty(required=True)
    language = StringProperty(
        required=True,
        choices={'en': 'English', 'fr': 'French'})
    addedOn = DateTimeProperty(default_now=True)
    updatedOn = DateTimeProperty(default_now=True)

    def pre_save(self):
        self.updatedOn = datetime.datetime.utcnow()
