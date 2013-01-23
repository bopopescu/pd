from django.db import models
from django.conf import settings
from django.db.models import signals

from django.core.mail import send_mail, get_connection

from django.contrib.sites.models import Site

from django.template import Origin, Template, Context
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext, get_language, activate

from mydebug import *
from types import ListType
from django.contrib.auth.models import User

from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse


from mailer import send_html_mail

from cachebot.managers import CacheBotManager
import datetime

QUEUE_ALL = getattr(settings, "NOTIFICATION_QUEUE_ALL", False)

# medium for message
MESSAGE_MEDIA = (
    ("update", _("Update")),
    ("message", _("Message")),
    ("email", _("Email")),
    ("facebook", _("Facebook")),
)


MESSAGE_PARTS = (
    ("subject", _("Subject")),
    ("body", _("Body"))
)


class Message(models.Model):    
    
    def get_content(self, type, part="body"):
        try:
            content = MessageContent.objects.get(medium=self.medium, type=type, part=part)
            return content.content
        except MessageContent.DoesNotExist:
            return None
            
    def send(self):
        return get_message_preference(self.user, self.message_type, self.medium)

    class Meta:
        abstract=True
        app_label='notify'


class MessagePreference(models.Model):
    """
    Indicates, for a given user, whether to send notifications
    of a given type to a given medium.
    """

    user = models.ForeignKey(User, verbose_name=_('user'))
    type = models.CharField(_('Message Type'), max_length=40)
    send = models.BooleanField(_('Send?'))
    objects = CacheBotManager()

    class Meta:
        verbose_name = _("message preference")
        verbose_name_plural = _("message preferences")
        unique_together = ("user", "type")
        app_label='notify'

class MessagePreferenceDefaults(models.Model):
    type = models.CharField(_('Message Type'), max_length=40)
    send = models.BooleanField(_('Send?'))
    objects = CacheBotManager()

    class Meta:
        verbose_name = _("message preference default")
        verbose_name_plural = _("message preference defaults")
        unique_together = ("type", )
        app_label='notify'
    
def create_message_pref_default(type, send):
    try:
        mpd = MessagePreferenceDefaults.objects.get(type=type)
        updated = False
        if mpd.send != send:
            mpd.send = send
            updated = True
        if updated:
            mpd.save()
    except MessagePreferenceDefaults.DoesNotExist:
        MessagePreferenceDefaults(type=type, send=send).save() 

def get_message_preference(user, type):
    send = False

    mp = get_message_preferences(user)

    return mp[type]

def get_message_preferences(user):
    current_preferences = {}
    default_preferences = list(MessagePreferenceDefaults.objects.cache().all())
    for pref in default_preferences:
        current_preferences[pref.type] = pref.send

    try:
        user_preferences = list(MessagePreference.objects.filter(user=user).all())
        for pref in user_preferences:
            current_preferences[pref.type] = pref.send 

        return current_preferences
        
    except MessagePreference.DoesNotExist:
        return current_preferences

def save_message_preferences(user, new_preferences):
    old_preferences = get_message_preferences(user)
    for type in old_preferences.keys():
        if not old_preferences[type] == new_preferences[type]:
            try:
                preference = MessagePreference.objects.get(user=user, type=type)
                preference.send = new_preferences[type]
                preference.save()
            except:
                MessagePreference(user=user, type=type, send=new_preferences[type]).save()


            
UPDATE_TYPES = (
    ("general",_("General")),
    ("photo",_("Photo Related")),
    ("playlist",_("Playlist Related")),
    ("playdate", _("Playdate Related")),                
)

class UpdateQueueBatch(models.Model):
    pickled_data = models.TextField()
    class Meta:
        app_label='notify'


