from typing import Optional, Union, cast, List, Tuple
from src.utils.exceptions.wrapper_exceptions import NoCurrentVersionFound, VersionDoesNotBelongToNode
import src.models.survey_model as sm
import src.models.question_model as qm

from src.database.db import get_db
from datetime import datetime
from neomodel.exceptions import DoesNotExist, NeomodelException
from neomodel import NodeSet, Traversal, RelationshipManager
from neomodel.match import OUTGOING
from src.utils.marshmallow.survey_schema import SurveySchema
from src.utils.marshmallow.surveyversion_schema import SurveyVersionSchema
import model_wrappers.question_wrapper as qw

# TODO 
# Question and PreQuestion Wrappers 
# Version Comparitor functions
# Version update function
# Current Version wrapper that extends base version functionailty ?? 
class SurveyVersionWrapper:

    def __init__(self, version: Optional["sm.SurveyVersion"] = None, 
                 survey: Optional["SurveyWrapper"] = None) -> None:
        if version is not None:
            self.version = version
        if survey is not None:
            self.survey = survey
    
    @property
    def nodeId(self) -> Union[str, None]:
        if hasattr(self,'_nodeId'):
            return self._nodeId
        return None

    @property
    def title(self) -> Union[str, None]:
        if hasattr(self,'_title'):
            return self._title
        return None
    @property
    def isCurrentVersion(self) -> bool:
        return self._isCurrentVersion
    
    @property
    def version(self) -> "sm.SurveyVersion":
        return self._version
    
    @version.setter
    def version(self, version: Union["sm.SurveyVersion", str]):
        if isinstance(version, str):
            version = sm.SurveyVersion.nodes.get(nodeId=version)
        version = cast(sm.SurveyVersion, version)
        self._version = version
        self._nodeId = version.nodeId
        self._title = version.title
        self._questions = self._version.questions
        self._preQuestions = self._version.preQuestions
        self._previousVersion = self._version.previousVersion
        self._surveyNode = self._version.survey
        self._isCurrentVersion = self._version.currentVersion
    
    @property
    def questions(self) -> List["qw.QuestionWrapper"]:
        if not hasattr(self, '_version'):
           raise ValueError('No SurveyVersion has been assigned to this wrapper')
        elif isinstance(self._questions, RelationshipManager):
            questions = []
            for question in self._questions:
                wrapped_question = qw.QuestionWrapper(question)
                questions.append(wrapped_question)
            self._questions = questions
        return self._questions
    
    @property
    def preQuestions(self) -> List["qw.PreQuestionWrapper"]:
        if not hasattr(self, '_version'):
            raise ValueError('No SurveyVersion has been assigned to this wrapper')
        elif isinstance(self._preQuestions, RelationshipManager):
            preQuestions = []
            for preQuestion in self._preQuestions:
                preQuestions.append(
                    qw.PreQuestionWrapper(
                        preQuestion
                    )
                )
            self._preQuestions = preQuestions
        return self._preQuestions
    
    @property
    def surveyNode(self):
        if not hasattr(self, '_version'):
            raise ValueError('No SurveyVersion has been assigned to this wrapper')
        elif isinstance(self._survey, RelationshipManager):
            try:
                surveyNode = self._survey.single()
            except NeomodelException:
                surveyNode = None
            self._surveyNode = surveyNode
        
        return self._surveyNode

    @property
    def survey(self) -> "SurveyWrapper":
        if not hasattr(self, '_version'):
            raise ValueError('No SurveyVersion is assigned to this wrapper')
        elif not hasattr(self, '_parent_wrapper'):
            self.survey = SurveyWrapper(self.surveyNode)
        return self._survey

    @survey.setter
    def survey(self, survey: "SurveyWrapper"):
        if survey.contains_version(self._version):
            self._survey = survey
        else:
            raise ValueError(
                f"The SurveyVersion in the parent wrapper does not exist in the survey slug: {survey.slug} " +
                f"nodeId: {survey.nodeId}"
            )
    
    @property
    def previous_version(self) -> "SurveyVersionWrapper":
        if not hasattr(self, '_version'):
            raise ValueError('No SurveyVersion is assigned to this wrapper')
        elif isinstance(self._previousVersion, RelationshipManager):
            try:
                self._previousVersion =  SurveyVersionWrapper(self._previousVersion.single())
            except NeomodelException:
                self._previousVersion = None
        self._previousVersion = cast(SurveyVersionWrapper, self._previousVersion)
        return self._previousVersion
    
    def add_question(self, question: 'qm.Question', rel_props: Optional[dict] = None):
        try:
            rel = self._version.questions.connect(question, rel_props)
        except ValueError:
            question.save()
            rel = self._version.questions.connect(question, rel_props)
        rel.save()
        if isinstance(self._questions, RelationshipManager):
            self._questions = self._version.questions
        else:
            self._questions.append(qw.QuestionWrapper(question))
    
    def dump(self, exclude: Optional[List[str]] = None, only: Optional[List[str]] = None):
        if only is not None and len(only) == 1 and only[0] == 'survey':
            return self._get_survey_dump(exclude=exclude)
        elif only is not None and len(only) == 1 and only[0] == "previousVersions":
            return self._get_previous_versions_dump()
        elif only is not None and len(only) == 1 and only[0] == "questions":
            return self._get_questions_dump()
        elif only is not None and len(only) == 1 and only[0] == 'preQuestions':
            return self._get_preQuestions_dump()
        elif exclude is None and only is None:
            version_dump = SurveyVersionSchema().dump(self.version).data
            version_dump['survey'] = self._get_survey_dump(exclude=exclude)
            version_dump['previousVersions'] = self._get_previous_versions_dump()
        elif exclude is not None and only is None:
            version_dump = SurveyVersionSchema(exclude=tuple(exclude)).dump(self.version).data
            if 'survey' not in exclude:
                version_dump['survey'] = self._get_survey_dump(exclude=exclude)
            if 'previousVersions' not in exclude:
                version_dump['previousVersions'] = self._get_previous_versions_dump()
            if 'questions' not in exclude:
                version_dump['questions'] = self._get_questions_dump()
            if 'preQuestions' not in exclude:
                version_dump['preQuestions'] = self._get_preQuestions_dump()
        elif exclude is None and only is not None:
            try:
                only.remove('survey')
                survey_dump = self._get_survey_dump()
            except ValueError:
                survey_dump = None

            try:
                only.remove('previousVersions')
                previous_versions_dump = self._get_previous_versions_dump()
            except ValueError:
                previous_versions_dump = None 
            
            try:
                only.remove('questions')
                questions_dump = self._get_questions_dump()
            except ValueError:
                only.remove('preQuestions')
                preQuestions_dump = self._get_preQuestions_dump()

            version_dump = SurveyVersionSchema(only=only).dump(self.version).data
            
            if survey_dump is not None:
                version_dump['survey'] = survey_dump
            if previous_versions_dump is not None:
                version_dump['previousVersions'] = previous_versions_dump
            if questions_dump is not None:
                version_dump['questions'] = questions_dump
            if preQuestions_dump is not None:
                version_dump['preQuestions_dump'] = preQuestions_dump
                
        else:
            raise ValueError('exclude and only are mutaually exclusive')
        return version_dump
    
    def _get_survey_dump(self, exclude: Optional[List[str]] = None):
        try:
            if exclude is None:
                return self.survey.dump(exclude = ['currentVersionNode'])
            if 'currentVersionNode' not in exclude:
                exclude.append('currentVersionNode') 
            return self.survey.dump()
        except AttributeError:
            return {}
    
    def _get_questions_dump(self):
        questions = []
        if self.questions != []:
            for question in self.questions:
                questions.append(
                    question.dump(
                        exclude = [
                            'surveyVersions',
                            'preQuestions',
                            'surveys'
                        ]
                    )
                )
        return questions
    
    def _get_preQuestions_dump(self):
        preQuestions = []
        if self.preQuestions != []:
            for preQuestion in self.preQuestions:
                preQuestions.append(
                    preQuestion.dump(
                        exclude = [
                            'surveyVersions',
                            'questions',
                            'surveys'
                        ]
                    )
                )
        return preQuestions

    def _get_previous_versions_dump(self):
        return self._get_previous_versions_dump_rec([])
    
    def _get_previous_versions_dump_rec(self, dumps: list):
        if self.previous_version is None:
            return dumps    
       
        prev_version_dump = self.previous_version.dump(
            only= ['nodeId', 'title']
        )

        dumps.append(prev_version_dump)

        dumps = self.previous_version._get_previous_versions_dump_rec(dumps)

        return dumps


