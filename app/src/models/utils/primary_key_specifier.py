from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import BigInteger

# Change emitted sql based upon which database


class SerialId(expression.ColumnClause):

    def __init__(self, sequence):
        self.sequence = sequence


@compiles(SerialId, 'postgresql')
def myserial(element, compiler, **kw):
    return f"SERIAL '{element.sequence}'"


class pkeyspec(expression.FunctionElement):
    type = BigInteger()

    def __init__(self, sequence):
        self.sequence = sequence


@compiles(pkeyspec, 'postgresql')
def pk(element, compiler, **kw):
    return (f"nextval('{element.sequence}'::regclass)")
