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

def determine_zip(location):
    if location is None:
        return None

    try:
        city, state = location['name'].split(',')
        city = city.strip()
        state = state.strip()
    except:
        return None

    from places.models import Zip


    print city
    print state
    try:
        zs = Zip.objects.filter(city=city, state_full=state)[:1].get()
    except Zip.DoesNotExist:
        return None

    return zs



location = {u'id': u'108424279189115', u'name': u'New York, New York'}
zs = determine_zip(location)
if zs is not None:
    print zs.zip
