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
from profiles.models import Child, FacebookUser

klasses = {
    'User': User,
    'Child': Child,
    'Facebook Connects':FacebookUser,
}

def get_klass(klass):
    return klasses[klass]

def do_count(klass):
    return get_klass(klass).objects.all().count();

#cnt = do_count('User')

#print cnt

abc = User.objects.all()

for a in abc:
    print a.email
    break
