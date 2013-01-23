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

from friends.models import populate_friend_suggestion


child_q = Child.objects.all()

for child in child_q:
    populate_friend_suggestion(child)
