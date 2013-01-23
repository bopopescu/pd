# Rendering & Requests
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import render_to_response, get_list_or_404

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from my_django_utils import PDEncoder, children_required

# Forms
from django.views.decorators.csrf import csrf_protect

# Settings
from django.conf import settings
from django.contrib.sites.models import Site

# Utils
import re, datetime, urllib
from django.contrib import messages

from profiles.models import Profile, Child, Adult_Child, ChildView, get_cv_list_from_ac, create_childview

from models import Friendship
import urllib, simplejson

from django.db import IntegrityError

# Locals (used only in Friends)
from friends.models import *

@login_required
def add_friend(request):
    if request.method == 'POST':        
        post = request.POST        
        message = ''
        how_related = "4"
        source = ''
           
        if 'how_related' in post:
            how_related = post['how_related']

        if 'message' in post:
            message=post['message']

        if 'source' in post:
            source = post['source']

        from_child_id=post['from_child']
        to_child_id=post['to_child']
        to_user_id=post['to_user']

        if not re.match('^[0-9]+$',from_child_id):
            raise("Invalid input")

        if not re.match('^[0-9]+$',to_child_id):
            raise("Invalid input")

        if not re.match('^[0-9]+$',to_user_id):
            raise("Invalid input")
        
        from_user = request.user
        to_user = User.objects.select_related('_profile_cache').get(id=to_user_id)
        from_child = Child.objects.get(id=from_child_id)
        to_child = Child.objects.get(id=to_child_id)

        cv = ChildView(to_user, to_child)

        if not cv.can_edit_child_playlist:
            raise Exception('User does not have permissions to approve request')

        cv = ChildView(from_user, from_child)

        if not cv.can_edit_child_playlist:
            raise Exception('User does not have permissions to send request')

        
        # hardcode TODO
        from friends.models import FriendshipInvitation;
        invitation = FriendshipInvitation(
            from_user=from_user, 
            to_user=to_user, 
            from_child=from_child,
            to_child=to_child,
            message=message,
            how_related=how_related, 
            status="2"
        )
        try:
            invitation.save_and_notify()
        except IntegrityError:
            pass
        
        response_dict = { "success":"true", "message":"Invitation Sent"}
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
        
@login_required
def confirm_friend(request):
    if request.method == 'POST':        
        post = request.POST        
        from_child_id=post['from_child']
        to_child_id=post['to_child']


        if not re.match('^[0-9]+$',from_child_id):
            raise("Invalid input")

        if not re.match('^[0-9]+$',to_child_id):
            raise("Invalid input")


        from_child = Child.objects.get(id=from_child_id)        
        to_child = Child.objects.get(id=to_child_id)
        cv = ChildView(request.user, to_child)

        if not cv.can_edit_child_playlist:
            raise Exception('User does not have permissions to approve request')

        friend_invitation = None
        try:
            friend_invitation = FriendshipInvitation.objects.get(from_child=from_child, to_child=to_child)
        except:
            raise Exception('No such friend request')

#        try:
        friend_invitation.accept_and_notify()
#        except:
#            pass
       
        response_dict = { "success":"true", "message":"Friend Confirmed"}
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
        
@login_required
def remove_friend_suggestion(request):
    if request.method == 'POST':        
        post = request.POST        
        suggestion_id=post['suggestion_id']

        if not re.match('^[0-9]+$',suggestion_id):
            raise("Invalid input")

        fs = FriendSuggestion.objects.get(id=suggestion_id)
        cv = ChildView(request.user, fs.child)

        if not cv.can_edit_child_playlist:
            raise Exception('User does not have permissions to approve request')

        fs.active = False
        fs.save()

        response_dict = { "success":"true", "message":"Suggestion Removed"}
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')


@login_required
def remove_contact(request, contact_id, contact_type):
    contact_id = int(contact_id)

    if contact_type == 'fb':
        contact = ContactFB.objects.get(owner=request.user, id=contact_id)
        contact.removed = True
        contact.save()
    
    if contact_type == 'email':
        contact = ContactEmail.objects.get(owner=request.user, id=contact_id)
        contact.removed = True
        contact.save()

    messages.add_message(request, messages.INFO, 'Contact Removed')

    return HttpResponseRedirect(reverse("contacts"))


