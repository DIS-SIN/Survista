######################################################## FLASK SETTINGS ##############################################################
#Specifying that static resources should be cached for an hour
SEND_FILE_MAX_AGE_DEFAULT = 3600

#JSON should be sorted in production to aid with caching
JSON_SORT_KEYS = True

#How long should the session cookie last
PERMANENT_SESSION_LIFETIME = 3600