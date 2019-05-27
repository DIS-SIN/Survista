from marshmallow import Schema
from marshmallow.fields import DateTime, Str, Boolean, Nested

class QuestionSchema(Schema):
    nodeId = str()
    slug = str()
    language = str()
    addedOn = DateTime()
    
