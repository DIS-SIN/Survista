from typing import Callable, Any, TypeVar

T = TypeVar('T')

def comp_wrapper(func: Callable[[T, Any], bool]) -> Callable[[T, Any], bool]:
    def comp_func(self, other):
        if not isinstance(other, HeapNode):
            TypeError(f"other must be of type HeapNode but got {type(other)}")
        elif other.key != self.key:
            raise ValueError(
                "Comparison node does not have the correct key " +
                f"expected HeapNode with key {self.key} but got {other}"
            )
        func(self, other)    
    return comp_func


"""
These two implementations are equivalent

class SomeClass:
    @comp_func
    def __eq__(self, other):
        #Some comp
        return comp

class SomeClass:
    def __init__(self)
        self.__eq__ = comp_wrapper(self.__eq__)
    
    def __eq__(self, other):
        #Some comp
        return comp
"""