from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)



from profiles.models import Child, Adult_Child, Profile, FacebookUser, Friendship
from friends.models import ContactFB
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from django.db import connection

from models import *
from schedule.models import *
from django.core.validators import email_re
from datetime import datetime
import re
from time import time

from django.core.validators import email_re

def is_valid_email(email):
    return True if email_re.match(email) else False

us = User.objects.get(id=2)
pd = Playdate.objects.get(id=1)
pd.request_user = us

for funk in pd.invitees_cv:
    print str(funk)




# user = User.objects.select_related('_profile_cache').get(id=83)

#organizer_child = ['129','128']


#child_friends = list(Friendship.objects.select_related('to_child','to_child__adults','to_child__adults__adult___profile_cache').cache().filter(from_child__in=organizer_child).all())
#for c in connection.queries:
#    print str(c)



#ids = []
#for c in child_friends:
#    for a in c.to_child.adults.all():
#        pass
#        print "parent first name: " + a.get_profile().first_name
#    ids.append(int(c.to_child.id))
#
#facebook_friends = list(ContactFB.objects.cache().filter(owner=user).all())
#
#child_friend_parents = list(Adult_Child.objects.select_related('adult___profile_cache').cache().filter(child__in=ids).all())
#
#qa='il'
#for cf in child_friend_parents:
#    profile = cf.adult.get_profile()
#    if re.match("^"+qa,profile.first_name, re.IGNORECASE):
#        print "qa"
#    else:
#        print profile.first_name
#
#        child_friends_parents = list(Profile.objects.cache().filter(user__children__friends__in=child_list).all())


#for c in child_friends:
#    print c.to_child.first_name

#print len(connection.queries)