@login_required
@children_required
def suggested_friends(request, child_id = None):
    children = None
    can_manage_child_playlist = False
    child = None
    manage_playlist_children = None
    cv = None

    if child_id:
        if not re.match('^[0-9]+$',child_id):
            raise Exception('Invalid input')
        try:
            child = Child.objects.select_related('photo','album','school').get(id=child_id)
        except Child.DoesNotExist:
            raise Exception("Invalid input")

    if child is not None:
        cv = ChildView(user=request.user, child=child)
        if not cv.can_edit_child_playlist:
            raise Exception("You do not have permissions for this")

        if cv.is_child_mine:
            my_child = True

    if child is None or my_child == True:
        manage_playlist_children = request.user.get_profile().manage_playlist_children

        if child is None:
            child = manage_playlist_children[0].child

    if manage_playlist_children is None:
        manage_playlist_children = request.user.get_profile().manage_playlist_children

    if cv is None:
        cv = ChildView(user=request.user, child=child)

    
    manage_playlist_children = get_cv_list_from_ac(request.user, manage_playlist_children)  

    friend_suggestion_list = list(FriendSuggestion.objects.cache().select_related('child','child__photo','child__album','suggested_child','suggested_child__photo','suggested_child__school','suggested_child__album').filter(child=child, active=True).all()[:10])

#    child_list = []
#    for sf in friend_suggestion_list:
#        child_list.append(sf.suggested_child)
    suggested_list = create_list_of_children_and_parents(request, friend_suggestion_list)


#    tolog(str(cv.get_profile()))

    ctx = {
        'suggested_list': suggested_list,
        'current_child': cv,
        'manage_playlist_children': manage_playlist_children,
        'profile': request.user.get_profile(),
        'cat_friends': True,
    }   

    template = 'friends/suggested_friends.html'
    return render_to_response(template, RequestContext(request, ctx))
    

def create_list_of_children_and_parents(request, friend_suggestion_list):
    result = []
    for child_suggestion in friend_suggestion_list:
        child = child_suggestion.suggested_child
        parent_list = []
        for parent in child.parents:
            parent_list.append(parent.get_profile().get_profile())

        childview = create_childview(user=request.user, child=child)

        result.append({ 'child':childview.profile, 'parents':parent_list, 'suggestion_id':child_suggestion.id })

    return simplejson.dumps(result, cls=PDEncoder)


@login_required
@children_required
def view_playlist(request, child_id=None, **kwargs):

# can be optimized to do a single SQL query to the database to pull adult_child relations
# and a single call to get all friends (cached to memcached)
    my_view_children = None
    can_edit_child_playlist = False
    child = None
    cv = None

    if child_id:
        if not re.match('^[0-9]+$',child_id):
            raise Exception('Invalid input')
        try:
            child = Child.objects.select_related('photo','album','school').get(id=child_id)
        except Child.DoesNotExist:
            raise Exception("Invalid input")


    my_child = False
    if child is not None:    
        cv = ChildView(user=request.user, child=child)
        if not cv.can_view_child_playlist:
            raise Exception("You do not have permissions for this")

        if cv.is_child_mine:
            my_child = True

    profile = request.user.get_profile()
    if child is None or my_child == True:
        my_view_children = get_cv_list_from_ac(request.user, profile.view_playlist_children)  
        
        if child is None:
            child = my_view_children[0].child
            cv = my_view_children[0]
            my_child = True

    if cv is None:
        cv = ChildView(user=request.user, child=child)

    my_edit_children = get_cv_list_from_ac(request.user, profile.edit_playlist_children)  

    cat_friends = False
    if my_child:
        cat_friends = True,

    ctx = {
        'profile': profile,
        'current_child': cv,
        'my_view_children': my_view_children,
        'my_edit_children':my_edit_children,
        'my_child':my_child,
        'cat_friends':cat_friends,
    }   

    template = 'friends/view_playlist.html'
    return render_to_response(template, RequestContext(request, ctx))

@login_required
def get_profiles(request, child_id):
    if not re.match('^[0-9]+$',child_id):
        raise Exception('Invalid input')

    if request.method == 'POST':
    
        offset = request.POST.get("offset", None)
        limit = request.POST.get("limit", None)

