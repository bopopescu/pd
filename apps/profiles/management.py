from django.db.models import get_models, signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _

from photos.models import create_image, create_album

from photos import models as photos
from profiles import models as profiles
from django.contrib.auth.models import User
from profiles.models import Profile

import os

# terminology
# actor - the person who is doing the action - joined, invited, rsvped, cancelled, commented, added to playlist, liked, tagged, posted, added, modified,
# actee - the person who is being done the action on - the recipient of the playdate invite, the recipient of the playlist request, the child being tagged, .
# object - photo, link, playdate, 


def create_user(username, email, password):
    user = User()
    user.username = username
    user.email = email.strip().lower()
    user.set_password(password)
    user.save()

    return user

def create_profile(user, fname, lname, zip):

    profile = Profile()        
    profile.user = user
    profile.first_name = fname
    profile.last_name = lname
    profile.zip_code = zip

    profile.save()
    
    return profile 


def create_default_profile(app, created_models, verbosity, **kwargs):

    try:
        user = User.objects.get(id=1)
    except User.DoesNotExist:
        user = User(id=1, username="default_user", email=settings.DEFAULT_FROM_EMAIL)
        user.save()
        profile = Profile(user=user, first_name="Notification")
        profile.save()

    
def create_placeholders(app, created_models, verbosity, **kwargs):
    al = create_album(settings.DEFAULT_ALBUM_ID, 'Placeholder Album')
    create_image(settings.DEFAULT_PROFILE_PHOTO_ID, al, "Placeholder", os.path.join(settings.PROJECT_ROOT, "media", "images/placeholder.jpg") )



signals.post_syncdb.connect(create_placeholders, sender=photos)
signals.post_syncdb.connect(create_default_profile, sender=profiles)
