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
from django import db
from profiles.models import *

from models import *

# photo has tagged kids, so there are *going* to be permissions associated there with their friends viewing those

# photo is in an album. the album has an owning object - playdate, child or user.

# user access on a photo checks whether the user


#photo = Photo.objects.get(id=2)
#user = User.objects.get(id=1)
#viewer = User.objects.get(id=3)

#albums = get_child_albums(user, viewer)
#for a in albums:
#    print str(a)

from django.contrib.contenttypes.models import ContentType

prt = ContentType.objects.get(app_label="profiles", model="profile")

for a in Profile.objects.all():
#    print a.album.id
    a.album.content_type=prt
    a.album.object_id=a.id
    a.album.save()

prt = ContentType.objects.get(app_label="profiles", model="child")
for a in Child.objects.all():
#    print a.album.id
    a.album.content_type=prt
    a.album.object_id=a.id
    a.album.save()





