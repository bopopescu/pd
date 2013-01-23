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
from django import db
import random


from schools.models import Zip_School_Prox, School

from places.models import Zip
import re
import os
header = """{% extends "site_registration_base.html" %}

{% block head_title %}School Index{% endblock %}

{% block body_class %}home{% endblock %}

{% block body %}
 <div id="content">
"""

footer = """
</div>
{% endblock %}
"""

states = open("/var/www/playdation.net/playdation/templates/sm/states.html","w")
print >>states, header

for s in School.objects.values('state').distinct():
    if s['state'] is None:
        continue
    print >> states, '<a href="/sm/'+s['state']+'/">'+s['state']+'</a><br>'
    state = open("/var/www/playdation.net/playdation/templates/sm/state_"+s['state']+".html","w")
    print >>state, header

    iter=0

    for j in School.objects.values('city').filter(state=s['state']).distinct():
        iter = iter + 1
        city_file_path = '/var/www/playdation.net/playdation/templates/sm/'+s['state']
        if not os.path.exists(city_file_path):
             os.makedirs(city_file_path)
        
        city_file_name = city_file_path +'/city_'+str(iter)+".html"
        city = open(city_file_name,"w")
        print >>city, header

        print >> state, '<a href="/sm/'+s['state'] +'/'+str(iter)+'/">'+j['city']+'</a><br>'

        for i in School.objects.values('id','name').filter(city=j['city'], state=s['state']):
            print >> city, '<a href="/schools/view/'+str(i['id'])+'/">'+i['name']+'</a><br>'

        print >>city, footer
        city.close()

    print >>state, footer
    state.close()

    break

print >>states, footer

states.close()