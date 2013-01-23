from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from models import *

from mydebug import *

import re
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
import urllib, simplejson
from datetime import datetime
from schedule.models import *
from profiles.models import Child, Adult_Child, Profile, FacebookUser, Friendship, ChildView, get_cv_list_from_ac, create_childview
from friends.models import ContactFB, ContactEmail

from my_django_utils import PDEncoder, children_required


from django.core.validators import email_re
from places.models import *
from django.db import connection
from django import db
from django.utils.http import urlquote
from django.contrib.auth import REDIRECT_FIELD_NAME


def is_valid_email(email):
    return True if email_re.match(email) else False

@login_required
def set_invite_choices(request):
    if request.method == "POST":
        post = request.POST
        choices = post.getlist('choices')

        valid_children = {}
        for cv in request.user.get_profile().edit_schedule_children:
            valid_children[str(cv.child_id)] = True
 
        for choice in choices:        
            if not re.match('^[0-9]+:[0-9]+$',choice):
                raise Exception('Invalid input - status')

        for choice in choices:
            data_parts=choice.split(':')
            child_id = data_parts[0];

            child_choice = data_parts[1];

            if str(child_id) not in valid_children:
                raise Exception('not allowed to do that for that child')


            child = Child.objects.get(id=int(child_id))
            invite_design = InviteDesign.objects.get(id=child_choice)
            child.default_invite = invite_design
            child.save()
    
        response_dict = { "success":True, "message": "Done" }
    
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')


def dt_from_epoch(epoch):
  import datetime
  return datetime.datetime.fromtimestamp(float(epoch))
  

@login_required
@children_required
def new_playdate(request, key = None, start = None, end = None, **kwargs):
    template = 'playdates/new_playdate.html'

    edit_schedule_children = get_cv_list_from_ac(request.user, request.user.get_profile().edit_schedule_children)  

    single_child = False
    
    if len(edit_schedule_children) == 1:
        single_child = True

    ctx = {}
    record = None
    oc = None
    start_date = ''
    start_time = ''
    end_time = ''

    if start is not None:
        todebug("start is not none") 
        start_dt = dt_from_epoch(start)
        end_dt = dt_from_epoch(end)
        start_date = start_dt.strftime("%m/%d/%Y")
        start_time = start_dt.strftime("%I:%M%p")
        end_time = end_dt.strftime("%I:%M%p")
        todebug(start_time)
        todebug(end_time)
        todebug(start_date)

    
    if key is not None:
        if re.match('^[0-9]+_[0-9]+_[0-9]+$',key):
            parts = key.split('_')
