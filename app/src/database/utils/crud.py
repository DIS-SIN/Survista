from src.database.db import get_db_session
from .parsetree import ParseTree
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import json
# Query the database for a type matching model (tag, experience, etc)
# that has the same id as the parameter id
def read_row_by_id(model, id):
    """
    get one row by it's primary key id
    """
    session, _ = get_db_session()
    results = session.query(model).filter(model.id == id)
    return results
# Query the database for a type matching model (tag, experience, etc)
# that has the same id as the parameter id
def read_rows(model, filters = None):
    """
    get all rows from model where the criteria in the kwargs is met

    Parameters
    ----------
    model 
        sqlalchemy.ext.declarative.api.DeclativeMeta
    filters
        dict
        filters dict must be in the following structure
        [  {
                'column': {
                    'comparitor': '>=' OR '==' OR '<=' OR '>' OR '<' OR !=
                    'data': str OR int OR float  
                },
                join = "and" OR "or"
            }
        ]
    """
    session, _ = get_db_session()
    if filters is not None:
        querier = ParseTree(model,filters)
        results = querier.query(session)
    else:
        results = session.query(model)
    return results
# Insert a new record in the database, for the sqlalchemy object matching
# the type of the model parameter
def create_row(model):
    session, _ = get_db_session()
    session.add(model)
    try:
        session.commit()
        session.flush()
        
    except Exception as e:
        # TODO Logging.log.exception()
        session.rollback()
        session.flush()
        raise e
def create_rows(*models):
    session, _ = get_db_session()
    for model in models:
        session.add(model)
    try:
        session.commit()
        session.flush()
    except Exception as e:
        # TODO Logging.log.exception()
        print(repr(e))
        session.rollback()
        session.flush()
        raise e
def update_row_by_id(model, id, updates):
    if not isinstance(updates, dict):
        raise TypeError('updates must be of type dict')
    session, _ = get_db_session()
    query = read_row_by_id(model, id)
    #check if row indeed exists by calling the one method
    ##OPTOMIZATION REMARK##
    ##this actually queries the db there needs to be a better way for determining this
    ##DESIGN PATTERN REMARK##
    ## reraising exceptions 
    try:
       query.one()
    except NoResultFound as e:
        raise NoResultFound(
            "row cannot be updated because no row can be found with \
                id: " + str(id))
    except MultipleResultsFound as e:
        raise MultipleResultsFound(
            "the database contains multiple results for this id when \
                only one is expected. id: " + str(id)
        )
    matched =  query.update(updates)
    if matched == 0:
        raise ValueError('bad update request, no columns could be matched \
            updates requested: ' + json.dumps(updates))
    try:
        session.commit()
        session.flush()
    except Exception as e:
        # TODO Logging.log.exception()
        session.rollback()
        session.flush()
        raise e
def update_rows(model, updates, filters = None):
    if not isinstance(updates, dict):
        raise TypeError('updates must be of type dict')
    session, _ = get_db_session()
    results = read_rows(model,filters)
    check_res = results.first()
    if check_res == None:
        raise NoResultFound(
         "no rows can be updated because no rows can be found \
             with the following filters: " + json.dumps(filters)
        )
    matched = results.update(updates)
    if matched == 0:
        raise ValueError('bad update request, no columns could be matched \
            updates requested: ' + json.dumps(updates))
    try:
        session.commit()
        session.flush()
    except Exception as e:
        # TODO Logging.log.exception()
        session.rollback()
        session.flush()
        raise e
def delete_row_by_id(model, id):
    session, _ = get_db_session()
    results = read_row_by_id(model, id)
    matched = results.delete()
    if matched == 0:
        raise NoResultFound('a row with the id specified was not found \
            id: ' + str(id))
    try:
        session.commit()
        session.flush()
    except Exception as e:
        # TODO Logging.log.exception()
        session.rollback()
        session.flush()
        raise e
def delete_rows(model, filters = None):
    session, _ = get_db_session()
    results = read_rows(model, filters)
    matched = results.delete()
    if matched == 0:
        raise NoResultFound('No rows were found to delete with the following \
             filters: ' + json.dumps(filters))
    try:
        session.commit()
        session.flush()
    except Exception as e:
        # TODO Logging.log.exception()
        session.rollback()
        session.flush()
        raise e
def execute_sql(sql):
    if not isinstance(sql, str):
        raise TypeError('sql must be of type str')
    session, _ = get_db_session()
    try:
        results = session.execute(sql)
        session.commit()
        session.flush()
        return results
    except Exception as e:
        session.rollback()
        session.flush()
        raise e
    