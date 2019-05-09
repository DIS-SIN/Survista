from neomodel.contrib import SemiStructuredNode
from neomodel import (UniqueIdProperty, 
                      StringProperty,
                      DateTimeProperty,
                      FloatProperty,
                      BooleanProperty
                    )
from datetime import datetime
import pytz
from .utils.sentimentSetter import SentimentSetter
class Answer(SemiStructuredNode):
    nodeId = UniqueIdProperty()
    answer = StringProperty(required=True)
    addedOn = DateTimeProperty(default_now=True)
    updatedOn = DateTimeProperty(required=True)
    detectedLanguage = StringProperty(
        choices={
            'en': 'English',
            'fr': 'French',
            'NA': 'Not Detected'
            }
    )
    sentimentSet = BooleanProperty(default=False)
    sentimentCalculated = BooleanProperty(default=False)
    def pre_save(self):
        self.updatedOn = datetime.utcnow().replace(
            tzinfo=pytz.utc
        )
        if self.detectedLanguage is None:
            self.detectedLanguage = "NA"
        if self.sentimentSet is False:
            SentimentSetter.setSentimentVariables(self)
        
            

