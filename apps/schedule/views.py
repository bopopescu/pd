from urllib import quote
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.create_update import delete_object
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import delete_object
from profiles.models import ChildView, get_cv_list_from_ac, create_childview
from my_django_utils import select_related_generic, select_related_generic_prop 

from gdata.contacts.service import ContactsService


import re
import urllib, simplejson
from datetime import datetime


from schedule.models import *

from mydebug import *
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client
import gdata.acl.data
import atom.data
import time

from gdata.calendar.service import CalendarService
from account.models import update_other_services, other_service
from my_django_utils import PDEncoder, children_required

# update_other_services


GOOGLE_CALENDAR_URI = 'http://www.google.com/calendar/feeds/'

def authsub_login(request):    
    if "token" in request.GET:
        request.session["authsub_token"] = request.GET["token"]
        
        update_other_services(request.user, gcal=request.GET["token"])
        token = request.GET["token"]

#        calendar_service = gdata.calendar.service.CalendarService()
#        calendar_service.SetAuthSubToken(token)
#        calendar_service.auth_token = token
#        calendar_service.UpgradeToSessionToken()
#        feed = calendar_service.GetCalendarListFeed()
#        for i, a_calendar in enumerate(feed.entry):

        return render_to_response("schedule/gcal.html", RequestContext(request, { 'token':request.GET["token"]}))

    calendar_service = CalendarService()
    authsub_url = calendar_service.GenerateAuthSubURL(request.build_absolute_uri(), GOOGLE_CALENDAR_URI, False, True)

    return HttpResponseRedirect(authsub_url)



@login_required
@children_required
def view_calendar(request, child_id = None, periods=None, template="schedule/calendar.html"):
    children = None
    can_edit_child_schedule = False
    child = None
    view_schedule_children = None

    if child_id:
        if not re.match('^[0-9]+$',child_id):
            raise Exception('Invalid input')
        try:
            child = Child.objects.select_related('album','photo','school').get(id=child_id)
        except Child.DoesNotExist:
            raise Exception("Invalid input")


    my_child = False
    if child is not None:    
        cv = ChildView(user=request.user, child=child)
        if not cv.can_view_child_schedule:
            raise Exception("You do not have permissions for this")

        if cv.is_child_mine:
            my_child = True

    if child is None or my_child == True:
        view_schedule_children = request.user.get_profile().view_schedule_children

        if child is None:
            child = view_schedule_children[0].child

    cv = ChildView(user=request.user, child=child)
            
    date = datetime.now()

    if view_schedule_children is None:
        view_schedule_children = request.user.get_profile().view_schedule_children

    view_schedule_children = get_cv_list_from_ac(request.user, view_schedule_children)  

    ctx = {
        'current_child': cv,
        'view_schedule_children': view_schedule_children,
        'date': date,
    }   

    template = 'schedule/calendar.html'
    return render_to_response(template, RequestContext(request, ctx))

@login_required
def get_events(request, child_id):
    if child_id:
        if not re.match('^[0-9]+$',child_id):
            raise Exception('Invalid input')
        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            raise Exception("Invalid input")

        cv = ChildView(user=request.user, child=child)

        if not cv.can_view_child_schedule:
            raise Exception("You do not have permissions for this")

        start, end = get_period_date(request.GET)

        event_list = list(child.events.select_related('event').filter(event__start__gte = start, event__end__lte = end))
        # TODO filter out 'unavailable' events.
        
        select_related_generic_prop(event_list, 'activity','event')

        return_list = process_event_list_for_fullcalendar(event_list)
            
    return HttpResponse(simplejson.dumps(return_list, default=dthandler), mimetype='application/javascript')

@login_required
def new_event(request, child_id):
    child = None
    if child_id:
        if not re.match('^[0-9]+$',child_id):
            raise Exception('Invalid input')
        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            raise Exception("Invalid input")

        cv = ChildView(user=request.user, child=child)

        if not cv.can_edit_child_schedule:
            raise Exception("You do not have permissions to edit child's schedule")
    else:
        raise Exception("Invalid request")

    if request.method == "POST":
        new_event = simplejson.loads(request.POST["new_event"])
        date_format = '%Y-%m-%dT%H:%M'
        start = datetime.strptime(new_event[u"start"], date_format)
        end = datetime.strptime(new_event[u"end"], date_format)

        status = new_event[u"status"]
        activity_opts = new_event[u"activity_opts"]       
        
        ac = create_activity(activity_opts)
        event = create_event(start, end, ac)
        evp = create_eventplan(child, event, status)

        response_dict = { "success":True, "message":"New event/activity created"}

        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

    response_dict = { "success":True, "message":"No new event found"}

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
        
@login_required
def delete_event(request, child_id):
    child = None
    if child_id:
        if not re.match('^[0-9]+$',child_id):
            raise Exception('Invalid input')
        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            raise Exception("Invalid input")

        cv = ChildView(user=request.user, child=child)

        if not cv.can_edit_child_schedule:
            raise Exception("You do not have permissions to edit child's schedule")

    if request.method == "POST":
        id = request.POST["id"]

        if not re.match('^[0-9]+$',id):
            raise Exception('Invalid input')

        evp = EventPlan.objects.get(id=id, child=child)
        evp.delete()


        response_dict = { "success":True, "message":"No new event found"}
    
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')

    raise Exception("Access Fail")


def cancel_event(request, opts):
    return True



def dthandler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj))    


def process_event_list_for_fullcalendar(event_list):
    reformatted_list = []
    for item in event_list:
        reformatted_list.append( { "description":item.event.activity.summary(), 
                                   "recurring":False, 
                                   "title":item.event.activity.summary(), 
                                   "start":item.event.start, 
                                   "end":item.event.end,
                                   "event_id":item.event_id,
                                   "id":item.id,
                                   "status":item.status,
                                   "summary":item.event.activity.summary(),
                                   "details":item.event.activity.summary_body(),
                                   "allDay":False,
                                   "deleteable":item.event.activity.deleteable,
                                   "absolute_url":item.event.activity.direct_url,
                                })    
    return reformatted_list

        
def dt_from_epoch(epoch):
    import datetime
    return datetime.datetime.fromtimestamp(float(epoch))
       
        
def get_period_date(dict):
    start_epoch = start = end_epoch = end = None
    
    if "start" in dict:
        start_epoch = dict["start"]
        start = dt_from_epoch(float(start_epoch))
        
    if "end" in dict:
        end_epoch = dict["end"]
        end = dt_from_epoch(float(end_epoch))


    if start is None:
        raise Exception('start and end parameters not passed')

    return (start, end)
