DATABASES = {
    "default": {
#        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "ENGINE": "mysql", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME":   "playdation",               # Or path to database file if using sqlite3.
        "USER": "playdation",                             # Not used with sqlite3.
        "PASSWORD": "playdate123",                         # Not used with sqlite3.
        "HOST": "10.252.177.206",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}


WWW_HOST = 'www.playdation.com'


FB_API_KEY = '183857661635390'
FB_SECRET_KEY = '78c8683c95ddbc0d8e1189e3009bd4bf'
BASE_URL = "http://www.playdation.com/"

YAHOO_CONSUMER_KEY='dj0yJmk9ckRpaVdMbnpPRlZDJmQ9WVdrOVZESTNTalZvTjJVbWNHbzlOakEzT1RFNU5qWXkmcz1jb25zdW1lcnNlY3JldCZ4PTAx'
YAHOO_CONSUMER_SECRET='9f75de381999caa3f0437fe9746545999e962ba1'
GOOGLE_ANAL_ACCOUNT = 'UA-22901472-2'

GOOGLE_OAUTH_CONSUMER_KEY='www.playdation.com'
GOOGLE_OAUTH_CONSUMER_SECRET='IvtAJYBEaLm7EscLtZEKDPqC'
PRODUCTION = True

OAUTH_SETTINGS = {
    'GOOGLE':{
        'OAUTH_CONSUMER_KEY':'www.playdation.com',
        'OAUTH_CONSUMER_SECRET':'IvtAJYBEaLm7EscLtZEKDPqC'
    }                  
}

OAUTH_ACCESS_SETTINGS = {
    'yahoo':{
             'keys': {
                      'KEY': 'dj0yJmk9ckRpaVdMbnpPRlZDJmQ9WVdrOVZESTNTalZvTjJVbWNHbzlOakEzT1RFNU5qWXkmcz1jb25zdW1lcnNlY3JldCZ4PTAx',
                      'SECRET': '9f75de381999caa3f0437fe9746545999e962ba1',
                      },
             'endpoints': {
                      'request_token':'https://api.login.yahoo.com/oauth/v2/get_request_token',
                      'access_token':'https://api.login.yahoo.com/oauth/v2/get_token',
                      'authorize':'https://api.login.yahoo.com/oauth/v2/request_auth',                                
                      'provider_scope':'anything',
                           }
             }
}

BBAUTH_APP_ID = 'kl58lHrIkY17kn585dsBON6TRcNz37Y-'
BBAUTH_SHARED_SECRET = '81ab45d2788d6f00a237d12eb98ab968'

KISS_ID = '//doug1izaerwt3.cloudfront.net/c5bc54dd6381da5d385b0c8c504ba72ae88f74c6.1.js'
