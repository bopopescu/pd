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
from photos.models import *

import os, random
from datetime import datetime
from datetime import timedelta

from notify.models import create_message, create_update, send_email
from schedule.models import *
import random
from random import randint

def tossh():
    if random.choice(range(0,10)) < 5:
        return True
    else:
        return False

def tosst():
    if random.choice(range(0,9)) < 3:
        return True
    else:
        return False

def tossq():
    if random.choice(range(0,12)) < 3:
        return True
    else:
        return False

status_updates = [
                  "Off to see Rango at Loews Lincoln Square",
                  "Going to the park",
                  "Checking out that awesome new place",
                  "Helping with homework",
                  "Zoo time! Off to the Central Park Zoo. Kids are excited about the zebras!",
                  "Just finished reading a bed time story. Nighty night.",
                  "Gymboree, here we come!",
                  "Taking the kids to a birthday party at Chuck E. Cheese.",
                  "Going to the 72nd street playground",
                  ]


times = [
         "Now",
         "Now",
         "Now",
         "In two hours",
         "In three hours",
         "This evening",
         "In an hour",
         "In five minutes",         
         ]


def create_status_feed(us, parents = None):
    for i in range(0,10):
        if parents is not None:
            user = parents[random.choice(range(0, len(parents)))]
        else:
            user = us

        ac_list = user.get_profile().manage_playlist_children
        children = []
        for ac in ac_list:
            children.append(ac.child)


        ctx = { 
               'actor':user.get_profile(),
               'actor_children':ok[random.choice(range(0, len(ok) ) ) ].first_name,
               'status':status_updates[random.choice(range(0, len(status_updates) ) ) ],
               'when':times[random.choice(range(0, len(times)))], 
               }
        
        create_update(us, 'status_update_self', ctx)
        create_user_update(us, up)
        exclude_users = []
        for child in children:
            exclude_users = exclude_users + create_user_update_for_child_playlist_adults(child, up, exclude = exclude_users)



us = User.objects.get(id=61)

ac_list = us.get_profile().manage_playlist_children
child = ac_list[0].child

parents_to_update = []
for f in child.friends.all():
    parents = f.parents
    parent = parents[0]
    parents_to_update.append(parent)

create_status_feed()

#
#for ac in ac_list:
#    print ac.child.first_name

#
#families = []
#for i in range(0,20):
#    kd = create_family()
#    families.append(kd)
#
#print str(families)
#    
#create_status_feed(us, observer_kids)
#
#
