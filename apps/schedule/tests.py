from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from models import *
from profiles.models import *
import datetime
from django import db
connection = db.connection


from schedule.periods import Year, Month, Week, Day


def create_ca(description):
    ca = CustomActivity(description=description)
    ca.save()
    return ca

#    start = models.DateTimeField(_("start"))
#    end = models.DateTimeField(_("end"),help_text=_("The end time must be later than the start time."))


def now():
    return datetime.datetime.now()


def create_event(start, end, activity):
    ev = Event(start=start, end=end, activity=activity)
    ev.save()
    return ev

def create_eventplan(child, event, status):
    es = EventPlan(child=child, event=event, status=status)
    es.save()
    return es

def process_event_list_for_fullcalendar(event_list):
    reformatted_list = []
    for item in event_list:
        reformatted_list.append( { "description":item.event.activity.summary(), 
                                   "recurring":False, 
                                   "title":item.event.activity.summary(), 
                                   "start":item.event.start, 
                                   "end":item.event.end,
                                   "id":item.event.id,
                                   "status":item.status, 
                                   "allDay":False 
                                })    
    return reformatted_list


def select_related_generic_ev(list_of_items, generic_relation_name, prop):
    from django.contrib.contenttypes.models import ContentType
    generics = {}

    for item in list_of_items:
        obj = getattr(item, prop)
        generics.setdefault(obj.content_type_id, set()).add(obj.object_id)

    content_types = ContentType.objects.in_bulk(generics.keys())
    relations = {}

    for ct, fk_list in generics.items():
        ct_model = content_types[ct].model_class()
        relations[ct] = ct_model.objects.in_bulk(list(fk_list))

    cache_key_name = '_' + generic_relation_name + '_cache'

    for item in list_of_items:
        obj = getattr(item, prop)
        setattr(obj, cache_key_name,
                relations[obj.content_type_id][obj.object_id])




def select_related_generic(list_of_items, generic_relation_name):
    from django.contrib.contenttypes.models import ContentType
    generics = {}

    for item in list_of_items:
        generics.setdefault(item.content_type_id, set()).add(item.object_id)

    content_types = ContentType.objects.in_bulk(generics.keys())
    relations = {}

    for ct, fk_list in generics.items():
        ct_model = content_types[ct].model_class()
        relations[ct] = ct_model.objects.in_bulk(list(fk_list))

    cache_key_name = '_' + generic_relation_name + '_cache'

    for item in list_of_items:
        setattr(item, cache_key_name,
                relations[item.content_type_id][item.object_id])




child = Child.objects.get(id=144)

import random
i=0
activity = create_ca("Available")
while i < 4:
    
    dday = random.randint(1,10)
    hour_start = random.randint(7,20)
    hour_end = hour_start + 1
    
    
    start = datetime.datetime.now() + datetime.timedelta(days=dday, hours=hour_start)
    end = datetime.datetime.now() + datetime.timedelta(days=dday, hours=hour_end)
    
    event = create_event(start, end, activity )
    evp = create_eventplan(child, event, "2")
    i=i+1

#db.reset_queries()
#
#event_list = list(child.events.select_related('event').all())
#
#select_related_generic_ev(event_list, 'activity', 'event')
#
#return_list = process_event_list_for_fullcalendar(event_list)
#
#print "after getting event_list: " + str(len(connection.queries))
#
#
#print str(return_list)
#
#
#
#
#


#event_list = list(eventplan.event for eventplan in list(child.events.select_related('event','event__activity').all()))    
#event_list = list(eventplan.event for eventplan in list(child.events.select_related('event').all()))    
#
#
#def select_related_generic(list_of_items, generic_relation_name):
#    from django.contrib.contenttypes.models import ContentType
#    generics = {}
#    
#    for item in list_of_items:
#        generics.setdefault(item.content_type_id, set()).add(item.object_id)
#    
#    content_types = ContentType.objects.in_bulk(generics.keys())
#    relations = {}
#    
#    for ct, fk_list in generics.items():
#        ct_model = content_types[ct].model_class()
#        relations[ct] = ct_model.objects.in_bulk(list(fk_list))
#   
#    cache_key_name = '_' + generic_relation_name + '_cache' 
#
#    for item in list_of_items:
#        setattr(item, cache_key_name,
#                relations[item.content_type_id][item.object_id])
#
#
#    
#
#
#select_related_generic(event_list, 'activity')
#
#print "after getting event_list: " + str(len(connection.queries))
# db.reset_queries()

#for evl in event_list:
#    print str(evl)

#periods = [ Week ]
#date = datetime.datetime.now() + datetime.timedelta(days=1)
#
#period_objects = dict([(period.__name__.lower(), period(event_list, date)) for period in periods])
#
#
#print "after going through period_objects: " + str(len(connection.queries))
#
#
##for occur in period_objects["week"].get_occurrences():
#for event in period_objects["week"].events:
#    print str(event.activity.summary())    
##    print "queries done: " + str(len(connection.queries)) + " summary: " + str(occur.event.activity.summary())
#
#
#print "end: " + str(len(connection.queries))
#
#
#    print str(day.start)
#    print str(day.end)
#    print str(day.get_occurrences())
#
#get_days():
