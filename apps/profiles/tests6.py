from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from profiles.models import Child, Adult_Child, Profile, FacebookUser, ChildView
from friends.models import Friendship
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from django.db import connection

user = User.objects.get(id=200)

child = Child.objects.get(id=142)

cv = ChildView(user=user, child=child)

print cv.profile["first_name"]

if cv.can_edit_child_schedule:
    print "YUP schedule"

if cv.can_edit_child_playlist:
    print "YUP playlist"

if cv.can_view_child_playlist:
    print "YUP view playlist"

if cv.my_child:
    print "My Child"

if cv.is_in_friends:
    print "In Friends"

if cv.is_pending_sent:
    print "Pending Sent"

if cv.is_pending_received:
    print "Pending Received"

# print str(cv)
