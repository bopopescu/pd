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
from mydebug import *
from django.db import connection
from django import db

from photos.models import *

from comments.models import *



#class Photo(ImageModel):
#    caption = models.CharField(max_length=200)
#    original_image = models.ImageField(upload_to='photos')


#ph = Photo(caption='funky donkey', original_image='image.jpg')
#ph.save()
db.reset_queries()

ph = Photo.objects.select_related('comments').get(id=151)
#print ph.id
u = User.objects.get(id=26)

c = Comment(item =ph, user=u, comment="I think this  actually works")
c.save()

tolog(str(connection.queries))

db.reset_queries()

for x in ph.comments.all():
    print x.comment
    
    
tolog(str(connection.queries))
