
from marshmallow import Schema
from marshmallow.fields import (
    DateTime, Str, Bool
)

class PreQuestionSchema(Schema):
    nodeId = Str()
    slug = Str()
    langauge = Str()
    text = Str()
    randomize = Bool()
    addedOn = DateTime()