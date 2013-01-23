from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation') 
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)



from profiles.models import Child, Adult_Child, Profile, FacebookUser
from friends.models import Friendship
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from django.db import connection
from django import db


def create_user(username, email, password):
    user = User()
    user.username = username
    user.email = email.strip().lower()
    user.set_password(password)
    user.save()

    return user

def create_profile(user, fname, lname, zip):

    profile = Profile()        
    profile.user = user
    profile.first_name = fname
    profile.last_name = lname
    profile.zip_code = zip

    profile.save()
    
    return profile 


def create_child(fname, lname, gender, birthdate):
    child = Child(first_name=fname, last_name=lname, gender=gender, birthdate = birthdate)

    child.save()
    return child

def create_fbuser(user, fbid, access_token):
    fbuser = FacebookUser()        
    fbuser.user = user
    fbuser.facebook_id = fbid
    fbuser.last_name = lname
    fbuser.access_token = access_token

    fbuser.save()
    return fbuser

def create_adult_child(adult, child, relation):
    adult_child = Adult_Child( adult = adult, child = child, relation = relation, can_view_schedule = True)
    adult_child.save()
    return adult_child

import datetime


import random


from django.db.models import Q

qs = User.objects.filter(Q(_profile_cache__first_name__startswith='Lin') | Q(_profile_cache__last_name__startswith='Lin'))
for u in qs:
    print str(u)
