from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
import time
from profiles.models import Child, ChildView, get_cv_list_from_ac, create_childview

from datetime import datetime, timedelta
from my_django_utils import select_related_generic, select_related_generic_prop 
from mydebug import *
import urllib, simplejson
import re
from notify.models import create_message, create_update, send_email, create_user_update, create_user_update_for_child_playlist_adults
from django.core.urlresolvers import reverse
from photos.models import *
from my_django_utils import PDEncoder, children_required
from friends.models import populate_friend_suggestion, FriendSuggestion, ContactEmail


@login_required
@children_required
def home(request, new_user = None):

    ctx = {}
    template = 'home/homepage.html'
    fb_user=False

    if new_user is not None:
        new_user = True
    else:
        new_user = False

    my_profile = request.user.get_profile()
    
    if new_user:    

        fb_user = my_profile.get_facebook_user()

        if fb_user is not None:
            ctx.update({ 
                "fb_user": True
            }) 
        else:
            ctx.update({
                "show_addr_book": True
            })

        if "show_addr_book" in request.GET:
            ctx.update({
                "fb_user": False,
                "show_addr_book": True,
            })
        

        manage_playlist_children = get_cv_list_from_ac(request.user, my_profile.manage_playlist_children)  
        
        ctx.update({ 
                "manage_playlist_children": manage_playlist_children,
        })


    start = datetime.now()
    end = start + timedelta(days=7)
    if not start.strftime('%B') == end.strftime('%B'):
        month =  start.strftime('%b') + ' - ' + end.strftime('%b')
    else:
        month = start.strftime('%B')


    if not start.strftime('%Y') == end.strftime('%Y'):
        year =  start.strftime('%Y') + ' - ' + end.strftime('%Y')
    else:
        year = start.strftime('%Y')

  
    # determine day list on homepage -- 
    day_suffix = ['th'] + ['st','nd','rd'] + 17*['th'] + ['st','nd','rd'] + 7*['th'] + ['st']
    day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_day = start
    days = []

    while not current_day.day == end.day:
        day = current_day.strftime('%d')
        days.append({ 'day': day, 'suffix':day_suffix[int(day)], 'dow':day_of_week[current_day.weekday()] })
        current_day = current_day + timedelta(days=1)    

    only_child = False
    view_schedule_children = get_cv_list_from_ac(request.user, my_profile.view_schedule_children)  
    if len(view_schedule_children) == 1:
        only_child = True
    current_child_cv = view_schedule_children[0]
    manage_playlist_children = get_cv_list_from_ac(request.user, my_profile.manage_playlist_children)  

    ctx.update({ 
                'manage_playlist_children':manage_playlist_children,
                'current_child':current_child_cv,
                'view_schedule_children':view_schedule_children,
                'month':month,
                'year':year,
                'days':days,
                'updates': request.user.updates.cache().select_related('update').filter(update__deleted='0')[:10], 
                'timestamp': int(time.time()),
                'new_user':new_user,
                'cat_home': True,
                'fb_app_id': settings.FB_API_KEY,
                'www_host': settings.WWW_HOST,
                'only_child':only_child,
               })
    
    return render_to_response(template, RequestContext(request, ctx))


@login_required
def get_suggested_friends(request):
    my_profile = request.user.get_profile()
    response_dict = {}

    suggest_friends_list = {}

    for ac in my_profile.manage_playlist_children:
        friend_suggestion_list = list(FriendSuggestion.objects.cache().select_related('child','child__photo','child__album','suggested_child','suggested_child__photo','suggested_child__school','suggested_child__album').filter(child=ac.child_id, active=True).all()[:3])

        child_list = []
        for sf in friend_suggestion_list:
            child_list.append(sf)
        sf_list = create_list_of_children_and_parents(request, child_list)
        suggest_friends_list.update({ ac.child_id : sf_list })


    response_dict.update({ 'success': True, 'suggested_friends':suggest_friends_list  })

    return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')

@login_required
def new_home(request):
    return home(request, new_user = True)


