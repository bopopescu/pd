from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from django.db import connection
from django import db

from mydebug import * 

from notify.models import MessagePreference, MessagePreferenceDefaults, Update, InternalMessage, Email, FBPost, create_message_content, create_message, get_message_content, inbox_count_for, create_update, send_email
from profiles.models import Child
from django.contrib.auth.models import User
from playdates.models import *
import time

max_limit=5

f = open("/tmp/emails.list")

for line in f:
    print "sending to: " + line.rstrip()
    send_email(line.rstrip(), 'beta_2_invite', ctx={}, skip_footer=True)
    time.sleep(5)

f.close()

