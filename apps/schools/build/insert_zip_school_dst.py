#!/usr/bin/python
from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from django.db import connection
from schools.models import School, Zip_School_Prox
from places.models import Zip

import xml.sax.handler
from copy import copy
import re

zips = { }

school_last = 'nothing'
school_cache = None

f = open('sdc.csv','r')

for ssss in f:
    line = ssss.rstrip()
    parts = line.split(',')
    gsid = str(parts[0])
    zip_code = str(parts[1])
    dst = parts[2]
    if not (re.match('^[0-9]{5}$',zip_code)):
        continue

#    insert(zip_code, gsid, dst)
    zip = zip_code
    school = gsid
    distance = dst

    zip = zip.strip()
    zp = Zip.objects.get(zip=str(zip))

    school = school.strip()
    sc = School.objects.get(gsid=str(school))

#    try:
    zsp = Zip_School_Prox(school=sc, zip=zp, dst = distance)
    zsp.save()
#    except:
#        print "FAIL FAIL FAIL zip: " + str(zip) + " school: " + school
#        pass




#for sc in connection.queries:
#    print str(sc)
