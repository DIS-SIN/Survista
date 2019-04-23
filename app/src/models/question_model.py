from neomodel.contrib import SemiStructuredNode
from neomodel import UniqueIdProperty, StringProperty, DateTimeProperty
from datetime import datetime


class Question(SemiStructuredNode):
    questionId = UniqueIdProperty()
    question = StringProperty(required=True)
    slug = StringProperty(unique_index=True)
    language = StringProperty(required=True, choices={
                              'en': 'English', 'fr': 'French'})
    addedOn = DateTimeProperty(default_now=True)
    updatedOn = DateTimeProperty(default_now=True)

    def pre_save(self):
        self.updatedOn = datetime.utcnow()
