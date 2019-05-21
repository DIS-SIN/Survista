#######
# This module provides a heap structure which allows the efficient sorting of nodes based on a field
#######

from typing import Generic, TypeVar, Optional, Callable, Any, List
from src.utils.boilerplate_decorators.comparitor_decorators import comp_wrapper
T = TypeVar('T')


class HeapNode(Generic[T]):

    def __init__(self, item: T, key: str, heap_type: str,
                 left: Optional["HeapNode[T]"] = None, 
                 right: Optional["HeapNode[T]"]= None,
                 parent: Optional["HeapNode[T]"] = None) -> None:
        self.key = key
        self.heap_type = heap_type
        self.item = item
        self.right = right
        self.left = left
        self.parent = parent
    
    @property
    def right(self) -> "HeapNode[T]":
        return self._right
    
    @right.setter
    def right(self, right: "HeapNode[T]"):
        if right is not None:
            assert isinstance(right, HeapNode)
            self._right = right
            right.parent = self
            self.item_swap(right)
    
    @property
    def left(self) -> "HeapNode[T]":
        return self._left
    
    @left.setter
    def left(self, left: "HeapNode[T]"):
        if left is not None:
            assert isinstance(left, HeapNode)
            self._left = left
            left.parent = self
            self.item_swap(left) 
        
    @comp_wrapper
    def __eq__(self, other) -> bool:    
        return getattr(self.item, self.key) == getattr(other.item, self.key)
    
    @comp_wrapper
    def __gt__(self, other) -> bool:
        return getattr(self.item, self.key) > getattr(other.item, self.key)
    
    @comp_wrapper
    def __ge__(self, other) -> bool:
        return getattr(self.item, self.key) >= getattr(other.item, self.key)
    
    @comp_wrapper
    def __lt__(self, other) -> bool:
        return getattr(self.item, self.key) < getattr(other.item, self.key)
    
    @comp_wrapper
    def __le__(self, other) -> bool:
        return getattr(self.item, self.key) <= getattr(other.item, self.key)

    def node_compare(self, other: "HeapNode[T]") -> bool:
        "this function takes another node and returns whether or not the other node should replace it"
        if self.heap_type == "min":
            return other < self
        else:
            return other > self
    
    def item_swap(self, other: "HeapNode[T]"):
        """
        function which enfroces the heap properties when building the tree.

        if the items should be swapped they will be swapped and the swap function of the parent node will be called
        """
        if self.node_compare(other):
            temp = self.item
            self.item = other.item
            other.item = temp
            if self.parent is not None:
                self.parent.item_swap(self)

class NodeHeap(Generic[T]):
    def __init__(self, type: str, key: str, nodeArray: Optional[List[T]] = None) -> None:
        self.nodeArray = nodeArray
        self.type = type
        self.key = key
    
    @property
    def nodeArray(self) -> List[T]:
        return self._nodeArray
    
    @nodeArray.setter
    def nodeArray(self, nodeArray: List[T]):
        self._nodeArray = nodeArray
        self.root = HeapNode(nodeArray[0], self.key, self.type)
        self.__buildHeap(self.root, nodeArray, 1)
        
    
    def __buildHeap(self, tree: HeapNode[T], nodeArray: List[T], currentIndex: int):
        if currentIndex >= len(nodeArray):
            return
        if tree.left is None:
            tree.left = HeapNode(nodeArray[currentIndex], self.key, self.type)
        else:
            tree.right = HeapNode(nodeArray[currentIndex], self.key, self.type)
        currentIndex += 1
        self.__buildHeap(tree, nodeArray, currentIndex)

