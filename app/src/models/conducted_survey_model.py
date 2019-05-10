from neomodel.contrib import SemiStructuredNode
from neomodel import(
    StringProperty,
    UniqueIdProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty
)
import datetime
from .utils.sentimentSetter import SentimentSetter
class ConductedSurvey(SemiStructuredNode):

    conductedSurveyId = UniqueIdProperty()
    title = StringProperty(required=True)
    addedOn = DateTimeProperty(default_now=True)
    completedOn = DateTimeProperty(required=True)
    updatedOn = DateTimeProperty(default_now=True)
    status = StringProperty(
                            default="active", 
                            choices={
                                "closed": "closed",
                                "active": "active",
                                "abandoned": "abandoned"
                                }
                            )
    sentimentSet = BooleanProperty(default= False)
    def pre_save(self):
        self.updatedOn = datetime.datetime.utcnow()
        if self.sentimentSet is False:
            SentimentSetter.setSentimentVariables(self)
                
