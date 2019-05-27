from marshmallow import Schema
from marshmallow.fields import DateTime, Str, Boolean, List

class QuestionSchema(Schema):
    nodeId = str()
    slug = str()
    language = str()
    addedOn = DateTime()
    type = Str()
    options = List(Str())

    
