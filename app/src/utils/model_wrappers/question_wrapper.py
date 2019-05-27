from typing import Optional, Union, cast, List
import src.models.question_model as qm
from src.utils.marshmallow.question_schema import QuestionSchema
from src.utils.marshmallow.prequestion_schema import PreQuestionSchema
from neomodel import RelationshipManager
import model_wrappers.survey_wrapper as sw

class QuestionWrapper:

    def __init__(self, question: Optional["qm.Question"]) -> None:
        self.question = question
    
    @property
    def question(self) -> "qm.Question":
        return self._question

    @question.setter
    def question(self, question: Union[str, "qm.Question"]) -> None:

        if isinstance(question, str):
            question = qm.Question.nodes.get(nodeId=question)

        question = cast(qm.Question, question)
        self._question = question
        self._surveyVersions = question.surveyVersions
        self._nodeId = self._question.nodeId
        self._preQuestions = self._question.preQuestions
    
    @property
    def nodeId(self):
        if hasattr(self, '_nodeId'):
            return self._nodeId
    @property
    def surveyVersions(self) -> List["sw.SurveyVersionWrapper"]:
        if not hasattr(self, '_question'):
            raise ValueError('Question has not been assigned to this wrapper')
        elif isinstance(self._surveyVersions, RelationshipManager):
            surveyVersions = []
            for version in self._surveyVersions:
                surveyVersions.append(sw.SurveyVersionWrapper(version))
            self._surveyVersions = surveyVersions
        return self._surveyVersions
    @property
    def preQuestions(self) -> List['PreQuestionWrapper']:
        if not hasattr(self, '_quetsion'):
            raise ValueError('Question has not been assigned to this wrapper')
        elif isinstance(self._preQuestions,RelationshipManager):
            preQuestions = []
            for preQuestion in self._preQuestions:
                preQuestions.append(
                    PreQuestionWrapper(preQuestion)
                )
            self._preQuestions = preQuestions
        return self._preQuestions
    
    def set_question_by_question(self, question: str) -> bool:
        questionNode = qm.Question.nodes.get_or_none(
            question = question
        )
        if questionNode is None:
            return False
        else:
            self.question = questionNode
            return True
    
    def dump(self, exclude: Optional[List[str]] = None, 
             only: Optional[List[str]] = None ) -> Union[dict, list]:
        if only is not None and len(only) == 1 and only[0] == 'surveys':
            return self._get_surveys_dump()
        elif only is not None and len(only) == 1 and only[0] == "preQuestions":
            return self._get_preQuestions_dump()
        elif only is not None and len(only) == 1 and only[0]  == "surveyVersions":
            return self._get_surveyVersions_dump()
        elif exclude is not None and only is None:
            questions_dump = QuestionSchema(exclude=tuple(exclude)).dump(self.question).data
            if 'surveys' not in exclude:
                questions_dump['surveys'] = self._get_surveys_dump()
            if 'surveyVersions' not in exclude:
                questions_dump['surveyVersions'] = self._get_surveyVersions_dump()
            if 'preQuestions' not in exclude:
                questions_dump['preQuestions'] = self._get_preQuestions_dump()
        elif only is not None and exclude is None:
            try:
                only.remove('surveys')
                surveys_dump = self._get_surveys_dump()
            except ValueError:
                surveys_dump = None
            try:
                only.remove('surveyVersions')
                surveyVersions_dump = self._get_surveyVersions_dump()
            except ValueError:
                surveyVersions_dump = None
            try:
                only.remove('preQuestions')
                preQuestions_dump = self._get_preQuestions_dump()
            except ValueError:
                preQuestions_dump = None
            questions_dump = QuestionSchema(exclude=tuple(only)).dump(self.question).data
            if surveys_dump is not None:
                questions_dump['surveys'] = surveys_dump
            if surveyVersions_dump is not None:
                questions_dump['surveyVersions'] = surveyVersions_dump
            if preQuestions_dump is not None:
                questions_dump['preQuestions'] = preQuestions_dump
        else:
            raise ValueError('only and exclude are mutually exclusive')
        return questions_dump
    def _get_surveys_dump(self):
        surveyRegistry = {}
        if self.surveyVersions != []:
            for version in self.surveyVersions:
                sv = surveyRegistry.get(version.survey.nodeId)
                if sv is None:
                    surveyRegistry[version.survey.nodeId] = version.survey  

        if self.preQuestions != []:
            for prequestion in self.preQuestions:
                for version in prequestion.surveyVersions:
                    sv = surveyRegistry.get(version.survey.nodeId)
                if sv is None:
                    surveyRegistry[version.survey.nodeId] = version.survey
        
        surveys = []
        if bool(surveyRegistry) is not False:
            for survey in surveyRegistry.values():
                surveys.append(survey.dump(
                    only=['nodeId', 'title', 'language', 'addedOn']
                )
            )
        return surveys
    
    def _get_surveyVersions_dump(self):
        surveyVersions = []
        if self.surveyVersions != []:
            for version in self.surveyVersions:
                surveyVersions.append(
                    version.dump( exclude = [
                        'questions',
                        'preQuestions',
                        'previousVersions'
                    ])
                )
        if self.preQuestions != []:
            for preQuestion in self.preQuestions:
                surveyVersions.extend(
                    preQuestion.dump(only=['surveyVersions'])
                )

    def _get_preQuestions_dump(self):
        preQuestions = []
        if self.preQuestions != []:
            for preQuestion in self.preQuestions:
                preQuestions.append(
                    preQuestion.dump(
                        exclude = [
                            'surveys',
                            'surveyVersions',
                            'questions'
                        ]
                    )
                )
        return preQuestions


