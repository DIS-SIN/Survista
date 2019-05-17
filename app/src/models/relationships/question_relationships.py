from neomodel import StructuredRel, DateProperty, StringProperty


class Question_Question_Rel(StructuredRel):
    reason = StringProperty(choices={
        'language': 'language',
        'similar': 'similar'
    })
