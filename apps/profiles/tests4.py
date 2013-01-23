from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from profiles.models import Child, Adult_Child, Profile, FacebookUser, ChildView, create_childview
from friends.models import Friendship
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from django.db import connection
from mydebug import *
import urllib, simplejson
from photos.models import Photo


class PDEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Photo):
            print "doing photo"
            return obj.profile.url
        return simplejson.JSONEncoder.default(self, obj)


def dthandler(obj):
    if hasattr(obj, 'isoformat'):        
        return obj.isoformat()
    else:
        return 'unserializable'
        tolog('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))


def create_list_of_parents_and_children(user_list):
    ajax_user_list = []
    for user in user_list:
        profile = user.get_profile()
        vuser = User.objects.get(id=19)
        for ac in profile.manage_playlist_children:
            ajax_user = { 'user': profile.get_profile(), 'child': create_childview(user=vuser, child=ac.child).get_profile() }
            ajax_user_list.append(ajax_user)

    return simplejson.dumps(ajax_user_list, cls=PDEncoder) # , default=dthandler)



user = User.objects.get(id=2)
user2 = User.objects.get(id=4)
user3 = User.objects.get(id=5)



user_list = [ user, user2, user3 ]

aul = create_list_of_parents_and_children(user_list)

print str(aul)


