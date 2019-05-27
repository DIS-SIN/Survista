from flask_restful import Resource, reqparse
from src.models.survey_model import Survey
from src.utils.model_wrappers.survey_wrapper import SurveyWrapper
from src.database.db import get_db
from neomodel.exception import DoesNotExist, NeomodelException
parser = reqparse.RequestParser()
parser.add_argument(
   'language', type = str, 
    choices = ('en', 'fr'),
    help = "Bad choice must chose 'en' or 'fr': {error_msg}"
)

class SurveyResource(Resource):
    def get(self, nodeId = None, slug = None):
        args = parser.parse_args()
        if nodeId is not None:
            with get_db().read_transaction:
                try:
                    survey = Survey.nodes.get(
                        nodeId = nodeId
                    )
                except DoesNotExist:
                    return {
                        "message": f"The survey with nodeId {nodeId} could not be found"
                        }, 400
                except NeomodelException as e:
                    return {
                        "message": f"An internal error has occured: { repr(e) }"
                    }, 500
        elif slug is not None:
            with get_db().read_transaction:
                try:
                    survey = Survey.nodes.get(
                        slug = slug
                    )
                except DoesNotExist:
                    return {
                        "message": f"The survey with nodeId {slug} could not be found"
                        }, 400
                except NeomodelException as e:
                    return {
                        "message": f"An internal error has occured: { repr(e) }"
                    }, 500
        elif nodeId is None and slug is None:
            with get_db().read_transaction:
                if args.get('language') is not None:
                    surveys = Survey.nodes.filter(language = args.get('language')).all()
                else:
                    surveys = Survey.nodes.all()
                survey_dump = []
                try:
                    for survey in surveys:
                        survey_dump.append(
                            SurveyWrapper(survey).dump()
                    )
                    return survey_dump, 200
                except Exception as e:
                    return {
                        "message": f"An internal error has occured { repr(e)}"
                    }, 500
   
        try:
            survey_dump = SurveyWrapper(survey).dump()
            return survey_dump, 200
        except Exception as e:
            return {
                "message": ("The survey requested could not be serialized " +
                    f"with the following error: {repr(e)} ")
            }, 500
            

