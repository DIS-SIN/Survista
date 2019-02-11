from flask_restful import Resource, Api

class V1(Resource):
    def get(self):
        info = {
            "version": "v1.0",
            "implementedOn": "11/02/2019",
            "description" : "This is the first release of the Survista api",
            "features": [
                'Sentiment and magnitude analysis on selected text, individual comment and sentence scale',
                'Filter comments by sentiment and magnitude scores',
                'Keyword extraction on selected text',
                'Word counts and sentence counts'
            ],
            "termanologies":{
                "URI": "The actual endpoint",
                "methods" : "supported HTTP methods",
                "mainSelector" : "used in the dynamic URI to select a resource",
                "possibleArguments": "arguments that can be used, when there is multiple methods arguments will be split by method",
                "inherit": "the endpoint retains all the feature of the value which is another endpoint"
            },
            "endpoints":{
                "surveys": {
                    "URI": "/surveys/<surveyId>",
                    'description': "used to access top level survey information",
                    'methods': ['GET'],
                    "mainSelector":{
                        "surveyId":{
                            "type": "int",
                            "description": "the id of the survey",       
                        },
                    },
                    'possibleArguments': {
                        "slug":{
                            "type":"str",
                            "description": "a unique slug for the survey, this is set when you upload the survey zip"
                        }
                    },
                    'possibleErrors':{
                        'surveyNotFound':{
                            "decription": "The survey requested could not be found"
                        },
                        'surveyProcessingError':{
                            "description": "The survey is currently being processed and will be available shortly"
                        }
                    },
                    'subEndpoints':[
                        "questions",
                        "slug"
                    ]
                },
                "questions":{
                            "URI" : "/surveys/<survey_id>/questions/<questionNumber>",
                            "description": "used to access questions in survey",
                            "methods" : ['GET'],
                            "mainSelector":{
                                "questionNumber":{
                                    "type":"str",
                                    "description": "the question number, this should be the question number in your index csv"
                                }
                            },
                            'possibleArguments':{
                                'withComments': {
                                    "type": "bool",
                                    "description": "Include or not include comments",
                                    "default" : True
                                },
                                'sentimentScoreMin':{
                                    "type": "numerical",
                                    "description": "minimum sentiment score thresh hold for comments",
                                    "conditions":[
                                        'value must be between -1.0 and 1.0',
                                        'if sentimentScoreMax is set sentimentScoreMax must be >= senimentScoreMin'
                                    ]
                                },
                                'sentimentScoreMax' : {
                                    "type": "numerical",
                                    "description": "maximum sentiment score thresh hold for comments",
                                    "conditions":[
                                        'value must be between -1.0 and 1.0',
                                        'if sentimentScoreMin is set sentimentScoreMax must be >= senimentScoreMin'
                                    ]

                                },
                                'magnitudeScoreMin':{
                                    "type": "numerical",
                                    "description": "minimum magnitude score thresh hold for comments",
                                    "conditions":[
                                        'value must be greater than 0',
                                        'if magnitudeScoreMax is set magnitudeScoreMax must be >= magnitudeScoreMin'
                                    ]
                                },
                                'magnitudeScoreMax':{
                                    "type": "numerical",
                                    "description": "maximum sentiment score thresh hold for comments",
                                    "conditions":[
                                        'value must be greater than 0',
                                        'if magnitudeScoreMin is set magnitudeScoreMax must be >= magnitudeScoreMin'
                                    ]
                                }

                            }
                    },
                "slug":{
                            "URI": "/surveys/slug/<slug>",
                            "description": "used to access survey by slug instead of ID",
                            "mainSelector":{
                                "slug":{
                                    "type": "string",
                                    "description": "a unique slug for the survey, this is set when you upload the survey zip"
                                }
                            },
                            "inherit": "surveys"

                    }
                }
            }
        return info