from neomodel.contrib import SemiStructuredNode
from neomodel import (
    UniqueIdProperty,
    BooleanProperty,
    DateTimeProperty
)
from .utils.sentimentSetter import SentimentSetter

class ConductedSurveyQuestion(SemiStructuredNode):
    
    nodeId = UniqueIdProperty()
    sentimentSet = BooleanProperty(default=False)
    sentimentCalculated = BooleanProperty(default=False)
    addedOn = DateTimeProperty(default_now=True)

    def pre_save(self):
        if self.sentimentSet is False:
            SentimentSetter.setSentimentVariables(self)
        
