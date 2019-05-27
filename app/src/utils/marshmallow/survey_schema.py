
from marshmallow import Schema, post_dump
from marshmallow.fields import DateTime, Str, Boolean, Nested

class SurveySchema(Schema):
    nodeId = Str()
    slug = Str()
    language = Str()
    randomize = Boolean()
    addedOn = DateTime()  