#           key = str(which_child_friend_id) + '_' + str(parent_id) + '_' + str(self.child.id)
            oc = parts[0]
            child_id = parts[2]
            child = Child.objects.get(id=child_id)

            cv = create_childview(user=request.user, child=child)
            name = cv.profile["name"]
            if len(name) > 15:
                name = name[:15] + '...'

            record = { 
                      'name': name,
                      'tip': cv.profile["name"],
                      'small_profile_pic': cv.profile["small_profile_pic"],
                      'key':key
                      }

        elif re.match('^fb_[0-9]+$',key): #fb id
            parts = key.split('_')
            fb_contact_id = parts[1]
            fbc = ContactFB.objects.get(owner=request.user, id=int(fb_contact_id))

            name = fbc.name
            if len(name) > 15:
                name = name[:15] + '..'

            record = {
                      'key':key,
                      'name':name,
                      'tip':fbc.name,
                      'small_profile_pic':'http://graph.facebook.com/'+ str(fbc.facebook_id) +'/picture?type=square'
            }

        elif re.match('^ce_[0-9]+$',key):
            parts = key.split('_')
            contact_id = parts[1]

            c = ContactEmail.objects.get(owner=request.user, id=contact_id)

            name = c.email
            if len(name) > 15:
                name = name[:15] + '..'

            record = {
                    'key': c.email,
                    'name': name,
                    'tip': c.email,
            }
        else:
            todebug("not matching nothing")
            
    if request.method == "POST":
        post = request.POST
        errors = []
        if (post.get(u'dropoff',None) == 'yes'):
            dropoff = True
        else:
            dropoff = False

        min_participation = None
        max_participation = None
        expire_option = None
        new_loc_name = post.get(u'new_loc_name')
    
        address = post.get(u'address')

        ctx.update({ address: address })
        details = post.get(u'details')
    
    # phone validation
        phone = post.get(u'phone')
        if not re.match('^[0-9\s\(\)\-]+$',phone):
            errors.append('phone contains invalid characters')

        ctx.update({ phone: phone  })    

        activity = post.get(u'activity')
        if not re.match('^[0-9]+$',activity):
            raise Exception('invalid playdate activity')
    
        activity = PDActivity.objects.get(id=activity)

    # figure out how to have multiple organizer children
        organizer_child = post.getlist(u'organizer_child')
        invitees = post.getlist(u'invitee')
    
    # TODO validate invitees, organizer_child
    # date manipulation    
        date_str = post.get(u'date')
        time_start_str = post.get(u'time_start')
        time_end_str = post.get(u'time_end')

        date_good = True
        if not re.match('^\d{1,2}/\d{1,2}/\d{4}$', date_str):
            errors.append("date not selected or is invalid")
            date_good = False

        if not re.match('^\d{1,2}:\d{2}\w{2}$', time_start_str):
            errors.append("start time not selected or is invalid")
            date_good = False


        if not re.match('^\d{1,2}:\d{2}\w{2}$', time_end_str):
            errors.append("end time not selected or is invalid")
            date_good = False

            
        if date_good:
            when_str = date_str + time_start_str
            when = datetime.strptime(when_str, '%m/%d/%Y%I:%M%p')           
            until_str = date_str + time_end_str
            until = datetime.strptime(until_str, '%m/%d/%Y%I:%M%p')

        child_id = organizer_child[0]
        child = Child.objects.get(id=child_id)

        child_invite_design = child.default_invite


        if len(errors) > 0:
            tolog(str(errors))
            ctx.update({ 'errors': errors })
        else:
            pd = Playdate()
            pd.organizer = request.user
            pd.phone = phone
# save phone for later
            profile = request.user.get_profile()
            profile.phone = phone
            profile.save()
            
            pd.details = details
            pd.address = address
            pd.when_from = when
            pd.when_until = until
            pd.is_dropoff = dropoff
            pd.max_participation = max_participation
            pd.min_participation = min_participation
            pd.expire_option = expire_option
            pd.invite_design = child_invite_design
            pd.activity = activity
            pd.save()


            ev = create_event(pd.when_from, pd.when_until, pd)

            if ((new_loc_name is not None) and (len(new_loc_name) > 0)):
                nl = Place(owner=request.user, name=new_loc_name, address=address)
                nl.save()
                
            child = None
            for child_id in organizer_child:
                if re.match('^[0-9]+$',child_id):
                    child = Child.objects.get(id=child_id)
                    pdi = PlaydateInviteUser()
                    pdi.playdate = pd
                    pdi.organizer_child = child
                    pdi.to_child = child
                    pdi.to_user = request.user
                    pdi.phone = phone
                    pdi.accept()
                    create_eventplan(pdi.to_child, ev, "4")

            
            for invitee in invitees:
                if re.match('^[0-9]+_[0-9]+_[0-9]+$',invitee): # user id            
                    data_parts=invitee.split('_')                               
                    pdi = PlaydateInviteUser()
                    pdi.playdate = pd
                    pdi.organizer_child=Child.objects.get(id=data_parts[0]) 
                    pdi.to_user=User.objects.get(id=data_parts[1])
                    pdi.to_child=Child.objects.get(id=data_parts[2])
                    pdi.save_and_invite()
                    create_eventplan(pdi.to_child, ev, "4")

                elif re.match('^fb_[0-9]+$',invitee): #fb id
                    data_parts=invitee.split('_')                               
                    pdf = PlaydateInviteFB()
                    pdf.playdate = pd
                    pdf.organizer_child=child
                    fbc = ContactFB.objects.get(owner=request.user, id=int(data_parts[1]))
                    fbc.invited = True
                    fbc.save()
                    
                    pdf.facebook_contact_id = int(data_parts[1])
            
                    pdf.save_and_invite()

                elif is_valid_email(invitee):
                    pde = PlaydateInviteEmail()
                    pde.playdate = pd
                    pde.organizer_child=child 
                    pde.email = invitee
                    pde.token = pde.assign_token()
                    pde.save_and_invite()

                    try:
                        obj = ContactEmail.objects.get(owner=request.user, email=invitee)
                        obj.invited=True
                        obj.save()
                    except ContactEmail.DoesNotExist:
                        obj = ContactEmail(owner=request.user, email=invitee, invited=True)
                        obj.save()
                


            request.session["event"] = 'Created a Playdate'

            return HttpResponseRedirect(reverse("view_playdate", kwargs={"playdate_id":pd.id}))

    places = list(request.user.places.all())

    activities = list(PDActivity.objects.all())

    children_without_default_designs = []
    for cv in edit_schedule_children:
        if cv.child.default_invite is None:
            children_without_default_designs.append(cv)
            

    phone = request.user.get_profile().phone 
    
    ctx.update( { 
           'edit_schedule_children':edit_schedule_children,
           'places':places,
           'children_without_default_designs': children_without_default_designs,
           'phone':phone,
           'single_child':single_child,
           'activities':activities,
           'fb_app_id':settings.FB_API_KEY,
           'key':key,
           'record':simplejson.dumps(record, cls=PDEncoder),
           'oc':oc,
           'start_date': start_date,
           'start_time': start_time,
           'end_time' : end_time,
           'message': request.session.pop("message", None),
    })

    return render_to_response(template, RequestContext(request, ctx))


