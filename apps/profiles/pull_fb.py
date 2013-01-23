from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from django.contrib.auth.models import User
from django.db import connection
from mydebug import *
import urllib, simplejson


from profiles.models import *
from friends.models import *
from account.graphapi import GraphAPI

queued = FacebookUser.objects.filter(queue_for_pull=1)


for q in queued:
    quser = q.user
    print quser.get_profile().first_name
    fql= "SELECT uid, name, first_name, last_name, pic_square FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me())"
    fb_api = GraphAPI(q.access_token)
    friends = fb_api.fql(fql)

    app_user_friends = quser.get_profile().run_getAppUsers_query()
    friend_fb_users=FacebookUser.objects.filter(facebook_id__in=app_user_friends)
    fb_user_dict = {}
    for fuser in friend_fb_users:
        fb_user_dict[fuser.facebook_id]=fuser.user
        

    cn = 0
    for f in friends:
        name = f["name"]
        id = f["uid"]
        fname = f["first_name"]
        lname = f["last_name"]
        print "name:  " + name + " fname: " + fname + " lname: " + lname

        if id in fb_user_dict:
            user = fb_user_dict[id]
        else:
            user = None

        obj, created = ContactFB.objects.get_or_create(
            owner = quser,
            facebook_id = id,
            name = name,
            first_name=fname,
            last_name=lname,
            user = user
        )
        if created:
            cn = cn + 1


    q.queue_for_pull=False
    q.save()
    print "for " + quser.get_profile().first_name + " imported " + str(cn) + " friends " 