class Update(Message):
    owner = models.ForeignKey(User, verbose_name=_('user'), related_name="my_updates", db_index=True)
    message = models.TextField(_('message'))
    update_type = models.CharField(_('update type'), max_length=10, choices=UPDATE_TYPES, default="general")
    when = models.DateTimeField(_('added'), default=datetime.datetime.now)
    added = models.DateTimeField(_('added'), default=datetime.datetime.now)
    archived = models.BooleanField(_('archived'), default=False)
    deleted = models.BooleanField(_('deleted'), default=False)

    medium='update'

    objects = CacheBotManager()
    
    

    def __unicode__(self):
        return self.message

    def archive(self):
        self.archived = True
        self.save()

    def is_unseen(self):
        """
        returns value of self.unseen but also changes it to false.

        Use this in a template to mark an unseen notice differently the first
        time it is shown.
        """
        unseen = self.unseen
        if unseen:
            self.unseen = False
            self.save()
        return unseen

    class Meta:
        ordering = ["-added"]
        verbose_name = _("update")
        verbose_name_plural = _("updates")
        app_label='notify'


def create_update(user, message_type, ctx = {}, update_type = "general"):
    message_tmpl = Template(get_message_content('update', message_type))
    context = Context(ctx)
    update = Update.objects.create(owner=user, message=message_tmpl.render(context), update_type = update_type)
    return update

def create_status_update(user, message_type, ctx = {}, hours_in_the_future = None, update_type = "general"):
    message_tmpl = Template(get_message_content('update', message_type))
    context = Context(ctx)
    now = datetime.datetime.now()
    when = now
    if hours_in_the_future is not None:
        when = when + datetime.timedelta(hours=hours_in_the_future)
    update = Update.objects.create(owner=user, message=message_tmpl.render(context), added=now, when=when, update_type = update_type)
    return update




def send_update(*args, **kwargs):
    queue_flag = kwargs.pop("queue", False)
    now_flag = kwargs.pop("now", False)
    assert not (queue_flag and now_flag), "'queue' and 'now' cannot both be True."
    if queue_flag:
        return queue_update(*args, **kwargs)
    elif now_flag:
        return create_update(*args, **kwargs)
    else:
        if QUEUE_ALL:
            return queue_update(*args, **kwargs)
        else:
            return create_update(*args, **kwargs)
        

def queue_update(users, message, ctx = {}, update_type = None):
    """
    Queue the notification in NoticeQueueBatch. This allows for large amounts
    of user notifications to be deferred to a seperate process running outside
    the webserver.
    """
    if not isinstance(users, ListType):
        users = [ users ]

    if isinstance(users, QuerySet):
        users = [row["pk"] for row in users.values("pk")]
    else:
        users = [user.pk for user in users]

    notices = []
    for user in users:
        notices.append((user, message, ctx, update_type))
    UpdateQueueBatch(pickled_data=pickle.dumps(notices).encode("base64")).save()


