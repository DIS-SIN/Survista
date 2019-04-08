######################################################## FLASK SETTINGS ##############################################################
#Variable used to securly sign cookies
##THIS IS SET IN DEV ENVIRONMENT FOR CONVENIENCE BUT SHOULD BE SET AS AN ENVIRONMENT VARIABLE IN PROD
SECRET_KEY = "dev"

######################################################## FLASK SQLAlchemy SETTINGS ####################################################
#Postgres Database URI used by the SQLAlchemy ORM
## THIS SHOULD BE SET AS AN ENVIRONMENT VARIABLE IN PRODUCTION ##
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:password@localhost:5432/survista"