def view_playdate_with_fb(request, playdate_id, invite_id, **kwargs):
    
    ctx = {}

    fb_inv = None
    try:
        fb_inv = PlaydateInviteFB.objects.select_related('playdate','facebook_contact').get(id=invite_id, playdate=playdate_id)
    except:
        return HttpResponseRedirect(reverse("nl_home"))

    ctx = {
        'fname':fb_inv.facebook_contact.first_name,
        'lname':fb_inv.facebook_contact.last_name,
        'pd': fb_inv.playdate,
        'inv': fb_inv,
    }
    
    template = 'playdates/pd_connect_fb.html'
    return render_to_response(template, RequestContext(request, ctx))

def view_playdate_with_token(request, playdate_id, token, **kwargs):
    try:
        pde = PlaydateInviteEmail.objects.get(playdate=playdate_id, token=token)
    except PlaydateInviteEmail.DoesNotExist:
        raise Exception('Invalid token')

    dict_for_storage = { 'id':str(pde.playdate_id), 'email':pde.email, 'current_status':pde.status, 'token':token }


    if "pd_invites" in request.session:
        request.session["pd_invites"].update({ str(pde.playdate_id):dict_for_storage  })
    else:
        request.session["pd_invites"] = { str(pde.playdate_id):dict_for_storage } 

    return view_playdate(request, str(pde.playdate_id), **kwargs)



