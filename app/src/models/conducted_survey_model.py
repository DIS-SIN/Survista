from neomodel.contrib import SemiStructuredNode
from neomodel import(
    StringProperty,
    UniqueIdProperty,
    IntegerProperty,
    DateTimeProperty,
    FloatProperty
)
import datetime


class ConductedSurvey(SemiStructuredNode):

    conductedSurveyId = UniqueIdProperty()
    slug = StringProperty(unique_index=True)
    title = StringProperty(required=True)
    addedOn = DateTimeProperty(default_now=True)
    completedOn = DateTimeProperty(required=True)
    updatedOn = DateTimeProperty(default_now=True)
    respondentId = StringProperty(required=True)
    token = StringProperty(required=True, unique_index=True)
    status = StringProperty(
                            default="active", 
                            choices={
                                "closed": "closed",
                                "active": "active",
                                "abandoned": "abandoned"
                                }
                            )
    sentimentScore = FloatProperty()
    magnitudeScore = FloatProperty()

    def pre_save(self):
        self.updatedOn = datetime.datetime.utcnow()
        if self.sentimentScore is None and self.magnitudeScore is None:
            self.sentimentCalculated = False
        self.sentimentScore = self.sentimentScore or 0
        self.magnitudeScore = self.sentimentScore or 0
