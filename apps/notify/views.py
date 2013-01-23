from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.conf import settings

from notify.utils import format_quote
from django.http import Http404, HttpResponse, HttpResponseRedirect
import time

from profiles.models import create_childview
import urllib, simplejson
import datetime
from django.contrib import messages

from my_django_utils import PDEncoder, get_status_date_format

from models import *
from mydebug import *
import re

cat_map = {
    'M':'Message',
    'P':'Playdate Request',
    'F':'Friend Request',
    'S':'Sent',
    '0':None   
}

@login_required
def inbox(request, template_name='messages/inbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    message_list = None
    type='received'
    category= {}
    filter = request.GET.get("filter", None)

    if filter is not None:
        if cat_map[filter] is not None:
            category = { 'category': cat_map[filter] }

    message_list = InternalMessage.objects.inbox_for(request.user, **category)

    pd_message_list = []
    for message in message_list:
        pd_message_list.append(ReceivedMessage(message))

    return render_to_response(template_name, {
        'message_list': pd_message_list,
        'type': type,
        'cat_messages': True,
        'filter': filter,

    }, context_instance=RequestContext(request))




@login_required
def outbox(request, template_name='messages/outbox.html'):
    """
    Displays a list of received messages for the current user.
    Optional Arguments:
        ``template_name``: name of the template to use.
    """
    message_list = None
    type = None
    type='sent'
    category= {}

    filter = request.GET.get("filter", None)

    if filter is not None:
        if cat_map[filter] is not None:
            category = { 'category': cat_map[filter] }

    if filter is not None:
        category = { 'category': cat_map[filter] }

    message_list = InternalMessage.objects.outbox_for(request.user, **category)

    pd_message_list = []
    for message in message_list:
        pd_message_list.append(SentMessage(message))

    return render_to_response(template_name, {
        'message_list': pd_message_list,
        'type': type,
        'cat_messages': True,
        'filter': filter,

    }, context_instance=RequestContext(request))


@login_required
def trash(request, template_name='messages/trash.html'):
    """
    Displays a list of deleted messages. 
    Optional arguments:
        ``template_name``: name of the template to use
    Hint: A Cron-Job could periodicly clean up old messages, which are deleted
    by sender and recipient.
    """
    message_list = InternalMessage.objects.trash_for(request.user)
    return render_to_response(template_name, {
        'message_list': message_list,
        'cat_messages': True,

    }, context_instance=RequestContext(request))

@login_required
def reply(request, message_id, template_name='messages/compose.html', success_url=None):

    parent_msg = InternalMessage.objects.select_related('recipient','sender').get(id=message_id)
    
    if parent_msg.sender != request.user and parent_msg.recipient != request.user:
        raise Http404
    
    if request.method == "POST":
        sender = request.user
        recipient_id = request.POST["recipient"]
        recipient = User.objects.get(id=recipient_id)
        body = request.POST["body"]
        subject = "RE: " +parent_msg.subject

        msg = InternalMessage( sender = sender, recipient = recipient, subject = subject, body = body, parent_msg=parent_msg.id )
        msg.save()

        ctx = {
            'to_user':recipient.get_profile(),
            'from_user':sender.get_profile(),
        }

        email_pref = get_message_preference(recipient, 'user_messages')

        if email_pref:
            send_email(recipient.email, 'message_received', ctx)
        
        if success_url is None:
            success_url = reverse('messages_inbox')
        return HttpResponseRedirect(success_url)
    else:
        pass
        # not dealing with this yet.
        # here would go the non-js version of replying to a message
    
    
    return render_to_response(template_name, { }, context_instance=RequestContext(request))

@login_required
def delete(request, message_id, success_url=None):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely. 
    A cron-job should prune the database and remove old messages which are 
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.
    
    You can pass ?next=/foo/bar/ via the url to redirect the user to a different
    page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
    """
    user = request.user
    now = datetime.datetime.now()
    message = get_object_or_404(InternalMessage, id=message_id)

    deleted = False
    if request.GET.has_key('next'):
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == user:
        message.recipient_deleted_at = now
        deleted = True
    if deleted:
        message.save()
#        messages.add_message(request, messages.INFO, 'Message deleted')
        return HttpResponseRedirect(get_return_url(request))
    raise Http404

@login_required
def undelete(request, message_id, success_url=None):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    user = request.user
    message = get_object_or_404(InternalMessage, id=message_id)
    undeleted = False
    if success_url is None:
        success_url = reverse('messages_inbox')
    if request.GET.has_key('next'):
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = None
        undeleted = True
    if message.recipient == user:
        message.recipient_deleted_at = None
        undeleted = True
    if undeleted:
        message.save()
        return HttpResponseRedirect(success_url)
    raise Http404

@login_required
def view(request, message_id):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either 
    the sender or the recipient. If the user is not allowed a 404
    is raised. 
    If the user is the recipient and the message is unread 
    ``read_at`` is set to the current datetime.
    """
    user = request.user
    now = datetime.datetime.now()
#    message = get_object_or_404(InternalMessage, id=message_id)
    raw_message = InternalMessage.objects.select_related('sender','recipient','sender___profile_cache','sender___profile_cache__photo').get(id=message_id)
    message = None
    if raw_message.sender == user:
        message = SentMessage(raw_message)
    elif raw_message.recipient == user:
        message = ReceivedMessage(raw_message)
    else:        
        raise Http404

    message.mark_read()

    if message.show_as_message:
        return view_message(request, message)
    elif message.show_as_playdate:
        return view_pd_request(request, message)
    elif message.show_as_friend:
        return view_f_request(request, message)
    else:
        raise Exception('invalid message type')

    raise Exception('Should not be here')

def view_message(request, message):
    template_name='messages/view.html'
    return render_to_response(template_name, { 'message': message, 'cat_messages': True, 'return_url': get_return_url(request), }, context_instance=RequestContext(request))

def get_return_url(request):

    return_val = request.GET.get('return', None)

    if return_val is None:
        return reverse('messages_inbox')
    elif return_val == 'inbox':
        return reverse('messages_inbox')
    elif return_val == 'outbox':
        return reverse('messages_outbox')
    
def view_f_request(request, message):
    
    from friends.models import FriendshipInvitation
    ai = message.associated_item
    tolog(ai)
    fi = FriendshipInvitation.objects.cache().select_related('to_user','to_user___profile_cache','to_child','from_child','from_child__photo','from_child__album','from_child__school').get(id=message.associated_item)

    to_child = fi.to_child
    to_user = fi.to_user
    to_child_cv = create_childview(request.user, to_child)
    from_child = fi.from_child
    from_child_cv = create_childview(request.user, from_child)
    from_parents = from_child.parents
    from_caregiver = from_child.caregivers

    ctx = {
            'message':message,
            'fi':fi,
            'from_user':fi.from_user,
            'to_child':to_child_cv,
            'to_user':to_user,      
            'from_child':from_child_cv,
            'from_parents':from_parents,
            'from_caregiver':from_caregiver,
            'cat_messages': True,
            'return_url': get_return_url(request),
           }
    
    template_name='messages/view_f_request.html'
    return render_to_response(template_name, ctx, context_instance=RequestContext(request))


def view_pd_request(request, message):
    return HttpResponseRedirect(message.get_item_url)

def now():
    import datetime
    return datetime.datetime.now()


def dt_from_epoch(epoch):
    import datetime
    return datetime.datetime.fromtimestamp(float(epoch))

# HERE

@login_required
def delete_update(request):
    if request.method == "POST":
        id = request.POST.get("id", None)
        our_update = True
        failed = False
        try:
            up = Update.objects.get(id=id, owner=request.user)
            up.deleted = True
            up.save()
        except Update.DoesNotExist:
            our_update = False
        
        if not our_update:
            try:
                uup = UserUpdate.objects.get(update = id, user = request.user)
                uup.delete()
            except UserUpdate.DoesNotExist:
                failed = True
            
        if failed:
            response_dict = { "success":False, "message": "Failed" }
        else:
            response_dict = { "success":True, "message": "Done" }
    
        return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')



@login_required
def get_updates(request):
    timestamp = None

    timestamp = max_limit = None
    
    if request.method == "POST":
        timestamp = request.POST.get("timestamp", None)
        max_limit = request.POST.get("max_limit", None)

    if max_limit is None or max_limit < 1:
        max_limit = 10
    else:
        int(max_limit) # Exception if not integer I am assuming.        

    updates_qs = None

    timestamp = int(timestamp)
    if timestamp is None or timestamp == 0:
        updates_qs = request.user.updates.select_related('update').filter(update__deleted='0')[:max_limit]
    else:
        updates_qs = request.user.updates.select_related('update').filter(added__gt=dt_from_epoch(timestamp), update__deleted='0')

    updates = []
    
    for update in updates_qs:
        when = get_status_date_format(update.update.when)
        
        updates.append({ 'html': update.update.message, 'when':when, 'id':update.update.id })
        
    response_dict = { 'updates': updates, 'timestamp': int(time.time()) }

    return HttpResponse(simplejson.dumps(response_dict, cls=PDEncoder), mimetype='application/javascript')
    


# TODO - add checks to make sure no one is including other people's children in their status updates?
@login_required
def update_status(request, **kwargs):
    if request.method == 'POST':        
        
        post = request.POST        
        status_children = post.getlist('status_children')
        status = post['status']
        hours_in_the_future = post['status_when']
        hours_in_the_future = int(hours_in_the_future)

        for child_id in status_children:
            if not re.match('^[0-9]+$',child_id):
                raise Exception('Invalid input')

        actor_children_fnames = []

        from profiles.models import Child
        children = []
        for child_id in status_children:
            try:
                child = Child.objects.get(id=child_id)
                children.append(child)
                actor_children_fnames.append(child.first_name)
            except Child.DoesNotExist:
                raise Exception("Invalid input")

        ctx = {
            'actor':request.user.get_profile(),
            'actor_children': ' , '.join(actor_children_fnames),
            'status': status,
            'when': hours_in_the_future,                   
        }

        up = create_status_update(request.user, 'status_update', ctx, hours_in_the_future)

        create_user_update(request.user, up)

        exclude_users = []
        for child in children:
            exclude_users = exclude_users + create_user_update_for_child_playlist_adults(child, up, exclude = exclude_users)
    
        response_dict = { "success":True, "message":"Updated"}    

        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')


@login_required
def send_message(request, **kwargs):
    if request.method == 'POST':        
        post = request.POST        
        message = post.get('message',None)
        subject = post.get('subject',None)
        to_user_id = post.get('to_user',None)

        if not re.match('^[0-9]+$',to_user_id):
            raise("Invalid input")

        from_user = request.user
        to_user = User.objects.get(id=to_user_id)

        message = InternalMessage(subject=subject, body=message, sender=from_user, recipient=to_user)
        message.save()

        ctx = {
            'to_user':to_user.get_profile(),
            'from_user':from_user.get_profile(),
        }

        email_pref = get_message_preference(to_user, 'user_messages')

        if email_pref:
            send_email(to_user.email, 'message_received', ctx)

        response_dict = { "success":"true", "message":"Message Sent"}
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
