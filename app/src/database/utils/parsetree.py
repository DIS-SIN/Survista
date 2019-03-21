"""
this module contains the neccesary datastructures that are used by the utility functions in the cruds module

Contents
--------
Expression
     This class is used to construct a function with the specified expression
"""
#types used to give type hintings wherever possible 
import typing
#the sqlalchemy DeclarativeMeta class is imported to check if methods that require model arguments are actually modelsS
from sqlalchemy.ext.declarative.api import DeclarativeMeta as base
from sqlalchemy import or_, and_
from src.utils.datastructures import Queue, Stack
class Expression:
    """
    This class is used to construct an expression node in the expression parse tree

    Methods
    -------
    __init__
        constructor, takes the model class the atrribute, the operator and a value to construct an expression function
    get_expression
        returns the constructed expression         
    """
    def __init__(self, model,
    module_attribute: str, operator: str, value):
        """
        Constructor for the Expression class.

        The constructor takes a model, the desired_attribute, the comparitor operator and the value to compare to.
        An lambda function is built where the contents of this function is the expression built with the arguments described.

        Parameters
        ----------
        model
            sqlalchemy.ext.declarative.api.DeclativeMeta
            class which inherits the base class from the sqlalchemy declaritive system 
        module_attribute
            str
            the desired attribute of the passed model which will be used to build the left side of the expression
        operator
            str 
            the boolean operator of the expression 
        value
            str OR int OR float OR bool
            the value which will be used to construct the right side of the expression 
        """
        #ensure arguments have valid types
        if not isinstance(model, base):
            raise TypeError('model must be of type sqlalchemy.ext.declarative.api.DeclativeMeta')
        elif not isinstance(module_attribute, str):
            raise TypeError('module_attribute must be of type str')
        elif not isinstance(operator, str):
            raise TypeError('operator must be of type str')
        elif not isinstance(value, (str,int,float,bool)):
            raise TypeError('value must be of type str OR int OR float OR bool')
        #call __getattribute__ to ensure that the object attribute exists 
        model.__getattribute__(model,module_attribute)
        #construct a dictionary with the possible lambda functions for each of the operators 
        valid_operators = {
            '==': lambda: model.__getattribute__(model,module_attribute) == value,
            '>=': lambda: model.__getattribute__(model,module_attribute) >= value,
            '<=': lambda: model.__getattribute__(model,module_attribute) <= value,
            '>': lambda: model.__getattribute__(model,module_attribute) > value,
            '<': lambda: model.__getattribute__(model,module_attribute) < value,
            '!=': lambda: model.__getattribute__(model,module_attribute) != value
        }
        #get the appriopriate lambda function 
        self.expression = valid_operators.get(operator)()
        #if self.expression is none this means that the operator is invalid
        if self.expression is None:
            raise ValueError('operator is not valid')
    def get_expression(self):
        """
        get constructed expression

        Returns
        -------
        function
               the function with the expression
        """
        return self.expression
class Operator:
    """
    This class is used to construct an Operator node in the expression parse tree
    """
    VALID_OPERATORS = set(['and', 'or'])
    def __init__(self, operator = None):
        """
        Constructor for Operator class.
        """
        #check if arguments are of correct type
        if operator is not None:
            self.set_operator(operator)
        else:
            self.operator = None
        self.children = Queue()
    def dequeue_child(self):
        return self.children.dequeue()
    def enqueue_child(self, child):
        self.children.enqueue(child)
    def isEmpty(self):
        return self.children.isEmpty()
    def get_operator(self):
        """
        returns the boolean operator of this operator node
        Returns
        -------
        str
            the boolean operator of this operator node
        """
        return self.operator
    def set_operator(self, operator):
        if not isinstance(operator, str):
            raise TypeError('operator must be of type str')
        elif not operator in self.VALID_OPERATORS:
            raise ValueError('operator is not valid')
        self.operator = operator
