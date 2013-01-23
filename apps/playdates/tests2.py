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

user = User.objects.select_related('_profile_cache').get(id=30)
dropoff = True
min_participation = 2
max_participation = 3
expire_option = 48
address = '319 e. 50th street'
details = 'some details'
phone = '3473069639'

organizer_child = ['57','56' ]
invitees = ['41_31_44','41_40_53', 'braskin@playdation.com' ]

when_str = '11/11/2011 10:25 AM'
until_str = '01:35 PM'

when = datetime.strptime(when_str, '%m/%d/%Y %I:%M %p')           
until_str = when_str.split(' ')[0] + ' ' + until_str            
until = datetime.strptime(until_str, '%m/%d/%Y %I:%M %p')
print "l2 " + str(time())


pd = Playdate()
pd.organizer = user
pd.phone = phone
pd.details = details
pd.address = address
pd.when_from = when
pd.when_until = until
pd.is_dropoff = dropoff
pd.max_participation = max_participation
pd.min_participation = min_participation
pd.expire_option = expire_option
pd.save()
ev = create_event(pd.when_from, pd.when_until, pd)
print "l3 " + str(time())

#l2 1302120278.51
#l3 1302120278.52
#l4 1302120278.52
# 2 seconds
#l5 1302120280.37
# 2 seconds
#l5 1302120282.13
# 2 seconds
#l6 1302120283.99
#l7 1302120283.99

child = None
for child_id in organizer_child:
    if re.match('^[0-9]+$',child_id):
        child = Child.objects.get(id=child_id)
        pdi = PlaydateInviteUser()
        pdi.playdate = pd
        pdi.organizer_child = child
        pdi.to_child = child
        pdi.to_user = user
        pdi.accept()
        create_eventplan(pdi.to_child, ev, "4")

print "l4 " + str(time())
        
for invitee in invitees:
    if re.match('^[0-9]+_[0-9]+_[0-9]+$',invitee): # user id            
        data_parts=invitee.split('_')                               
        pdi = PlaydateInviteUser()
        pdi.playdate = pd
        pdi.organizer_child=Child.objects.get(id=data_parts[0]) 
        pdi.to_user=User.objects.get(id=data_parts[1])
        pdi.to_child=Child.objects.get(id=data_parts[2])
        print "l4.1 " + str(time())

        pdi.save_and_invite()

        print "l4.2 " + str(time())

        create_eventplan(pdi.to_child, ev, "4")
        print "l5 " + str(time())



    elif is_valid_email(invitee):
        pde = PlaydateInviteEmail()
        pde.playdate = pd
        pde.organizer_child=child 
        pde.email = invitee
        pde.token = pde.assign_token()
        print "l5.1 " + str(time())

        pde.save_and_invite()
        print "l6 " + str(time())


print "l7 " + str(time())
