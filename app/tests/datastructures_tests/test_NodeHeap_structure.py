import pytest
from configs.development_settings import NEOMODEL_DATABASE_URI
from datetime import datetime
import random

from src.utils.datastructures.node_heap import NodeHeap

@pytest.fixture
def set_node_config():
    from neomodel import (
        config, StringProperty, 
        DateTimeProperty, IntegerProperty, UniqueIdProperty, 
        remove_all_labels, install_all_labels
    )
    from neomodel.contrib import SemiStructuredNode
    from neomodel.util import clear_neo4j_database
    from neomodel import db
    class SomeNode(SemiStructuredNode):
        nodeId = UniqueIdProperty()
        someDate = DateTimeProperty()

    config.DATABASE_URL = NEOMODEL_DATABASE_URI
    
    clear_neo4j_database(db)
    remove_all_labels()

    install_all_labels()

    node_array = []
    with db.transaction:
        for i in range(1,32):
            for j in range(0,24):
                dt = datetime(2019,5,i,j)
                sm = SomeNode(someDate=dt)
                sm.save()
                node_array.append(SomeNode(someDate=dt))
    
    random.shuffle(node_array)
    return node_array


class Test_NodeHeap_Structure():
    
    def test_create_heap(self, set_node_config):
        test_node_heap_1 = NodeHeap("max", "someDate", set_node_config)
        assert test_node_heap_1.nodeCount == len(set_node_config)
