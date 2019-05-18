
from neomodel import StructuredRel, DateTimeProperty, StringProperty

class Survey_SurveyVersion_Rel(StructuredRel):
    addedOn = DateTimeProperty(default_now=True)

class SurveyVersion_Question_Rel(StructuredRel):
    addedOn = DateTimeProperty(default_now=True)


class Survey_Survey_Rel(StructuredRel):
    reason = StringProperty(choices={
        'language':'language',
        'similar': 'similar',
        'shorter': 'shorter'
    })
    addedOn = DateTimeProperty(default_now=True)

class SurveyVersion_PreQuestion_Rel(StructuredRel):
    addedOn = DateTimeProperty(default_now=True)