from flask_restful import Resource
from flask import g
import os
import db
class Surveys(Resource):
    def get(self):
        db.get_db()
        query = "SELECT it.id, it.survey_name, it.raw_data_path, st.status_name, it.processing_date \
            FROM index_table AS it INNER JOIN statuses AS st ON it.status_id = st.id "
        res = g.index_db.execute(query).fetchall()
        if query is None:
            return {}, 202
        else:
            surveys = {}
            for row in res:
                slug = str(row['raw_data_path']).rsplit(os.path.sep,1)[1]
                surveys[row['id']] = {
                    "surveyID": row['id'],
                    "surveyName": row['survey_name'],
                    "surveyStatus": row['status_name'],
                    "slug": slug,
                    "processingDate": row['processing_date']
                }
            return surveys


        
