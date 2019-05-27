
from neomodel import ( 
    StructuredRel, 
    DateTimeProperty,
    StringProperty
)

class Survey_Survey_Rel(StructuredRel):
    reason = StringProperty(
        choices={
                    'language':'language',
                    'similar': 'similar',
                    'shorter': 'shorter'
                },
        required = True
    )
    description = StringProperty()
    addedOn = DateTimeProperty(default_now=True)