def view_playdate(request, playdate_id, **kwargs):

    if not re.match('^[0-9]+$',playdate_id): # user id    
        raise Exception("Invalid Playdate")
  
    is_organizer = False
    playdate_invite_id = None
    token = email = contactfb = None
    set_status_yes = False
    first_response = False

   
    if 'pd_invites' in request.session and playdate_id in request.session["pd_invites"]: 
        template='playdates/view_pd_non_user.html'

        if "token" in request.session["pd_invites"][playdate_id]:
            token = request.session["pd_invites"][playdate_id]['token']
            email = request.session["pd_invites"][playdate_id]['email']
            del request.session["pd_invites"]
        elif "contactfb" in request.session["pd_invites"][playdate_id]:
            contactfb = request.session["pd_invites"][playdate_id]['contactfb']
            del request.session["pd_invites"]
        else:
            raise Exception('not fbid, no token. something is wrong')
    elif request.user.is_authenticated():
        template = "playdates/view_pd_user.html"
    else:
        request.session["message"] = 'Please log in to view this playdate'
        path = urlquote(request.get_full_path())
        tup = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
        return HttpResponseRedirect('%s?%s=%s' % tup)

    pd = None
    try:
        pd = Playdate.objects.select_related('organizer').get(id=playdate_id)
    except Playdate.DoesNotExist:
        raise Exception('NO PLAYDATE FOUND')

    if request.user.is_authenticated() and ( request.user == pd.organizer ):
        is_organizer = True

    my_invites = None

    if token is not None:
        try:
            my_invites = list(PlaydateInviteEmail.objects.filter(playdate=playdate_id, token=token).all())
        except:
            raise Exception('unauthorized - email ')
    elif contactfb is not None:
        try:
            my_invites = list(PlaydateInviteFB.objects.filter(playdate=playdate_id, facebook_contact=contactfb).all())
        except:
            raise Exception('unauthorized - email ')
    else: 
        try:
            my_invites = list(PlaydateInviteUser.objects.select_related('to_user','to_child','organizer_child').filter(playdate=playdate_id, to_user=request.user))
        except:
            raise Exception('unauthorized - user')

    if my_invites is None or len(my_invites) == 0:
        raise Exception('unauthorized')

    my_invite = None

    event = pd.get_event

    upload_url = reverse("upload_done", kwargs={"album_id":pd.album.id})
    activities = list(PDActivity.objects.all())

    if request.method == "GET" and "set_status" in request.GET:
        inv_status=request.GET['set_status']
        inv_id = request.GET['invite_id']
        inv_type = request.GET['invite_type']
        
        if not re.match('^[0-9]+$',inv_status):
            raise Exception('Invalid input - status')

        if not re.match('^[0-9]+$',inv_id):
            raise Exception('Invalid input - id')
        
        if not re.match('^[\w]+',inv_type):
            raise Exception('Invalid input - type')

#        if 'pd_invites' in request.session and playdate_id in request.session["pd_invites"]:
        for inv in my_invites:
            if inv.id == int(inv_id):
                my_invite = inv
            
#        elif request.user.is_authenticated():
#            for inv in my_invites:
#                if inv.id == inv_id:
#                    my_invite = inv

        if my_invite is None:
            raise Exception('unauthorized - noone')
 
        if my_invite.nr:
            first_response = True
        if inv_status == '2':
            my_invite.accept_and_notify()
            set_status_yes = True
        elif inv_status == '3':
            my_invite.decline_and_notify()
        elif inv_status == '4':
            my_invite.maybe_and_notify()

        pd.status = my_invite.playdate.status

#    if my_invite is None:
#        my_invite = my_invites[0]

    responses = pd.response_breakdown()
        
    for inv_resp in responses:
        for pdi in responses[inv_resp]:
            if isinstance(pdi, PlaydateInviteUser):
                pdi.adult = pdi.to_user.get_profile().get_profile()
                pdi.child = create_childview(user=request.user, child=pdi.to_child)
                pd.to_user = None
                pd.to_child = None

    
    ctx = {
        'pd': pd,
        'album': pd.album,
        'set_status_yes':set_status_yes,
        'upload_url':upload_url,
        'event': event,
        'responses': responses,
        'is_organizer': is_organizer,
        'my_invite': my_invite,
        'my_invites': my_invites,
        'email':email,
        'can_upload':pd.can_upload_photo(request.user),
        'session_key': request.session.session_key,
        'cat_playdates': True,
        'first_response': first_response,
        'activities': activities,
    }
  
    return render_to_response(template, RequestContext(request, ctx))


@login_required
def cancel_playdate(request, playdate_id):
    if not re.match('^[0-9]+$',playdate_id): # user id    
        raise Exception("Invalid Playdate")

    pd = Playdate.objects.select_related('organizer').get(id=playdate_id)

    if not pd.organizer == request.user:
        raise Exception('Not authorized to cancel this playdate')

    pd.cancel()

    return HttpResponseRedirect(reverse("view_playdate", kwargs={"playdate_id":playdate_id}))


