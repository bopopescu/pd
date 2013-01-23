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

from models import *
from profiles.models import Child
from django.contrib.auth.models import User
from playdates.models import *
import time

us = User.objects.get(id=2)

prefs = get_message_preferences(us)


#prefs['pending_friend_reminder'] = False

#save_message_preferences(us, prefs)

print str(prefs)