class CurrentSurveyVersionWrapper(SurveyVersionWrapper):
    pass         


class SurveyWrapper:
    def __init__(self, survey: Optional["sm.Survey"] = None) -> None:
        if survey is not None:
            self.survey = survey
            self.refreshed = True
        self.refreshed = False
    @property
    def slug(self) -> str:
        return self._slug
    
    @property
    def nodeId(self) -> str:
        return self._nodeId

    @property
    def survey(self) -> "sm.Survey":
        return self._survey
    
    @survey.setter
    def survey(self, survey: Union[str,"sm.Survey"]) -> None:
        if isinstance(survey, str):
            survey = sm.Survey.nodes.get(nodeId=survey)
        
        survey = cast(sm.Survey, survey)
        self._survey = survey
        self._slug = survey.slug
        self._nodeId = survey.nodeId
    
    @property
    def currentVersionNode(self) -> "sm.SurveyVersion":
        if hasattr(self, "_currentVersionNode") and self._currentVersionNode is not None:
            if self.refreshed is True:
               self.currentVersion
            return self._currentVersionNode
        self.currentVersion
        return self._currentVersionNode

    @property
    def currentVersion(self) -> CurrentSurveyVersionWrapper:
        # check if we have already assigned the private variable
        if self.refreshed == False and hasattr(self,"_currentVersion") and self._currentVersion is not None:
            return self._currentVersion
        
        # if not we try and retrieve the current version
        surveyVersion = self._survey.versions.get_or_none(currentVersion=True)
        # if we cannot get a current version we raise an error
        if surveyVersion is None:
            raise NoCurrentVersionFound(
                f"No versions of survey slug: {self._survey.slug} " +
                f"nodeId: {self._survey.nodeId} are selected as the current version"
            )
        else:
            # otherwise we call the setter and then return the private variable set as a result
           self.currentVersion = surveyVersion
           return self._currentVersion
    
    @currentVersion.setter
    def currentVersion(self, currentVersion: Union[str,"sm.SurveyVersion"] ) -> None:
        # if it is a string then this is the nodeId
        # use this to get the actual node
        if isinstance(currentVersion, str):
            currentVersion = sm.SurveyVersion.nodes.get(nodeId = currentVersion)
        currentVersion = cast("sm.SurveyVersion", currentVersion)
        
        # get the single survey node or none if the version is not attached to a survey
        currentVersionSurvey = currentVersion.survey.get_or_none()

        # assert that the survey of the SurveyVersion is none or it is the attached survey in the wrapper
        try:
            assert currentVersionSurvey is None or currentVersionSurvey == self._survey
        except AssertionError:
            raise VersionDoesNotBelongToNode("The version you are trying to attach does not belong to this survey")
        # assign the version to the private variable
        self._currentVersionNode = currentVersion

        # if the version does not have a survey then create a relationship and set currentVersion bool flag
        if currentVersionSurvey is None:
            self._survey.versions.connect(self._currentVersionNode)
        # if the currentVersion bool flag is not  true then set this to be true
       
        previous_version = self._survey.versions.get_or_none(currentVersion = True)

        if currentVersionSurvey is None and previous_version is not None\
            and len(self._currentVersionNode.previousVersion) == 0:
            self._currentVersionNode.previousVersion.connect(previous_version)

        if self._currentVersionNode.currentVersion != True:
            self._currentVersionNode.currentVersion = True
            self._currentVersionNode.save()
        
        for version in self._survey.versions:
            if version != self._currentVersionNode:
                version.currentVersion = False
                version.save()
        # finally wrap the current version in it's current version wrapper
        self._currentVersion = CurrentSurveyVersionWrapper(self._currentVersionNode, self) # type: CurrentSurveyVersionWrapper
        self.refreshed = False

    def set_survey_variables(self,**kwargs) -> None:
        for key in kwargs:
            setattr(self._survey, key, kwargs[key])
        self.save()

    def get_survey_version(
        self,
        nodeId: Optional[str] = None,
        title: Optional[str] = None
    ) -> Union["sm.SurveyVersion", None]:
        # if the nodeId is present use that to get the version node
        if nodeId is not None:
           return self._survey.versions.get(nodeId=nodeId)
        # otherwise use the title and get the first node with that title 
        elif title is not None:
            return self._survey.versions.filter(title=title).first()
        else:
            raise ValueError("You must provide wither nodeId, addedOn, or title")

    def get_survey_versions_lt_datetime(
        self,
        thershhold: datetime,
        inclusive: bool = False
    ) -> NodeSet:
        if inclusive:
            return self._survey.versions.match(addedOn__lte=thershhold)
        return self._survey.versions.match(addedOn__lt=thershhold)
    def get_survey_versions_gt_datetime(
        self,
        thershhold: datetime,
        inclusive: bool = False
    ) -> NodeSet:
        if inclusive:
           return self._survey.versions.match(addedOn__gte=thershhold)
        return self._survey.versions.match(addedOn__gt=thershhold)
    
    def get_survey_versions_between_datetime(
        self,
        thershhold_lower: datetime,
        thershhold_higher: datetime,
        thershhold_lower_inclusive: bool = True,
        thershhold_higher_inclusive: bool = False
    ) -> List[SurveyVersionWrapper]:

        query = f"MATCH (s:Survey {{nodeId: '{self._survey.nodeId}'}})-[r:SURVEY_VERSION]->(sv:SurveyVersion) " 
        if thershhold_lower_inclusive and thershhold_higher_inclusive:
            query = (
                query + f"WHERE r.addedOn >= {thershhold_lower.timestamp()} " + 
                f"AND r.addedOn <= {thershhold_higher.timestamp()} "
            )
        elif thershhold_lower_inclusive:
            query = (
                query + f"WHERE r.addedOn >= {thershhold_lower.timestamp()} " + 
                f"AND r.addedOn < {thershhold_higher.timestamp()} "
            )
        elif thershhold_higher_inclusive:
            query = (
                query + f"WHERE r.addedOn > {thershhold_lower.timestamp()} " + 
                f"AND r.addedOn <= {thershhold_higher.timestamp()} "
            )
        else:
           query = (
                query + f"WHERE r.addedOn > {thershhold_lower.timestamp()} " + 
                f"AND r.addedOn < {thershhold_higher.timestamp()} "
            )
        query = query + "RETURN sv"
        results, _ = get_db().cypher_query(query)
        versions = []
        for row in results:
            versions.append(
                SurveyVersionWrapper(sm.SurveyVersion.inflate(row[0]))
            )
        return versions
    
    def dump(self, 
             exclude: Optional[List[str]] = None,
             only: Optional[List[str]] = None,
             customSchema: Optional[SurveySchema] = None) -> dict:

        if only is not None and len(only) == 1 and only[0] == 'currentVersionNode':
            return self._get_current_version_dump(exclude=exclude)
        elif only is not None and len(only) == 1 and only[0] == "versions":
            return self._get_versions_dump()
        elif exclude is None and only is None:
            survey_dump = SurveySchema().dump(self.survey).data
            versions = self._get_versions_dump()
            currentVersionNode = self._get_current_version_dump()
            survey_dump['currentVersionNode'] = currentVersionNode
            survey_dump['versions'] = versions
        elif exclude is not None and only is None:
            survey_dump = SurveySchema(exclude=tuple(exclude)).dump(self.survey).data
            if 'currentVersionNode' not in exclude:
                survey_dump['currentVersionNode'] = self._get_current_version_dump()
            if 'versions' not in exclude:
                survey_dump['versions'] = self._get_versions_dump()
        elif only is not None and exclude is None:
            original_only = only
            if 'currentVersionNode' in only:
                only.remove('currentVersionNode')
            if 'versions' in only:
                only.remove('versions')
            survey_dump = SurveySchema(only=tuple(only)).dump(self.survey).data
            if 'currentVersionNode' in original_only:
                survey_dump['currentVersionNode'] = self._get_current_version_dump()
            if 'versions' in original_only:
                survey_dump['versions'] = self._get_versions_dump()
        else:
            raise ValueError('exclude and only arguments are mutually exclusive')
        return survey_dump

    def _get_current_version_dump(self, 
                                  exclude : Optional[List[str]] = None) -> dict:
        try:
            if exclude is None:
                return self.currentVersion.dump(exclude=['survey'])
            elif 'survey' not in exclude:
                exclude.append('survey')
            return self.currentVersion.dump(exclude=exclude)
        except NoCurrentVersionFound:
            return {}
    
    def _get_versions_dump(self):
        versions = []
        for version in self.survey.versions:
            versions.append(
                SurveyVersionWrapper(version).dump(only=['nodeId'])
            )
        return versions

    def contains_version(self, version: "sm.SurveyVersion") -> bool:
        return version in self.survey.versions

    def save(self) -> None:
        self._survey.save()