@login_required
def get_oc_pd_friends(request):
    if request.user.is_authenticated():
        q = request.POST.get("q", None)
        oc = request.POST.get("oc")

        friend_child_ids = []
        child_hash = {}
        friend_hash = {}
        result_hash = {}
        parent_hash = {}
        response = []


        if q is not None and not re.match('^[\w\s]+$',q):
            raise Exception('Invalid input')

        if not re.match('^[0-9,]+$', oc):
            raise Exception('Invalid input')

        child_list = []
        for child_id in oc.split(','):
            child = Child.objects.get(id=child_id)
            cv = ChildView(user=request.user, child=child)
            if not (cv.can_edit_child_schedule and cv.can_view_child_playlist):
                raise Exception("You do not have the access for this")
            child_list.append(child_id)

        child_friends = list(Friendship.objects.select_related('to_child').cache().filter(from_child__in=child_list).all())
        
        for c in child_friends:
            child_hash[int(c.to_child_id)] = c.to_child
            friend_hash[int(c.to_child_id)] = int(c.from_child_id)
            friend_child_ids.append(int(c.to_child_id))


        child_friend_parents = []

        if child_friends:
            child_friend_parents = list(Adult_Child.objects.select_related('adult','adult___profile_cache','child').cache().filter(child__in=friend_child_ids).all())

        for cf in child_friend_parents:
            parent_hash[int(cf.child_id)] = cf.adult.get_profile()
        
        for c in child_friends:
            child = c.to_child
            profile = parent_hash[int(child.id)]

            if int(child.id) in result_hash:
                continue 
            else:
                result_hash[int(child.id)] = 1

            cv = create_childview(user=request.user, child=child)
            name = cv.profile["first_name"] + ' (' + profile.name   + '\'s Child) '

#            if len(name) > 15:
#                name = name[:15] + '...'
            
            response.append({ 
                            'key': str(friend_hash[child.id]) + '_' + str(profile.user_id) + '_' + str(child.id),
                            'name': name,
                            'tip': cv.profile["name"],
                            'small_profile_pic': cv.profile["small_profile_pic"],
                            })


        from operator import itemgetter
        response.sort(key=itemgetter('name'))

        return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')


@login_required
def get_fb_friends(request):
    facebook_friends = list(ContactFB.objects.cache().filter(owner=request.user, removed=False).all())
    response = {}
    fb_friends = []

    for f in facebook_friends:
        name = f.name
#        if len(name) > 15:
#            name = name[:15] + '..'

        fb_friends.append({
                        'key': 'fb_' + str(f.id),
                        'name': name,
                        'tip' : f.name,
                        'small_profile_pic': 'http://graph.facebook.com/'+ str(f.facebook_id) +'/picture?type=square'
                        })



    from operator import itemgetter
    fb_friends.sort(key=itemgetter('name'))
    
    response["fb_friends"] = fb_friends
    response["got_fb"] = False
    response["got_fb_perms"] = False

    if request.user.get_profile().fb_account_linked:
        response["got_fb"] = True

    if request.user.get_profile().fb_stream_publish:
        response["got_fb_perms"] = True

    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')


@login_required
def get_e_friends(request):
    email_contacts = list(ContactEmail.objects.cache().filter(owner=request.user, removed=False).all())
    response = []

    for c in email_contacts:
        name = c.email
#        if len(name) > 15:
#            name = name[:15] + '..'

        
        if c.invited:
            response.append({
                            'key': c.email,
                            'name': name,
                            'tip': c.email,
                             })

    from operator import itemgetter
    response.sort(key=itemgetter('name'))


    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')



@login_required
def playdate_in_place_save(request, playdate_id):
    if request.method == "POST":
        f = request.POST.get("field");
        v = request.POST.get("value");
        if v == 'false':
            v = False
        elif v=='true':
            v = True

        valid_fields = { 'address':True, 'details':True, 'phone':True, 'is_dropoff':True, 'activity':True  }
        if not f in valid_fields:
            raise Exception('invalid field' + f)


            
        pd = Playdate.objects.select_related('organizer').get(id=playdate_id)
    
        if not pd.organizer == request.user:
            raise Exception('user is not allowed to make changes')

        if f == 'activity':
            if not re.match('^[0-9,]$', v):
                raise Exception('Invalid input')
            v = PDActivity.objects.get(id=int(v))
    
        if hasattr(pd, f):
            setattr(pd, f, v)
            pd.save()
        else:
            raise Exception('invalid field' + f)
    
        response_dict = { "success":True, "message": "Done" }

        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')


