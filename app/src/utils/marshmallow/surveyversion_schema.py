from marshmallow import schema
from marshmallow.fields import Boolean, Str, DateTime

class SurveyVersionSchema(schema):
    nodeId = Str()
    title = Str()
    currentVersion = Boolean()


