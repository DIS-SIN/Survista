######################################################## FLASK SETTINGS ##############################################################
#Variable used to securly sign cookies
##THIS IS SET IN DEV ENVIRONMENT FOR CONVENIENCE BUT SHOULD BE SET AS AN ENVIRONMENT VARIABLE IN PROD
SECRET_KEY = "dev"

######################################################## FLASK SQLAlchemy SETTINGS ####################################################
#Neo4j Database URI used by the Neomodel OGM
## THIS SHOULD BE SET AS AN ENVIRONMENT VARIABLE IN PRODUCTION ##
NEOMODEL_DATABASE_URI = "bolt://test:test@localhost:7687"
