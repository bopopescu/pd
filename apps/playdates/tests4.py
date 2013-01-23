from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)



from profiles.models import Child, Adult_Child, Profile, FacebookUser
from friends.models import Friendship, FriendshipInvitation
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


print "l1 " + str(time())

user = User.objects.select_related('_profile_cache').get(id=83)
dropoff = True
min_participation = 2
max_participation = 3
expire_option = 48
address = '319 e. 50th street'
details = 'some details'
phone = '3473069639'

organizer_child = ['128','129' ]
invitees = ['128_85_132', 'braskin@playdation.com', 'fb_631' ]

when_str = '11/11/2011 10:25 AM'
until_str = '01:35 PM'

when = datetime.strptime(when_str, '%m/%d/%Y %I:%M %p')           
until_str = when_str.split(' ')[0] + ' ' + until_str            
until = datetime.strptime(until_str, '%m/%d/%Y %I:%M %p')


plist = Profile.objects.cache().filter(user__children__friends__in=organizer_child).all() 

for a in plist:
    print a.first_name


