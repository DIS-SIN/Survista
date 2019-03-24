

##################################################### FLASK SETTINGS #####################################################################
# Specifies that JSON should be rendered in UTF-8 rather than ASCI
JSON_AS_ASCII = False

#Specifies whether JSON should be sorted or not, sorted is useful for caching 
JSON_SORT_KEYS = False


#The amount of time static files should be cached
SEND_FILE_MAX_AGE_DEFAULT = 0

#The maximum ammount that is allowed to be uploaded in bytes 
MAX_CONTENT_LENGTH = 16*1024*1024
################################################## SURVISTA SETTINGS #####################################################################

#If symbols will be required for passwords
PASSWORD_SYMBOLS_REQUIRED = True

#Which symbols are allowed for passwords
PASSWORD_SYMBOLS = '@$%#*!&'

#If numbers are required for passwords
PASSWORD_NUMBERS_REQUIRED = True

#if uppercase letters are required for passwords
PASSWORD_UPPERCASE_REQUIRED = True

#The minimum length for passwords
PASSWORD_LENGTH_MIN = 8

#The maximum length for passwords
PASSWORD_LENGTH_MAX = 20

#Usernames that are restricted such that unauthorized users may not have or contain these usernames
RESTRICTED_USERNAMES= ['admin','owner','open','restricted','deactivated','chuck_norris']

#The minimum length for usernames 
USERNAME_LENGTH_MIN = 5

#The maximum length for usernames
USERNAME_LENGTH_MAX = 10

