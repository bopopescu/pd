from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)


from profiles.models import Child, Adult_Child, Profile, FacebookUser
from friends.models import *
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from django.db import connection
from datetime import datetime, timedelta
from django.db.models import Q
from itertools import *





user = User.objects.get(id=1)
for ac in user.get_profile().manage_playlist_children:
    populate_friend_suggestion(ac.child, user)


#child = Child.objects.get(id=2)
#apopulate_friend_suggestion(child)
