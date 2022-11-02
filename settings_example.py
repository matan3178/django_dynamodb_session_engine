INSTALLED_APPS = [
    ...
    'django.contrib.sessions',
    ...
]
MIDDLEWARE = [
    ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    ...
]
SESSION_ENGINE = 'YOUR_PATH.TO.dynamodb_session'

DYNAMODB_LOCAL_ENDPOINT = 'http://localhost:8000'
DYNAMODB_REGION = 'us-east-1'
DYNAMODB_SESSIONS_TABLE = 'django_sessions'

DYNAMODB_SESSIONS_ATTR_ID = 'id'
DYNAMODB_SESSIONS_ATTR_TTL = 'ttl'
DYNAMODB_SESSIONS_ATTR_SESSION_DATA = 'session_data'
