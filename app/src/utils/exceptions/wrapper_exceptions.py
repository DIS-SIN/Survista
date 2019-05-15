
from neomodel.exceptions import DoesNotExist
class NoCurrentVersionFound(DoesNotExist):
    """
    No version node of the a particular parent node could be found
    """
    pass

class VersionDoesNotBelongToNode(AssertionError):
    """
    The version that is trying to be attached does not belong to the parent node
    """
    pass