@login_required
def playdate_in_place_save_date(request, playdate_id):
    if request.user.is_authenticated():
        date_str = request.POST.get("date");
        time_start_str = request.POST.get("time_start");
        time_end_str = request.POST.get("time_end"); 
        errors = []
        date_good = True
        if not re.match('^\d{1,2}/\d{1,2}/\d{4}$', date_str):
            errors.append("date not selected or is invalid")
            date_good = False
    
        if not re.match('^\d{1,2}:\d{2}\w{2}$', time_start_str):
            errors.append("start time not selected or is invalid" + str(time_start_str))
            date_good = False
    
    
        if not re.match('^\d{1,2}:\d{2}\w{2}$', time_end_str):
            errors.append("end time not selected or is invalid" + str(time_end_str))
            date_good = False
    
            
        if date_good:
            when_str = date_str + time_start_str
            when = datetime.strptime(when_str, '%m/%d/%Y%I:%M%p')           
            until_str = date_str + time_end_str
            until = datetime.strptime(until_str, '%m/%d/%Y%I:%M%p')
        else:
            raise Exception('bad dates passed' + str(errors))

        pd = Playdate.objects.select_related('organizer').get(id=playdate_id)
    
        if not pd.organizer == request.user:
            raise Exception('user is not allowed to make changes')
  
        event = list(pd.event.all())[0] 
        event.start=when
        event.end=until 
        event.save()
    
        response_dict = { "success":True, "message": "Done" }

        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')



def fb_login_build(request, opts, next_url, cancel_url, perms = settings.FB_LOGIN_PERMS ):

    query_string = {
        "return_session"  : 1,
        "session_version" : 3,
        "v"               : '1.0'
    }
    
    # load default config
    query_string.update({
        "api_key"    : settings.FB_API_KEY,
        "cancel_url" : cancel_url,
        "next"       : next_url,
        "req_perms"  : perms,
    })

    query_string.update(opts)
    
    url = "https://www.facebook.com/login.php?%s" % urllib.urlencode(query_string)    

    return HttpResponseRedirect(url)


def pd_fb_login(request, playdate_id, invite_id, opts={}):
    server_name = request.META['HTTP_HOST']

    fb_login_next_url = 'http://'+ server_name + '/' + reverse('pd_fb_auth', kwargs={"playdate_id":playdate_id, "invite_id": invite_id} )
                                                               
    fb_login_cancel_url = 'http://' + server_name +'/' + settings.FB_LOGIN_CANCEL_URL

    return fb_login_build(request, opts, fb_login_next_url, fb_login_cancel_url, perms = '')


def pd_fb_auth(request, playdate_id, invite_id, **kwargs):

    fb_uid = process_fb_auth(request)

    pdf = PlaydateInviteFB.objects.select_related('facebook_contact').get(id=invite_id, playdate=playdate_id)

    if not str(pdf.facebook_contact.facebook_id) == str(fb_uid):
        return HttpResponseRedirect(reverse("nl_home"))

    dict_for_storage = { 'id':str(pdf.playdate_id), 'current_status':pdf.status, 'contactfb':pdf.facebook_contact_id }

    if "pd_invites" in request.session:
        request.session["pd_invites"].update({ str(pdf.playdate_id):dict_for_storage  })
    else:
        request.session["pd_invites"] = { str(pdf.playdate_id):dict_for_storage } 

    return view_playdate(request, str(pdf.playdate_id), **kwargs)
    
    
    
def process_fb_auth(request):

    token = uid = fb_exists = None

    if request.session.has_key("fb_user"):
        if request.session["fb_user"].has_key("access_token"):
            token = str(request.session["fb_user"]["access_token"])
            uid = str(request.session["fb_user"]["uid"])

    if request.GET.has_key("session"):
        fb_user = simplejson.loads(request.GET["session"])
        request.session["fb_user"] = fb_user
        token = str(request.session["fb_user"]["access_token"])
        uid = str(request.session["fb_user"]["uid"])


    return uid

