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


from models import *

ep = EventPlan.objects.get(id=694)

event = ep.get_event
event_start = event.start
event_end = event.end
day_start = event_start.replace(hour=0,minute=1,second=0)
day_end = event_end.replace(hour=23,minute=59,second=59)

event_list = list(ep.child.events.select_related('event').filter(event__start__gte = day_start, event__end__lte = day_end, event__end__gt = event_start, event__start__lt=event_end))

#def create_event(start, end, activity):
#def create_eventplan(child, event, status):




for epl in event_list:
    if epl != ep:
        if epl.avail:
            print 'event: ' + str(ep.start) + ' - ' + str(ep.end)
            print 'avail: ' + str(epl.start) + ' - ' + str(epl.end)
            if ep.start <= epl.start and ep.end >= epl.end:
                epl.delete()
#                print "availability fully contained within event. will delete"
            elif ep.start > epl.start and ep.end < epl.end:
                print "event fully contained within availability. will split availability"
                new_event = create_event(ep.end, epl.end, epl.event.activity)
                new_ep = create_eventplan(epl.child, new_event, '2')

                epl.event.end = ep.start
                epl.event.save()
                
                
            elif ep.start > epl.start and ep.end >= epl.end:
#                print "event starts within availability and ends at the end or after end of availability. will cut end time of availability"
                epl.event.end = ep.start
                epl.event.save()
#                print 'new avail: ' + str(epl.start) + ' - ' + str(epl.end)
            elif ep.start <= epl.start and ep.end < epl.end:
#                print "event starts before or at start of availability and ends during availabiliyt. will cut start time of availability"
                epl.event.start = ep.end
                epl.event.save()
#                print 'new avail: ' + str(epl.start) + ' - ' + str(epl.end)
            else:
                print "unrelated blah"


#print ep.status