class ParseTree:
    """
    This class is used to construct a parse tree and then evalaute this parse tree as a filter for a model query 

    Methods
    __init__
        class constructor, takes model of type sqlalchemy.ext.declarative.api.DeclarativeMeta and filters of type List[Dict] and initialises the parsetree
    query
        from the constructed parse tree query the model and return the results
    """
    def __init__(self, model, filters: typing.List[typing.Dict]):
        """Constructor for ParseTree class.
        
        Parameters
        ----------
        model
            sqlalchemy.ext.declarative.api.DeclarativeMeta
            the desired model to be query
        filters
            list[dict]
            the list of filters to use in the query
        """
        #check if filters is a list
        if not isinstance(filters, list):
            raise TypeError('filters must be of type list with dict children')
        #create a queue from the filters list
        filt_queue = Queue(filters)
        #create a traverse stack which keeps track of the parent
        traverse_stack = Stack()
        self.model = model
        #set the root element and push to the traverse stack
        self.root = Operator()
        traverse_stack.push(self.root)
        while not filt_queue.isEmpty():
            #dequueue the elememnt. check if it is the last by peeking and construct the expression from the values of the element
            elem = filt_queue.dequeue()
            elem_next = filt_queue.peek()
            elem_column = list(elem.keys())[0]
            elem_value = elem[elem_column]['data']
            elem_operator = elem[elem_column]['comparitor']
            elem_expression = Expression(model, elem_column, elem_operator, elem_value)
            current_parent = traverse_stack.pop()
            current_operator = current_parent.get_operator()
            #if the peeked next element is none we know this is the final element of the queue
            if elem_next is None:
                #get the parent from the traverse stack
                #if the parent operator is none we know there is only one element in the filters list so we set the root to be the single expression
                if current_operator is None:
                    self.root = elem_expression
                #otherwise this is the final element of the filter list so we just append to the parent 
                else:
                    current_parent.enqueue_child(elem_expression)
            #otherwise we have a logical operator
            else:
                #we get the current logical operator of the current element
                elem_join = elem['join']
                #we check whether this operator is an "or" OR "and"
                if elem_join == 'or':
                    #we check if the current operator is an or
                    #because or is lower in the logical precedence or operators must always be the parents of and operator nodes 
                    if current_operator == 'or':
                        #if the current parent is a node we just append the children in the child queue
                        current_parent.enqueue_child(elem_expression)
                        #we then repush the current node to the traverse stack
                        traverse_stack.push(current_parent)
                    elif current_operator == 'and':
                        #if the current expression parrent in the traverse stack is an and 
                        #we check if there is already an existing or parent
                        if traverse_stack.isEmpty():
                            parent_parent = None
                        else:
                            parent_parent = traverse_stack.pop()
                        #if not we create a new or parent enqueing the expression to the current and expression parent
                        #we set the root to the new or parent and push it to the traverse stack
                        if parent_parent is None:
                            current_parent.enqueue_child(elem_expression)
                            self.root = Operator('or')
                            self.root.enqueue_child(current_parent)
                            traverse_stack.push(self.root)
                        else:
                            #otherwise we just append the child to the existing root which will always be an or
                            parent_parent.enqueue_child(elem_expression)
                            traverse_stack.push(parent_parent)
                    else:
                        #otherwise if the current_oprator is none we know that this is the first element so we set the operator and enqueue the child expression 
                        current_parent.set_operator('or')
                        current_parent.enqueue_child(elem_expression)
                        traverse_stack.push(current_parent)
                elif elem_join == 'and':
                    #we check the current operator
                    if current_operator == 'or':
                        #if the current operator is an or 
                        #we must create a new and operator parent
                        child = Operator('and')
                        #we enqueue the current expression to this new and parent
                        child.enqueue_child(elem_expression)
                        #we penqueue the new operator parent to the root or parent
                        current_parent.enqueue_child(child)
                        #we push back the root onto the traverse stack
                        traverse_stack.push(current_parent)
                        #we push the new child into the traverse stack
                        traverse_stack.push(child)
                    elif current_operator == 'and':
                        #if the current_operator is and we append the expression as a child and push back the current_parent to the stack
                        current_parent.enqueue_child(elem_expression)
                        traverse_stack.push(current_parent)
                    else:
                        #otherwise we know that the current filter element is the first element in the list
                        # we set the operator of the root to and
                        current_parent.set_operator('and')
                        #we enqueue the child to the operator parent
                        current_parent.enqueue_child(elem_expression)
                        #we push back the current_parent to the stack
                        traverse_stack.push(current_parent)
    def query(self, session):
        #get a Query object for the current model for the current session
        """query the model using the constructed parse tree
        Parameters
        ----------
        session 
            this is a session instance created form the session factory 
        Returns
        -------
        Query
            this is the queried data 
        """
        results = session.query(self.model)
        if isinstance(self.root, Expression):
            #if the root is an expression filter for the current expression and then return the resultant Query object
            results = results.filter(self.root.get_expression())
            return results
        else:
            #if the root is of an instance of the Operator class
            if self.root.get_operator() == 'and':
                #if the root operator is an and we know that there is no further Operator children
                filters = []
                #get the expressions and then returned the Query for the results by invoking the filter method on the list of filters
                while not self.root.isEmpty():
                    filters.append(self.root.dequeue_child().get_expression())
                results = results.filter(*filters)
                return results
            elif self.root.get_operator() == 'or':
                #create an or queue to perserve the precedence of nodes that come first
                or_queue = Queue()
                #go over elements in root
                filters = []
                while not self.root.isEmpty():
                    current_child = self.root.dequeue_child()
                    #if the current_child is an expression append it to the or_queue
                    if isinstance(current_child, Expression):
                        or_queue.enqueue(current_child)
                    #otherwise if it is an operator filter the data on the children of the operator
                    elif isinstance(current_child, Operator):
                        one_filter = []
                        while not current_child.isEmpty():
                            one_filter.append(current_child.dequeue_child().get_expression())
                        filters.append(one_filter)
                if len(filters) > 0 :
                    filts = []
                    for filt in filters:
                        filts.append(and_(*filt))
                    results = results.filter(or_(*filts))
                filters = []
                #filter the data on the expression children of the root
                if not or_queue.isEmpty():
                    while not or_queue.isEmpty():
                        filters.append(or_queue.dequeue().get_expression())
                    results = results.filter(or_(*filters))
                return results
                    
            
                    



            

        






