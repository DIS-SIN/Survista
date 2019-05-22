from marshmallow import Schema
from marshmallow.fields import Boolean, Str, DateTime

class SurveyVersionSchema(Schema):
    nodeId = Str()
    title = Str()
    currentVersion = Boolean()


