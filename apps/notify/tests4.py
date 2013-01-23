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
from django.contrib.auth.models import User
import time

from django.core.urlresolvers import reverse

import simplejson

im = InternalMessage.objects.get(id=23)

im.associated_item=2

im.save()