class UserUpdate(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'), related_name="updates", db_index=True)
    update = models.ForeignKey(Update, db_index=True)
    unseen = models.BooleanField(_('unseen'), default=True)
    archived = models.BooleanField(_('archived'), default=False)
    added = models.DateTimeField(_('added'), null=True, blank=True)

    objects = CacheBotManager()


    class Meta:
        ordering = ["-added"]
        app_label='notify'



def create_user_update(users, update, exclude = []):
    from collections import Iterable
    if not isinstance(users, Iterable):
        users = [ users ]

    users_updated = []
    for user in users:
        if len(exclude) and user in exclude:
            tolog("excluding" + str(user.id))
            continue

        uupdate = UserUpdate.objects.create(user=user, update=update, added=update.added ) 
        uupdate.save()
        users_updated.append(user)

    return users_updated


# tries not to send the same update to the same user
def create_user_update_for_child_playlist_adults(child, update, exclude = []):
    users_updated = []

    new_exclude = exclude
    for friend in child.friends:
        users_updated = users_updated + create_user_update(friend.adults, update, exclude=new_exclude)
        new_exclude = exclude + users_updated

    return users_updated




class InternalMessageManager(CacheBotManager):
# here we can add other types of filters - 
# playdate invites
# playlist requests
# 
    def inbox_for(self, user, **kwargs):
        """
        Returns all messages that were received by the given user and are not
        marked as deleted.
        """
        return self.cache().select_related('sender','sender___profile_cache').filter( recipient=user, recipient_deleted_at__isnull=True, **kwargs )

    def outbox_for(self, user, **kwargs):
        """
        Returns all messages that were sent by the given user and are not
        marked as deleted.
        """

        return self.cache().select_related('recipient','recipient___profile_cache','sender','sender___profile_cache').filter( sender=user, sender_deleted_at__isnull=True, category='Message' )

    def trash_for(self, user):
        """
        Returns all messages that were either received or sent by the given
        user and are marked as deleted.
        """
        return self.filter(
            recipient=user,
            recipient_deleted_at__isnull=False,
        ) | self.filter(
            sender=user,
            sender_deleted_at__isnull=False,
        )



MESSAGE_TYPES = (
    ("Message", "Message"),
    ("Playdate Request", "Playdate Request"),
    ("Friend Request", "Friend Request"),
)

class PDMessage(object):
    message = None

    def id(self):
        return self.message.id
    id = property(id)
   
    def body(self):
        return self.message.body
    body = property(body)

    def recipient(self):
        return self.message.recipient
    recipient = property(recipient)

    def sender(self):
        return self.message.sender
    sender = property(sender)

    def can_reply(self):
        return False
    can_reply = property(can_reply)

    def sent_at(self):
        return self.message.sent_at
    sent_at = property(sent_at)

    def read_at(self):
        return self.message.read_at
    read_at = property(read_at)

    def category(self):
        return self.message.category
    category = property(category)

    def associated_item(self):
        return self.message.associated_item
    associated_item = property(associated_item)

    def save(self):
        self.message.save()

    def get_item_url(self):
        if self.category == 'Playdate Request':
            return reverse("view_playdate", kwargs={"playdate_id":self.associated_item})

        raise Exception('No other items have urls')

    get_item_url=property(get_item_url)

    def sent_or_received(self):
        return type
    
    sent_or_received = property(sent_or_received)

    def deleteable(self):
        return True
    
    deleteable = property(deleteable)

    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is not None:
            return False
        return True
    new = property(new)



class SentMessage(PDMessage):
    type = 'Sent'

    def __init__(self, message):
        self.message = message

    def mark_read(self):
        if self.message.read_at_sender is None:
            self.message.read_at_sender = datetime.datetime.now()
            self.message.save()

    def read_at(self):
        return self.message.read_at_sender
    read_at = property(read_at)

    def category_verbose(self):
        if self.message.category == 'Friend Request':
            return 'Friend Request related message'
        elif self.message.category == 'Playdate Request':
            return 'Playdate Request related message'
        return self.message.category
    category_verbose = property(category_verbose)

    def subject(self):
        if self.category == 'Friend Request':
            return "Friend request sent"
        else:
            return self.message.subject
    subject = property(subject)

    def show_as_message(self):
        if self.category == 'Message':
            return True
        if self.category == 'Friend Request':
            return True
        
        return False
    show_as_message = property(show_as_message)

    def show_as_playdate(self):
        if self.category == 'Playdate Request':
            return True
        return False
    show_as_playdate = property(show_as_playdate)

    def show_as_friend(self):
        return False
    show_as_friend = property(show_as_friend)



class ReceivedMessage(PDMessage):
    type = 'Received'

    def __init__(self, message):
        self.message = message


    def mark_read(self):
        if self.message.read_at_recipient is None:
            self.message.read_at_recipient = datetime.datetime.now()
            self.message.save()

    def subject(self):
        return self.message.subject
    subject = property(subject)

    def read_at(self):
        return self.message.read_at_recipient
    read_at = property(read_at)

    def category_verbose(self):
        return self.message.category
    category_verbose = property(category_verbose)

    def can_reply(self):
        if self.message.respond:
            return True
        return False
    can_reply = property(can_reply)

    def deleteable(self):
        if self.category == 'Friend Request':
            return False
        return True
    deleteable = property(deleteable)


    def show_as_message(self):
        if self.category == 'Message':
            return True
        
        return False
    show_as_message = property(show_as_message)

    def show_as_playdate(self):
        if self.category == 'Playdate Request':
            return True
        return False
    show_as_playdate = property(show_as_playdate)

    def show_as_friend(self):
        if self.category == 'Friend Request':
            return True
        return False
    show_as_friend = property(show_as_friend)


    
class InternalMessage(Message):
    """
    A private message from user to user
    """
    subject = models.CharField(_("Subject"), max_length=120)
    body = models.TextField(_("Body"))
    sender = models.ForeignKey(User, verbose_name=_("Sender"), related_name='messages_sent', db_index=True)
    recipient = models.ForeignKey(User, null=True, blank=True, verbose_name=_("Recipient"), related_name='messages_received', db_index=True)
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    read_at_sender = models.DateTimeField(_("read at"), null=True, blank=True)
    read_at_recipient = models.DateTimeField(_("read at"), null=True, blank=True)    
    replied_at = models.DateTimeField(_("replied at"), null=True, blank=True)
    sender_deleted_at = models.DateTimeField(_("Sender deleted at"), null=True, blank=True)
    recipient_deleted_at = models.DateTimeField(_("Recipient deleted at"), null=True, blank=True)
    category = models.CharField(_('Medium'), max_length=20, choices = MESSAGE_TYPES, default="Message")
    associated_item = models.CharField(max_length=20, null=True, blank=True)
    parent_msg = models.CharField(max_length=20, null=True, blank=True)
    respond = models.BooleanField(_('respond'), default=True)

    #message_type = models.


    medium='message'
    
    objects = InternalMessageManager()

    def subject_received(self):
        if self.category == 'Friend Request':
            return self.subject
        else:
            return self.subject
        
    def subject_sent(self):
        if self.category == 'Friend Request':
            return "Friend request sent"
        else:
            return self.subject
    
    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is not None:
            return False
        return True
        
    def replied(self):
        """returns whether the recipient has written a reply to this message"""
        if self.replied_at is not None:
            return True
        return False
    
    def __unicode__(self):
        return self.subject
   
    def save(self, force_insert=False, force_update=False):
        if not self.id:
            self.sent_at = datetime.datetime.now()
        super(InternalMessage, self).save(force_insert, force_update) 
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        app_label='notify'

def create_message(sender, recipients, message_type, ctx, category=None, associated_item = None, respond=True):

    if category is None:
        category='Message'
    else:
        tolog('cate - ' + category)
    
    context = Context( ctx )  
  
    if not isinstance(recipients, ListType):
        recipients = [ recipients ]

    body_tmpl = Template(get_message_content('message', message_type))
    subject_tmpl = Template(get_message_content('message', message_type, 'subject'))

    for recipient in recipients:
        imsg = InternalMessage(subject=subject_tmpl.render(context), 
                               body = body_tmpl.render(context),
                               category=category, 
                               sender=sender, 
                               recipient=recipient,
                               associated_item=associated_item,
                               respond=respond
                               )
        imsg.save()

def create_message_anon(recipients, message_type, ctx, category= None, associated_item = None):
    context = Context( ctx )  

    if category is None:
        category='Message'

  
    if not isinstance(recipients, ListType):
        recipients = [ recipients ]

    body_tmpl = Template(get_message_content('message', message_type))
    subject_tmpl = Template(get_message_content('message', message_type, 'subject'))

# TODO: Need anonymous user for delivering messages from playdation and for users outside playdation
    sender = User.objects.get(id=1)

    for recipient in recipients:
        imsg = InternalMessage(subject=subject_tmpl.render(context), 
                               body = body_tmpl.render(context), 
                               sender=sender, 
                               recipient=recipient,
                               category=category,
                               associated_item=associated_item,
                               respond=False)
        imsg.save()
    



def inbox_count_for(user):
    """
    returns the number of unread messages for the given user but does not
    mark them seen
    """
    l = InternalMessage.objects.cache().filter(recipient=user, read_at_recipient__isnull=True, recipient_deleted_at__isnull=True).all()
    return len(l)


class FBPost(Message):
    medium = 'facebook'
    def __unicode__(self):
        return "FB Post"

    class Meta:
        app_label='notify'

def post_to_own_facebook(access_token, message_type, ctx, **kwargs):

    context = Context( ctx )  

    from account.graphapi import GraphAPI
    
    api=GraphAPI(access_token)

    body_tmpl = Template(get_message_content('facebook', message_type, 'body'))
    api.put_object("me", "feed", message= body_tmpl.render(context), **kwargs)
    return True       

def post_to_other_facebook(access_token, fb_id, message_type, ctx, **kwargs):

    context = Context( ctx )  

    from account.graphapi import GraphAPI
    
    api=GraphAPI(access_token)

    body_tmpl = Template(get_message_content('facebook', message_type, 'body'))

    api.put_object(fb_id, "feed", message= body_tmpl.render(context), **kwargs)
    return True       




class Email(Message):
    medium = 'email'
    
    def __unicode__(self):
        return "Email"
    
    class Meta:
        app_label='notify'


def send_email(recipients, type, ctx = {}, skip_footer = False):
    context = Context( ctx )  

    new_recipients = []  
    if not isinstance(recipients, ListType):
        new_recipients.append(recipients)

    if new_recipients:
        recipients = new_recipients

    header_tmpl = get_message_content('email','header')
    original_body_tmpl = get_message_content('email', type)


    subject_tmpl = Template(get_message_content('email', type, 'subject'))    
    footer_tmpl = get_message_content('email','basic_footer')
    if not skip_footer:
        footer_tmpl = get_message_content('email','footer')

    body_tmpl = Template(header_tmpl + original_body_tmpl + footer_tmpl)

    text_message='Text Message'

    try:
        text_tmpl = Template(get_message_content('email',type,'body_text'))
        text_message = text_tmpl.render(context)
    except:
        text_tmpl = Template(original_body_tmpl)
        text_message = text_tmpl.render(context)

    for recipient in recipients:
        recipient_list = [ ]
        recipient_list.append(recipient)
        context.update({ recipient:recipient })
        send_html_mail(subject_tmpl.render(context), text_message, body_tmpl.render(context), settings.DEFAULT_FROM_EMAIL, recipient_list)


def send_invite_email(recipient, invite_design, ctx = {}):
    context = Context( ctx )  

    subject_tmpl = Template(invite_design.subject)
    body_tmpl = Template(invite_design.html)

    recipient_list = [ ]
    recipient_list.append(recipient)
    context.update({ recipient:recipient })

    send_html_mail(subject_tmpl.render(context), 'text message', body_tmpl.render(context), settings.DEFAULT_FROM_EMAIL, recipient_list)





class MessageContent(models.Model):
    # friend_request, photo_tagged, added_child, etcc.
    type = models.CharField(_('Message Type'), max_length=40)
    # update , message, email, fbpost
    medium = models.CharField(_('Medium'), max_length=20, choices = MESSAGE_MEDIA)
    # subject vs body - some message types don't need a subject
    part = models.CharField(_('Message Part'), max_length=20, choices = MESSAGE_PARTS)
    # actual django content template string.
    content = models.TextField(_("Content"))
    objects = CacheBotManager()

    class Meta:
        unique_together = ("type","medium", "part")
        app_label='notify'

def create_message_content(medium, type, content, part = 'body'):
    try:
        message = MessageContent.objects.get(type=type, medium=medium, part=part)
        updated = False
        if content != message.content:
            message.content = content
            updated = True
        if updated:
            message.save()
    except MessageContent.DoesNotExist:
        MessageContent(type=type, medium=medium, part=part, content=content).save() 

def get_message_content(medium, type, part='body'):
    try:
        content = MessageContent.objects.get(medium=medium, type=type, part=part)
        return content.content
    except MessageContent.DoesNotExist:
        raise Exception('no content found for medium: ' + str(medium) + ' for type: "' + str(type)+'"')


