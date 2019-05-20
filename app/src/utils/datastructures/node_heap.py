#######
# This module provides a heap structure which allows the efficient sorting of nodes based on a field
#######

from typing import Generic, TypeVar, Optional, Callable, Any
from src.utils.boilerplate_decorators.comparitor_decorators import comp_wrapper
T = TypeVar('T')

class NodeMaxHeap(Generic[T]):
    pass

class HeapNode(Generic[T]):

    def __init__(self, item: T, key: str, 
                 left: Optional["HeapNode[T]"], 
                 right: Optional["HeapNode[T]"]) -> None:
        self.key = key
        self.item = item
        self.right = right
        self.left = left
    
    @property
    def right(self) -> "HeapNode[T]":
        pass
    
    @right.setter
    def right(self, right: "HeapNode[T]"):
        pass

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
       