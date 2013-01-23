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

from django.contrib.auth.models import User
import time

from management import create_default_profile


my_user = User.objects.get(id=200)

my_user.delete()
