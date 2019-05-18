from typing import Optional, Union, cast
from src.utils.exceptions.wrapper_exceptions import NoCurrentVersionFound, VersionDoesNotBelongToNode
import src.models.survey_model as sm
from src.database.db import get_db
from datetime import datetime
from neomodel.exceptions import DoesNotExist
from neomodel import NodeSet
from neomodel import Traversal
from neomodel.match import OUTGOING
class SurveyWrapper:

    def __init__(self, survey: Optional["sm.Survey"] = None) -> None:
        if survey is not None:
            self.survey = survey
        self.survey_version_definition = dict(
            node_class=sm.Survey,
            direction=OUTGOING,
            relation_type="SURVEY_VERSION",
            model = sm.Survey_SurveyVersion_Rel
        )

    @property
    def survey(self) -> "sm.Survey":
        return self._survey
    
    @survey.setter
    def survey(self, survey: Union[str,"sm.Survey"]) -> None:
        if isinstance(survey, str):
            survey = sm.Survey.nodes.get(nodeId=survey)
        
        survey = cast(sm.Survey, survey)
        self._survey = survey
    
    @property
    def currentVersion(self) -> "sm.SurveyVersion":
        # check if we have already assigned the private variable
        if hasattr(self,"_currentVersion") and self._currentVersion is not None:
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
        self._currentVersion = currentVersion

        # if the version does not have a survey then create a relationship and set currentVersion bool flag
        if currentVersionSurvey is None:
            self._currentVersion.currentVersion = True
            self._currentVersion.save()
            self._survey.versions.connect(self._currentVersion)
        # if the currentVersion bool flag is not true then set this to be true
        if self._currentVersion.currentVersion != True:
            self._currentVersion.currentVersion = True
            self._currentVersion.save()
        
        for version in self._survey.versions:
            if version != self._currentVersion:
                version.currentVersion = False
                version.save()
    
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
    ) -> list:
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
            versions.append(sm.SurveyVersion.inflate(row[0]))
        return versions
    def save(self) -> None:
        self._survey.save()

    def _get_nodeSet(self, relationship) -> NodeSet:
        return NodeSet(relationship._new_traversal())



  
