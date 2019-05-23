
from marshmallow import Schema, post_dump
from marshmallow.fields import DateTime, Str, Boolean, Nested
from .custom_fields.survey_fields import CurrentVersion
class SurveySchema(Schema):
    nodeId = Str()
    slug = Str()
    language = Str()
    randomize = Boolean()
    addedOn = DateTime()
    """currentVersion = CurrentVersion(attribute="versions", dump_only = True)
    versions= Nested('SurveyVersionSchema',
                      only=["nodeId"], many=True, dump_only=True)
    """        