def invites_cv(playdate, request):
    invites_cv = []
    for invite in playdate.invites_list():
        if invite.is_user:
            invite.childview = create_childview(request.user, invite.to_child )
        invites_cv.append(invite)

    return invites_cv

def compare_pd(a,b):
    if a.playdate.get_event.start > b.playdate.get_event.start:
        return -1
    else:
        return 1

@login_required
@children_required
def list_playdates(request, child_id = None):

    children = None
    child = None
    view_schedule_children = None
    cv = None

    if child_id is not None:
        if not re.match('^[0-9]+$',child_id):
            raise Exception('Invalid input')
        try:
            child = Child.objects.select_related('album','photo','school').get(id=child_id)
            cv = ChildView(user=request.user, child=child)
            if not cv.can_view_child_schedule:
                raise Exception("You do not have permissions for this")
            if cv.is_child_mine:
                my_child = True
        except Child.DoesNotExist:
            raise Exception("Invalid input")

    all_friends = []
    children = []
    avail_list_ini = []
    if child is None or my_child == True:
        view_schedule_children = request.user.get_profile().view_schedule_children

    if child is None:
        for vsc in view_schedule_children:
            children.append(vsc.child)
            all_friends = all_friends + vsc.child.friends
        my_child = True
    else:
        all_friends = child.friends
        children.append(child)

    max = int(request.GET.get("view_more", 4))
    more = None
    view_more = None

    pdis = []
    avail_list_ini = []

    pdis = list(PlaydateInviteUser.objects.select_related('playdate','playdate__event').cache().filter(to_child__in=children).all())

    pdis = sorted(pdis, compare_pd)

    if all_friends:
        avail_list_ini = list(EventPlan.objects.select_related('child','event').cache().filter(event__start__gte=datetime.now(),status='2',child__in=all_friends).order_by('event__start').all()[:max+1])
    avail_list = []    
    
    iterator = 1
    
    for avail in avail_list_ini:
        if iterator > max:
            more = True
            view_more = max + 4
            break;
        iterator = iterator + 1
        avail_cv = ChildView(user=request.user, child=avail.child)
        if avail_cv.can_view_child_schedule:
            avail_list.append({ 'avail':avail, 'childview':avail_cv })

    playdates = []

    view_schedule_children = get_cv_list_from_ac(request.user, view_schedule_children)  

    pd_seen = {}
    for pdi in pdis:
        if not str(pdi.playdate_id) in pd_seen:
            playdates.append({ 'playdate': pdi.playdate, 'invites':invites_cv(pdi.playdate, request)})
            pd_seen[str(pdi.playdate_id)] = True
            
    ctx = {
            'view_schedule_children':view_schedule_children,
            'current_child':cv,
            'my_child':my_child,
            'playdates':playdates,
            'avail_list':avail_list,
            'cat_playdates': True,
            'more':more,
            'view_more':view_more,
           }

    template = 'playdates/list_playdates.html'
    return render_to_response(template, RequestContext(request, ctx))

def save_optional_info(request, playdate_id):
    if not re.match('^[0-9]+$',playdate_id): # user id    
        raise Exception("Invalid Playdate")


    if request.method == "POST":
        post = request.POST
        phone = post['phone']
        pickup_details = post.get('pickup_details', None)
        inv_type = post['inv_type']
        inv_id = post['inv_id']

        if not re.match('^[0-9]+$',inv_id):
            raise Exception('Invalid input - id')
        
        if not re.match('^[\w]+',inv_type):
            raise Exception('Invalid input - type')

        invite = None
        if inv_type == 'user':
            invite = PlaydateInviteUser.objects.get(id=inv_id)
        elif inv_type == 'email':
            invite = PlaydateInviteEmail.objects.get(id=inv_id)
        elif inv_type == 'facebook':
            invite = PlaydateInviteFB.objects.get(id=inv_id)

        invite.phone = phone
        invite.pickup_details = pickup_details
        invite.save()
        
    return HttpResponseRedirect(invite.playdate_url)
