from neomodel.contrib import SemiStructuredNode
from neomodel import(
    StringProperty,
    UniqueIdProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty
)
from typing import Optional
from datetime import datetime
import pytz
from .utils.sentimentSetter import SentimentSetter
class ConductedSurvey(SemiStructuredNode):

    nodeId = UniqueIdProperty()
    addedOn = DateTimeProperty(default_now=True)
    updatedOn = DateTimeProperty()
    closedOn = DateTimeProperty(default_now=True)
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
        if self.updatedOn is None:
            self.updatedOn = self.addedOn
        else:
            self.updatedOn = datetime.utcnow().replace(tzinfo=pytz.utc)
        if self.sentimentSet is False:
            SentimentSetter.setSentimentVariables(self)

    def set_closedOn(self, dt: Optional[datetime] = None) -> None:
        if dt is None:
            self.closedOn = datetime.utcnow().replace(tzinfo=pytz.utc)
        else:
            self.closedOn = dt.replace(tzinfo=pytz.utc)

