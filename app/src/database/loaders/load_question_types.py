
from flask import Flask
from sqltills import create_rows


def run(app: Flask):
    from src.models.question_model import QuestionTypeModel
    from src.database.db import get_db
    sess = get_db()
    # if no SUPPORTED_QUESTION_TYPES explicitly stated resort to default
    if app.config.get("SUPPORTED_QUESTION_TYPES") is None:
        app.config['SUPPORTED_QUESTION_TYPES'] = [
            'mcq',
            'dropdown',
            'text',
            'matrix'
        ]
    # get the SUPPORTED_QUESTION_TYPES from the config
    supported_question_types = app.config['SUPPORTED_QUESTION_TYPES']

    # if it is not a list throw an error
    if not isinstance(supported_question_types, list):
        raise TypeError('SUPPORTED_QUESTION_TYPES must be a list if provided')

    # loop through the question_types and push the rows to database
    for q_type in supported_question_types:
        question_type = QuestionTypeModel(question_type=q_type)
        create_rows(sess, question_type)