@login_required
def get_condensed_calendar(request, child_id, **kwargs):
    if child_id:
        if not re.match('^[0-9]+$',child_id):
            raise Exception('Invalid input')
        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            raise Exception("Invalid input")

        childview = create_childview(user=request.user, child=child)
        if not childview.can_view_child_schedule:
            raise Exception("No permissions for this")
    else:
        raise Exception('Invalid input')


    start = datetime.now()
    start = start.replace(hour=0,minute=1,second=0)
    end = start + timedelta(days=7, hours=2)
    end = end.replace(hour=0,minute=1,second=0)

    days = []

    day_to_array_map = {}
    day_counter = 0

    current_day = start    
    event_day_list = []

    while not current_day.day == end.day:
        day = current_day.strftime('%d')
        day_to_array_map[day] = day_counter
        day_counter = day_counter + 1
        event_day_list.append([])
        current_day = current_day + timedelta(days=1)

    event_list = list(child.events.select_related('event').filter(event__start__gte = start, event__end__lte = end))
    select_related_generic_prop(event_list, 'activity','event')

    max_events = 3

    for ep in event_list:
        if not ep.status == '1' and not ep.status == '5':
            ev_day = ep.event.start.strftime('%d')
            
            ev_start = ep.event.start.strftime('%I:%M %p')
            ev_status = ep.status

            ev_index = day_to_array_map[ev_day]

            if len(event_day_list[ev_index]) < max_events:
                activity = ep.event.activity

                event_day_list[ev_index].append({ 'direct_url':activity.direct_url, 'type':activity.type, 'start': ev_start, 'status': ev_status, 'summary':activity.summary() })
                
    return HttpResponse(simplejson.dumps(event_day_list), mimetype='application/javascript')




@login_required
def get_signup_friends(request):
    fb_friends = False
    addr_friends = False

    if request.method == "POST":
        if "fb_friends" in request.POST:
            fb_friends = True
        elif "addr_friends" in request.POST:
            addr_friends = True        

        response_dict = {}
        profile = request.user.get_profile()
        if fb_friends:
            current_fb_users_list = profile.run_getAppUsers_query()
            if current_fb_users_list is not None:
                current_fb_users_string = ','.join(current_fb_users_list)    
            num_imported = run_fb_import(request)

            playdation_friend_users = profile.get_playdation_fb_friend_users(current_fb_users_list)
    
            json_list = create_list_of_parents_and_children(request, playdation_friend_users)
            response_dict.update({ 'success': True, 'playdation_friends':json_list, 'current_fb_users':current_fb_users_string })

        
        else: # address book
            # noop if import already done.. (i think)
    
            status, error = run_import(request)
            playdation_friend_users = profile.get_playdation_contact_friend_users()
            json_list = create_list_of_parents_and_children(request, playdation_friend_users)
            response_dict.update({ 'success': True, 'playdation_friends':json_list })

        # since we have the user on hold anyway, let's take the opportunity to populate their possible friends.
        for ac in profile.manage_playlist_children:
            populate_friend_suggestion(ac.child, request.user)
        
        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')

@login_required
def import_facebook_friends(request):
    profile = request.user.get_profile()
    num_imported = run_fb_import(request)
    current_fb_users_list = profile.run_getAppUsers_query()
    current_fb_users_string = ''
    if current_fb_users_list is not None:
        current_fb_users_string = ','.join(current_fb_users_list)    

    response_dict = { 'success': True, 'current_fb_users':current_fb_users_string }
    return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')


def run_fb_import(request):
    profile = request.user.get_profile()
    fb_user = profile.get_facebook_user()
    if fb_user is None:
        raise Exception('no fb user')
    
    from account.graphapi import GraphAPI

    fql= "SELECT uid, name, first_name, last_name, pic_square FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me())"
    fb_api = GraphAPI(fb_user.access_token)
    friends = fb_api.fql(fql)

    app_user_friends = profile.run_getAppUsers_query()
    from profiles.models import FacebookUser
    friend_fb_users=FacebookUser.objects.filter(facebook_id__in=app_user_friends)
    fb_user_dict = {}
    for fuser in friend_fb_users:
        fb_user_dict[int(fuser.facebook_id)]=fuser.user

    from friends.models import ContactFB
    cn = 0    

    for f in friends:
        name = f["name"]
        id = f["uid"]
        fname = f["first_name"]
        lname = f["last_name"]

        if id in fb_user_dict:
            user = fb_user_dict[id]
        else:
            user = None

        try:
            obj = ContactFB.objects.get(owner=request.user, facebook_id = id)
            if obj.first_name != fname or obj.last_name != lname or obj.name != name:
                obj.first_name = fname
                obj.last_name = lname
                obj.name = name
                obj.save()
        except ContactFB.DoesNotExist:
            obj = ContactFB(
                owner = request.user,
                facebook_id = id,
                name = name,
                first_name=fname,
                last_name=lname,
                user = user
            ).save()
            cn = cn + 1

    return cn


