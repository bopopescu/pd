#!/usr/bin/env python
# filename: /etc/sentry.conf.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/sentry.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SENTRY_LOG_FILE = '/tmp/sentry.log'
SENTRY_WEB_LOG_FILE = '/tmp/web.log'
SENTRY_WEB_PID_FILE = '/tmp/web.pid'
WEB_LOG_FILE = '/tmp/web.log'

SENTRY_WEB_HOST = 'playdation.net'
SENTRY_WEB_PORT = 8000

SENTRY_ROOT_URLCONF = ''
