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



try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client
import gdata.calendar.service
import gdata.acl.data
import atom.data
import time

# token = '1/aZU-JkcZzGiWKC2JCGDtcxc4sTBl7gDlQhAgY96nQB8'


# token='1/hywxRQrkAMOANgpYhNKRMraAbDFYtYtNhv0u0Ph_6xk'
#token='1/MrD1eooOcuPKrGsM6v5OG46eWZY1c_nDFNk78WE-WRU'
# token='1/PBZICkZs16_GtGH63RL7q6sEhEClb5MgiAkP0O5nxOo'
#token='1/1R_DYc41HE28MN1u8A7DLWeo_cShxsai0lGeQ4B1JuE'
#token = '1/_TMhU1QFReuA_3Dnm23Le538igIvwXk6i97qbsxecTo'
# token = '1/dop_xNPdNvuDLQrUtkEe1xS2_oID98OaZHmUvCm4OfE'
token = '1/oKYYZ0CIal_J5LIm0pmp1wD972RwFDkqhDdM6Y-8Amo'

calendar_service = gdata.calendar.service.CalendarService()
calendar_service.SetAuthSubToken(token)
#calendar_service.UpgradeToSessionToken()

mt = calendar_service._GetAuthToken()

print "session_token:" + mt

# gdata.gauth.AuthSubToken(token))
#username='boris.raskin@gmail.com'

#feed = calendar_service.GetAllCalendarsFeed()
#print feed.title.text
#for i, a_calendar in enumerate(feed.entry):
#    print '\t%s. %s' % (i, a_calendar.title.text,)

text_query = '#pd'
query = gdata.calendar.service.CalendarEventQuery('default', 'private', 'full', text_query)

feed = calendar_service.CalendarQuery(query)

for i, an_event in enumerate(feed.entry):
  print str(an_event)

  print '\t%s. %s' % (i, an_event.title.text,)
  print '\t\t%s. %s' % (i, an_event.content.text,)
  print '\t\t%s. %s' % (i, an_event.uid,)
  for a_when in an_event.when:
    print '\t\tStart time: %s' % (a_when.start_time,)
    print '\t\tEnd time:   %s' % (a_when.end_time,)


