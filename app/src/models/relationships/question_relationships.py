from neomodel import StructuredRel, DateTimeProperty, StringProperty


class Question_Question_Rel(StructuredRel):
    reason = StringProperty(choices={
        'language': 'language',
        'similar': 'similar'
    })
    addedOn = DateTimeProperty(default_now=True)

class PreQuestion_PreQuestion_Rel(StructuredRel):
    reason = StringProperty(choices= {
        'language': 'language',
        'similar': 'similar'
     }
    )
    addedOn = DateTimeProperty(default_now=True)

class PreQuestion_Question_Rel(StructuredRel):
    addedOn = DateTimeProperty(default_now=True)
    