class PreQuestionWrapper:

    def __init__(self, preQuestion: Optional['qm.PreQuestion']) -> None:
        self.preQuestion = preQuestion

    @property
    def preQuestion(self) -> "qm.PreQuestion":
        return self._preQuestion

    @preQuestion.setter
    def preQuestion(self, preQuestion: Union[str, 'qm.PreQuestion']) -> None:
        if isinstance(preQuestion, str):
            preQuestion =  qm.PreQuestion.nodes.get(nodeId = preQuestion)
        preQuestion = cast(qm.PreQuestion, preQuestion)
        self._preQuestion = preQuestion
        self._nodeId = self._preQuestion.nodeId
        self._questions = self._preQuestion.questions
        self._surveyVersions = self._preQuestion.surveyVersions

    @property
    def nodeId(self):
        if hasattr(self, '_nodeId'):
            return self._nodeId
    
    @property
    def questions(self) -> List[QuestionWrapper]:
        if not hasattr(self, '_preQuestion'):
            raise ValueError('No PreQuestion assigned to this wrapper')
        elif isinstance(self._questions, RelationshipManager):
            questions = []
            for question in self._questions:
                questions.append(
                    QuestionWrapper(question)
                )
            self._questions = questions
        return self._questions
    
    @property
    def surveyVersions(self) -> List['sw.SurveyVersionWrapper']:
        if not hasattr(self, '_preQuestion'):
            raise ValueError('No PreQuestion assigned to this wrapper')
        elif isinstance(self._surveyVersions, RelationshipManager):
            surveyVersions = [] # type: List[sw.SurveyVersionWrapper]
            for version in surveyVersions:
                surveyVersions.append(
                    sw.SurveyVersionWrapper(
                        version
                    )
                )
            self._surveyVersions = surveyVersions
        return self._surveyVersions
    
    def dump(self, exclude : Optional[List[str]] = None, only = Optional[List[str]]) -> Union[dict, list]:
        if only is not None and len(only) == 1 and only[0] == 'surveys':
            return self._get_surveys_dump()
        elif only is not None and len(only) == 1 and only[0] == 'questions':
            return self._get_questions_dump()
        elif only is not None and len(only) == 1 and only[0] == "surveyVersions":
            return self._get_surveyVersions_dump()
        elif exclude is not None and only is None:
            prequestion_dump = PreQuestionSchema(exclude=tuple(exclude)).dump(self.preQuestion).data
            if 'surveys' not in exclude:
                prequestion_dump['surveys'] = self._get_surveys_dump()
            if 'questions' not in exclude:
                prequestion_dump['questions'] = self._get_questions_dump()
            if 'surveyVersions' not in exclude:
                prequestion_dump['surveyVersions'] = self._get_surveyVersions_dump()
        elif exclude is None and only is not None:
            try:
                only.remove('surveys')
                survey_dump = self._get_surveys_dump()
            except ValueError:
                survey_dump = None
            try:
                only.remove('questions')
                questions_dump = self._get_questions_dump()
            except ValueError:
                questions_dump = None
            try:
                only.remove('surveyVersions')
                surveyVersions_dump = self._get_surveyVersions_dump()
            except:
                surveyVersions_dump = None
            prequestion_dump = PreQuestionSchema(only = tuple(only)).dump(self.preQuestion).data
            if survey_dump is not None:
                prequestion_dump['surveys'] = survey_dump
            if questions_dump is not None:
                prequestion_dump['questions'] = questions_dump
            if surveyVersions_dump is not None:
                prequestion_dump['surveyVersions'] = surveyVersions_dump
        else:
            raise ValueError('exclude and only are mutually exclusive arguments')
        return prequestion_dump
    
    def _get_surveys_dump(self):
        surveyRegistry = {}
        if self.surveyVersions != []:
            for version in self.surveyVersions:
                sv = surveyRegistry.get(version.survey.nodeId)
                if sv is None:
                    surveyRegistry[version.survey.nodeId] = version.survey
        
        surveys = []
        if bool(surveyRegistry) is not False:
            for survey in surveyRegistry.values():
                surveys.append(
                    survey.dump(only = ['nodeId', 'title', 'language', 'addedOn'])
                )
        
        return surveys
    def _get_questions_dump(self):
        questions = []
        if self.questions != []:
            for question in self.questions:
                questions.append(
                    question.dump(
                        exclude= [
                            'surveyVersions',
                            'surveys',
                            'preQuestions'
                        ]
                    )
                )
        return questions
    
    def _get_surveyVersions_dump(self):
        surveyVersions = []
        if self.surveyVersions != []:
            for version in self.surveyVersions:
                surveyVersions.append(
                    version.dump(
                        exclude = [
                            'survey',
                            'questions',
                            'preQuestions',
                            'previousVersions'
                        ]
                    )
                )
        return surveyVersions 








        


    