def run_import(request):
    from contacts_import.views import signup_run_import
    status, error = signup_run_import(request)
    return status, error


def import_email_list(request):
    status, error = run_import(request)
    response_dict = { "success":status, "error":error }

    return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')




@login_required
def import_generic(request):
    if request.method == 'POST':
        post = request.POST
        service = post.get('service', None)
        password = post.get('password', None)
        email = post.get('email', None)

        if (service is None) or (password is None) or (email is None):
            raise Exception('data incomplete') 
    
        request.session["generic"] = True
        request.session["password"] = password
        request.session["email"] = email
        request.session["service"] = service

        status, error = run_import(request)

        response_dict = { "success":status, "error":error }

        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')


from django.core.validators import email_re
@login_required
def save_email_list(request):
    if request.method == 'POST':
        post = request.POST
        emails = post.get('emails', None)

        if emails is None:
            raise Exception('no email list passed in')

        email_list_unstripped = emails.split(',')
        email_list = []
        bad_emails = []
        for email in email_list_unstripped:
            if email_re.match(email.strip()):
                email_list.append(email.strip())
            else:
                bad_emails.append(email)

        response_dict = {}
        if not bad_emails:
            request.session["email_list"] = email_list
            response_dict = { "success":True, "message": "Done" }
        else:
            response_dict = { "success":False, "message": "Invalid emails found", "bad_emails":bad_emails }
    
        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')



@login_required
def get_non_user_contacts(request):
    if request.method == 'POST':
        if "run_import" in request.POST:
            status, error = run_import(request)
        non_user_contacts = request.user.get_profile().get_playdation_contact_non_users()
        non_users = []
        for contact in non_user_contacts:
            label = contact.name
            if label is None or len(label) == 0:
                label=contact.email

            label = label.lower()

            non_users.append({ "label":label, "email":contact.email, "name":contact.name, "id":contact.id })


        from operator import itemgetter
        non_users.sort(key=itemgetter('label'))

        MAX_NO_KEYS = 30
        MIN_CONTACTS_PER_LETTER = 10
        FIVE_BUCKET_MAX = 120
        from string import ascii_letters
        sort_keys = [ ]
        buckets = []
        bucket_size = 7

        if len(non_users) > MAX_NO_KEYS:
            if  len(non_users) > FIVE_BUCKET_MAX:
                bucket_size = 3
        
            i=0
            while i < 26:
                min_l = i
                max_l = i + bucket_size - 1
                if max_l > 25:
                    max_l = 25

                buckets.append( (ascii_letters[min_l], ascii_letters[max_l]) )
                i = i + bucket_size

           
            min_l, max_l = buckets[0]
            i=0

            current_bucket = 0
            min_l, max_l = buckets[current_bucket]
            for contact in non_users:
                if contact["label"][0].lower() >= min_l and current_bucket < len(buckets):
                    sort_keys.append( [ min_l + ' - ' + max_l , i  ] )
                    current_bucket = current_bucket + 1
                    if current_bucket < len(buckets):
                        min_l, max_l = buckets[current_bucket]

                i = i + 1

        response_dict = { "success":True, "non_users": non_users, "sort_keys":sort_keys }

        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')



@login_required
def invite_by_email(request):
    if request.method == 'POST':
        invites = request.POST.getlist("invite_id")

        for invite_id in invites:
            if not re.match('^[0-9]+$',invite_id):
                raise Exception('Invalid input')

            invite = ContactEmail.objects.get(owner = request.user, id=int(invite_id))
            invite.send_invite()

        request.session["event"] = "Invited Contacts via Email"
        if "ajax" in request.POST:
            response_dict = { "success":True, "message": Done }
    
            return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')
        else:
            return HttpResponseRedirect(reverse("home"))



def create_list_of_parents_and_children(request, user_list):
    ajax_user_list = []
    for user in user_list:
        profile = user.get_profile() 
        for ac in profile.manage_playlist_children:
            ajax_user = { 'user': profile.get_profile(), 'child': create_childview(user=request.user, child=ac.child).get_profile() }
            ajax_user_list.append(ajax_user)   
    
    return ajax_user_list


def create_list_of_children_and_parents(request, child_list):
    result = []
    for sf in child_list:
        child = sf.suggested_child
        parent_list = []
        for parent in child.parents:
            parent_list.append(parent.get_profile().get_profile())    

        childview = create_childview(user=request.user, child=child)

        result.append({ 'suggestion_id': int(sf.id), 'child':childview.profile, 'parents':parent_list })

    return result

