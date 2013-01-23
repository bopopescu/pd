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



def get_owner_obj(photo):
    album = photo.album
    owner = album.owner
    return owner


def child_allows(owner, user):
    cv = ChildView(user=user, child=owner)
    if cv.can_view_child_photos:
        return True

def playdate_allows(owner, user):
    print type(owner)
    return True

def can_view_photo(user,photo):
    owner = get_owner_obj(photo)
    return owner.can_view_photo(user)


def get_child_albums(user, viewer):
    b = []
    for ac in user.get_profile().display_children:
        albums = ac.child.albums.all();
        for a in albums:
            if a.can_view_album(viewer):
                b.append(a)
    return b



photo = Photo.objects.get(id=2)

user = User.objects.get(id=1)
viewer = User.objects.get(id=3)

albums = get_child_albums(user, viewer)
for a in albums:
    print str(a)






#
#well = can_view_photo(user,photo)
#
#if well:
#    print "can view photo"
#else:
#    print "can not view photo"



#user = User.objects.get(id=1)




#for c in connection.queries:
#    print str(c)
#
#album = Album.objects.get(id=1)
#for p in album.photos.all():
#    print p.id
