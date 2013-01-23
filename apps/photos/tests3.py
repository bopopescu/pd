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



#for album in Album.objects.all():
#    for photo in album.photos.all():
#        print "running for:" + photo.original.url
#        print photo.original.url






#class Photo(ImageModel):
#    caption = models.CharField(max_length=200)
#    original_image = models.ImageField(upload_to='photos')


#ph = Photo(caption='funky donkey', original_image='image.jpg')

#


for profile in Child.objects.all():
    parent = profile.parents[0]
    print str(parent)
    if profile.album is None:
        album = Album(title="Profile Photos", created_by=parent)
        album.save()
        profile.album=album
        profile.save()
#
#user = User.objects.get(id=8)

#album = user.get_profile().album
#print str(album)

#ph.save()
#print ph.original.url