#    offset = '0'
#    limit = '1'
    
        if not re.match('^[0-9]+$',offset):
            raise Exception('Invalid input')
    
        if not re.match('^[0-9]+$',limit):
            raise Exception('Invalid input')
    
        try:
            child = Child.objects.select_related('album','photo','school').get(id=child_id)
        except Child.DoesNotExist:
            raise Exception("Invalid input")    
    
        cv = ChildView(user=request.user, child=child)
        if not cv.can_view_child_playlist:
            raise Exception("You do not have permissions for this")

        max = int(offset)+int(limit)
        offset = int(offset)
        result = []
        friends_all = child.friends
        friends = friends_all[offset:max]

        if len(friends):

            friend_id_dict = {}
            for obj in friends:
                friend_id_dict[obj.id] = []
            
            friend_ids = friend_id_dict.keys()

            friend_parents_ac = list(Adult_Child.objects.select_related('adult','adult___profile_cache','adult___profile_cache__photo','adult___profile_cache__album').filter(child__in=friend_ids, relation='P'))

            for fpac in friend_parents_ac:
                friend_id_dict[fpac.child_id].append(fpac.adult)

            for friend in friends:
                parent_list = []
                for parent in friend_id_dict[friend.id]:
                    parent_list.append(parent.get_profile().get_profile())    
                childview = create_childview(user=request.user, child=friend)
    
                result.append({ 'child':childview.profile,
                               'key':childview.key(),
                               'parents':parent_list, 
                               'is_friend':childview.is_in_friends, 
                               'is_mine':childview.is_child_mine,
                               'is_pending_sent':childview.is_pending_sent,
                               'is_pending_received':childview.is_pending_received,
                               })
    
        return HttpResponse(simplejson.dumps(result, cls=PDEncoder), mimetype='application/javascript')



# PD users +
# FB friends who you invited +
# Email contacts who you invited
@login_required
@children_required
def contacts(request):

    contacts = []
    
    contacts_email = list(ContactEmail.objects.filter(owner=request.user, invited=True, removed=False).all())


    for contact in contacts_email:
        temp_hash = {}
        if contact.first_name:
            temp_hash['name'] = contact.first_name + ' ' + contact.last_name
        else:
            temp_hash['name'] = contact.email
        temp_hash['sort'] = temp_hash['name'].lower()

        temp_hash['type'] = 'email'
        temp_hash['email'] = contact.email
        temp_hash['id'] = contact.id
        temp_hash['key'] = contact.key
        contacts.append(temp_hash)    
    
    contacts_fb = list(ContactFB.objects.filter(owner=request.user, invited=True, removed=False).all())

    for contact in contacts_fb:
        temp_hash = {}
        temp_hash['name'] = contact.first_name + ' ' + contact.last_name
        temp_hash['sort'] = temp_hash['name'].lower()
        temp_hash['type'] = 'fb'
        temp_hash['fbid'] = contact.facebook_id
        temp_hash['id'] = contact.id
        temp_hash['key'] = contact.key

        contacts.append(temp_hash)    

    child_ac_list = request.user.get_profile().view_schedule_children
    friends = []
    for ac in child_ac_list:
        friends = friends + ac.child.friends

    friend_id_hash = {}
    for friend in friends:
        friend_id_hash[friend.id] = friend
        
    friend_ids = friend_id_hash.keys()
    
    friend_parents_ac = []
    if friend_ids:
        friend_parents_ac = list(Adult_Child.objects.select_related('adult','adult___profile_cache','adult___profile_cache__photo','adult___profile_cache__album', 'child','child__photo','child__school','child__album').filter(child__in=friend_ids, relation='P'))

    contacts_pd_children = {}
    for ac in friend_parents_ac:
        if ac.adult.id in contacts_pd_children:
            contacts_pd_children[ac.adult.id].append( create_childview(user=request.user, child=ac.child) )
        else:
            contacts_pd_children[ac.adult.id] = [ create_childview(user=request.user, child=ac.child) ]

    seen_adult = {}
    for ac in friend_parents_ac:
        if ac.adult.id in seen_adult:
            continue
        else:
            seen_adult[ac.adult.id] = 1
            
        temp_hash = {}
        contact = ac.adult.get_profile()
        temp_hash['name'] = contact.first_name + ' ' + contact.last_name
        temp_hash['sort'] = temp_hash['name'].lower()
        temp_hash['type'] = 'pd'
        temp_hash['children'] = contacts_pd_children[ac.adult.id]
        temp_hash['id'] = contact.id
        temp_hash['profile'] = contact.get_profile()
        
        contacts.append(temp_hash)
        
    from operator import itemgetter 
    contacts.sort(key=itemgetter('sort'))

    ctx = { 'contacts':contacts, 'cat_contacts':True }
    
    template = 'friends/contacts.html'
    return render_to_response(template, RequestContext(request, ctx))


def accept_invitation(request, confirmation_key):
    return True
