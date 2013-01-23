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

access_token = '121631667910635|06254ef00a9b3b537d327c2e-1045167610|qnUmeaX7VvApskfkOt8J5hsh5yg'
actee_fb_id = '692537411'

args = {
    'link':'http://www.playdation.net'+reverse("view_playdate_with_fb", kwargs={"playdate_id":'39'}),
    'attribution':simplejson.dumps('Playdation'),
    'name':simplejson.dumps('Playdation link'),
    'caption':simplejson.dumps('Playdation - Your child\'s social life'),
    'description':simplejson.dumps('Playdation - Your child\'s social life in one place'),
    'picture':'http://www.playdation.net/static/images/slogo.png'
} 

print str(args)


ctx = { }

post_to_other_facebook(access_token, actee_fb_id, 'playdate_request_received', ctx, **args)
