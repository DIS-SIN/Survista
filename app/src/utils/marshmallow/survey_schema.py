
from marshmallow import Schema
from marshmallow.fields import DateTime, Str, Boolean

class SurveySchema(Schema):
    nodeId = Str()
    slug = Str()
    language = Str()
    randomize = Boolean()
    addedOn = DateTime()
