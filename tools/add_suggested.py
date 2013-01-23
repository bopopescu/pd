from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)


from django.contrib.auth.models import User
import re
from django.db.models import Q

from friends.models import FriendSuggestion

email = 'bexample@demo.com';

user = User.objects.get(email=email)


profile = user.get_profile()

#child = profile.manage_playlist_children[0]
#child = child.child

#print child.last_name

fake_users = list(User.objects.filter(email__startswith = 'demo')[10:20])
fake_children = []

for fu in fake_users:
    fake_child_ac = fu.get_profile().manage_playlist_children[0]
    fake_children.append(fake_child_ac.child)
    
for ac in profile.manage_playlist_children:
    child = ac.child
    for fc in fake_children:
        print "creating fs for: " + child.first_name + " and " + fc.first_name
        fs, _ = FriendSuggestion.objects.get_or_create(child=child, suggested_child=fc)
        fs, _ = FriendSuggestion.objects.get_or_create(child=fc, suggested_child=child)


#for f in fake_users.all():
#    fs, _ = FriendSuggestion.objects.get_or_create(child=child, suggested_child=p)
#    fs, _ = FriendSuggestion.objects.get_or_create(child=p, suggested_child=child)


# for c in profile.manage_playlist_children:
#    print c.child.last_name
