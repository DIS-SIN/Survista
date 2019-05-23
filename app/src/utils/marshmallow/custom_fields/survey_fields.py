
from marshmallow.fields import Field
from neomodel.contrib import SemiStructuredNode
from src.utils.marshmallow.surveyversion_schema import SurveyVersionSchema
class CurrentVersion(Field):
    def _serialize(self, value, attr, obj: SemiStructuredNode):
        version = obj.versions.get_or_none(currentVersion=True)
        if version is None:
            return None
        else:
            return SurveyVersionSchema(exclude=('currentVersion', )).dump(version).data


        