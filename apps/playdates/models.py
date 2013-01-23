from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from profiles.models import Child, create_childview
from schedule.models import Activity
from django.core.urlresolvers import reverse
from comments.models import Comment
from django.contrib.contenttypes import generic

from friends.models import *
from notify.models import create_message, create_update, send_email, send_invite_email, create_message_anon, post_to_other_facebook, post_to_own_facebook, get_message_preference
from photos.models import Album, Photo
from itertools import *
from mydebug import *
import simplejson
from playdates.invites import InviteDesign

from cachebot.managers import CacheBotManager

import datetime, re
    


class PDActivity(models.Model):
    name = models.CharField(_('Activity Name'), max_length=50)
    objects = CacheBotManager()

    class Meta:
        app_label='playdates'

def create_pd_activity(name):
    try:
        mpd = PDActivity.objects.get(name=name)
    except PDActivity.DoesNotExist:
        PDActivity(name=name).save() 

EXPIRE_OPTIONS = (
    ('24', '1 day from now'),
    ('48', '2 days from now'),
    ('72', '3 days from now'),
    ('96', '4 days from now'),
)


STATUS_OPTIONS = (
    ('1', 'Pending'),
    ('2', 'Scheduled'),
    ('3', 'Cancelled'),
)

class Playdate(Activity):
    type = 'playdate'
    organizer = models.ForeignKey(User)

    is_dropoff = models.BooleanField(_("Is this a dropoff"), default=True)        
    phone = models.CharField(_("phone"), max_length=15,null=False, blank=True)

    details = models.TextField(_("Details"), null=True, blank=True)
    max_participants = models.PositiveIntegerField(_("Maximum Number of Participants"), null=True, blank=True)
    expire_option = models.CharField(_("Expiration Option"), max_length=5, choices=EXPIRE_OPTIONS, null=True, blank=True)

    min_participants = models.PositiveIntegerField(_("Maximum Number of Participants"), null=True, blank=True)
    invite_design = models.ForeignKey(InviteDesign, null=True, blank=True)
    address = models.TextField(_("Address"), null=False)
    comments = generic.GenericRelation(Comment)
    photo = models.ForeignKey(Photo, null=True, blank=True, default=settings.DEFAULT_PROFILE_PHOTO_ID, db_index=True) #should be a constant
    album = models.ForeignKey(Album, null=True, blank=True, db_index=True, related_name='+')
    activity = models.ForeignKey(PDActivity, null=True, blank=True, db_index=True, related_name='+')
    status = models.CharField(_("Playdate Status"), max_length=2, choices=STATUS_OPTIONS, default='1')
    create_date = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)


    deleteable = False

    request_user = None
    _event = None
    _invites = None
    objects = CacheBotManager()


    class Meta:
        app_label='playdates'

    def scheduled(self):
        if self.status == '2':
            return True
        return False

    scheduled = property(scheduled)

    def canceled(self):
        if self.status == '3':
            return True
        return False

    canceled = property(canceled)


    def cancel(self):
        self.status = '3'
        self.save()
#        self.update_event_plans(self.status)

        ctx = {
               'organizer': self.organizer.get_profile(),
               'playdate':self,
        }

        message_type='playdate_canceled'

        self.notify_attending(ctx, message_type)


    def update_status(self):
        current_status = self.status

        new_status = '1'
        for invite in self.invites:
            if invite.yes and not invite.is_organizer:
                new_status = '2'

        if current_status != new_status:
            self.status = new_status
            self.save()

            if new_status == '2':
                self.update_event_plans(current_status)

    def update_event_plans(self, current_playdate_status):
        attending_children = []
        for invite in self.user_invites.all():
            if invite.yes:
                attending_children.append(invite.to_child_id)

        for ep in self.get_event.children.all():
            if ep.child_id in attending_children:
                ep.remove_availability_for_this_timeslot()

    def status_verbose(self):
        if self.status == '1':
            return 'Pending'
        elif self.status == '2':
            return 'Scheduled'
        elif self.status == '3':
            return 'Cancelled'
        else:
            raise Exception('invalid status')
        

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            album = Album(title="Playdate Photos", created_by=self.organizer)
            album.save()
            self.album=album;
            new=True
        
        super(Playdate, self).save(*args, **kwargs)
        if new:
            self.album.owner = self
            self.album.save()

    def get_event(self):
        if self._event is None:
            self._event = list(self.event.all())[0]
        
        return self._event

    get_event = property(get_event)

    def start(self):        
        return self.get_event.start
    
    start = property(start)
    
    def end(self):
        return self.get_event.end
    
    end = property(end)


    def set_profile_pic(self, np):
        self.photo=np
        self.save()

    def can_view_photo(self, user):
        can_view_children = {}
        for ac in user.get_profile().view_photo_children:
            can_view_children[ac.child_id] = True
            
        for u in self.user_invites.all():
            if u.to_child_id in can_view_children:
                return True
        return False


    def can_upload_photo(self, user):
        if not user.is_authenticated():
            return False
        can_upload_children = {}
        for ac in user.get_profile().upload_photo_children:
            can_upload_children[ac.child_id] = True

        for u in self.user_invites.all():
            if u.to_child_id in can_upload_children:
                return True

        return False

    def set_profile_language(self):
        return 'set as playdate album photo'

    
    def invites(self):
        if self._invites is None:
            self._invites = list(chain(self.user_invites.select_related('to_child','to_user','to_child__photo','to_child__album','to_child__school','to_user___profile_cache','to_user___profile_cache__photo','to_user___profile_cache__album').all(), 
                     self.email_invites.all(),
                     self.fb_invites.select_related('facebook_contact').all()))
        return self._invites


    def invites_list(self):
        return self.invites
    
    invites = property(invites)
                  
    def response_breakdown(self):
        response = {}

        for invite in self.invites_list():
            if not invite.current_status in response:
                response[invite.current_status] = [] 
            response[invite.current_status].append(invite)        
        return response
        
    def direct_url(self):
        return 'http://' + settings.WWW_HOST + reverse("view_playdate", kwargs={"playdate_id":self.id})

    direct_url = property(direct_url)

    def summary(self):
        summary_text = 'Playdate'
        if self.status == '1':
            summary_text = 'Pending Playdate'
        elif self.status == '2':
            summary_text = 'Confirmed Playdate'
        elif self.status == '3':
            summary_text = 'Cancelled Playdate'

        return(summary_text)
    
    def title(self):
        return("Playdate - " + self.event.start.strftime("%B %d, %Y"))

    title = property(title)

    name = property(title)

    def summary_body(self):
        return(self.details +" click <a href='"+ reverse("view_playdate", kwargs={"playdate_id":self.id}) +"'>here</a> for more details" )


    def notify_invitees(self, ctx, message_type, exclude_list = []):
        exclude_hash = { 'email': {}, 'facebook': {}, 'user': {} }

        dedupe_hash = { 'email': {}, 'facebook': {}, 'user': {} }
        for (type, id, obj) in exclude_list:
            exclude_hash[type][id] = obj
            dedupe_hash[type][obj.to] = True 
        
        for invite in self.invites:
            if invite.id in exclude_hash[invite.type]:
                continue

            if invite.type == 'user' and invite.to_user == self.organizer:
                continue

            if invite.to in dedupe_hash[invite.type]:
                continue
            else:
                dedupe_hash[invite.type][invite.to]=True

            ctx.update({ 'active_invite':invite,  })
            invite.notify_invitee(True, ctx, message_type)

    def notify_attending(self, ctx, message_type, exclude_list = []):
        exclude_hash = { 'email': {}, 'facebook': {}, 'user': {} }

        dedupe_hash = { 'email': {}, 'facebook': {}, 'user': {} }

        for (type, id, obj) in exclude_list:
            exclude_hash[type][id] = True
        
        for invite in self.invites:
            if invite.id in exclude_hash[invite.type]:
                continue

            if invite.type == 'user' and invite.to_user == self.organizer:
                continue

            if invite.to in dedupe_hash[invite.type]:
                continue
            else:
                dedupe_hash[invite.type][invite.to]=True

            if invite.yes:
                ctx.update({ 'active_invite':invite,  })
                invite.notify_invitee(True, ctx, message_type)


    def can_view_comments(self,user):
        return True



PD_INVITE_STATUS = (
    ("1", "Invited"),
    ("2", "Yes"),
    ("3", "No"),
    ("4", "Maybe"),
)    

class PlaydateInvite(models.Model):
    status = models.CharField(max_length=1, choices=PD_INVITE_STATUS, default='1')
    response = models.TextField(_("Invitee Text Response"), null=True, blank=True)
    phone = models.CharField(_("phone"), max_length=15, null=True, blank=True)
    pickup_details = models.CharField(_("phone"), max_length=250, null=True, blank=True)
   
    set_status_yes = False
    
    class Meta:
        app_label='playdates'
        abstract = True

    def child(self):
        return 'your child'

    def is_organizer(self):
        return False
    is_organizer = property(is_organizer)

    def accept(self, notify_friends=False):
        changed = False
        if not self.status == '2':
            self.status="2"
            self.save()
            self.playdate.update_status()
            self.set_status_yes = True
            changed=True
        return changed

   
    def save_and_invite(self, notify=True):
        self.save()

        self.invite_invitee('playdate_request_received')
    
    def decline(self):
        changed = False
        if not self.status == '3':
            self.status = "3"
            self.save()
            self.playdate.update_status()
            changed = True
            
        return changed
    

    def decline_and_notify(self, notify=True):
        changed = self.decline()

        if changed:
            self.notify_organizer(notify,'playdate_attendance_declined')


    def set_maybe(self):
        changed = False
        if not self.status == '4':
            self.status = "4"
            self.save()
            self.playdate.update_status()
            changed = True
            
        return changed
    

    def maybe_and_notify(self, notify=True):
        changed = self.set_maybe()

        if changed:
            self.notify_organizer(notify, 'playdate_attendance_maybe')

    def not_responded(self):
        if self.status == "1":
            return True
        return False

    nr = property(not_responded)


    def attending(self):
        if self.status == "2":
            return True
        False
    yes = property(attending)


    def not_attending(self):
        if self.status == "3":
            return True
        False

    no = property(not_attending)

    def maybe(self):
        if self.status == "4":
            return True
        False

    maybe=property(maybe)

    status_options = {
        '1':'noresponse',
        '2':'yes',
        '3':'no',
        '4':'noresponse',
    }

    def current_status(self):
        return self.status_options[self.status]
        
    current_status = property(current_status)

    def possessive(self):
        return 'their'
    possessive = property(possessive)


class PlaydateInviteEmail(PlaydateInvite):
    playdate = models.ForeignKey(Playdate, related_name="email_invites", db_index=True)
    email = models.EmailField(db_index=True)
    token = models.CharField(max_length=30)
    name = models.CharField(max_length=50, null=True, blank=True)
    organizer_child = models.ForeignKey(Child, related_name='my_email_invitees')
    is_user = False
    type = 'email'
    objects = CacheBotManager()

    class Meta:
        app_label='playdates'
        unique_together = ("playdate","email")

    def to(self):
        return self.email
    to = property(to)


    def playdate_url(self):
        return 'http://'+settings.WWW_HOST+reverse("view_playdate_with_token", kwargs={"playdate_id":self.playdate_id,"token":self.token})
    playdate_url = property(playdate_url)

    def assign_token(self):
        import os
        return (os.urandom(10).encode('hex'))


    def accept_and_notify(self, notify=True):
        changed = self.accept()

        if changed:
            self.notify_organizer(notify, 'playdate_attendance_confirmed')
    
            ctx = {
                   'invite': self,
                   'email': self.email,
                   'organizer': self.playdate.organizer,
                   'playdate':self.playdate,
                   'type':self.type,
            }
    
            self.playdate.notify_invitees(ctx, 'notify_attendees_accept', [ (self.type, self.id, self), ])



    def invite_invitee(self, message_type):
        ctx = {
            'email': self.email,
            'actor': self.playdate.organizer.get_profile(),
            'actor_child': self.organizer_child,
            'message':self.playdate.details,
            'playdate':self.playdate,
            'invite_id':self.id,
            'token':self.token,
            'playdate_url':self.playdate_url,

        }

        
        send_invite_email(self.email, self.playdate.invite_design, ctx)


    
    def notify_invitee(self, notify, ctx, message_type):
        if not notify:
            return True

        ctx.update({ 
          'this_invite':self,            
        })

        send_email(self.email, message_type, ctx)
        


    def notify_organizer(self, notify, message_type):

        if not notify:
            return True
        
        ctx = {
            'email': self.email,
            'actee': self.playdate.organizer.get_profile(),
            'actee_child': self.organizer_child,
            'response':self.response,
            'playdate':self.playdate,
            'active_invite':self,
        }

        create_message_anon(self.playdate.organizer, message_type, ctx)

        email_pref = get_message_preference(self.playdate.organizer, 'playdate_host_related')

        if email_pref:
            send_email(self.playdate.organizer.email, message_type, ctx)



class PlaydateInviteUser(PlaydateInvite):
    playdate = models.ForeignKey(Playdate, related_name="user_invites", db_index=True)
    to_user = models.ForeignKey(User, db_index=True)
    to_child = models.ForeignKey(Child, db_index=True)
    organizer_child = models.ForeignKey(Child, related_name='my_user_invitees')
    is_user = True
    childview = None
    type = 'user'

    objects = CacheBotManager()

    class Meta:
        app_label='playdates'
        unique_together = ("playdate","to_child")


    def is_organizer(self):
        if self.to_user == self.playdate.organizer:
            return True
        return False
    is_organizer = property(is_organizer)

    def to(self):
        return self.to_user.get_profile().name

    to = property(to)


    def child(self):
        return self.to_child.first_name

    def possessive(self):
        return self.to_user.get_profile().possessive

    possessive = property(possessive)

    def playdate_url(self):
        return 'http://'+settings.WWW_HOST+reverse("view_playdate", kwargs={"playdate_id":self.playdate_id})
    playdate_url = property(playdate_url)

    def accept_and_notify(self, notify=True):
        changed = self.accept()

        if changed:
            self.notify_organizer(notify, 'playdate_attendance_confirmed')
    
            ctx = {
                   'invitee': self.to_user,
                   'invitee_child':self.to_child,
                   'organizer': self.playdate.organizer,
                   'playdate':self.playdate,
                   'type':self.type,
                   'invite':self,
            }
    
            self.phone = self.to_user.get_profile().phone
    
            self.playdate.notify_invitees(ctx, 'notify_attendees_accept', [ (self.type, self.id, self), ])


    def invite_invitee(self, message_type):
        ctx = {
            'actor': self.playdate.organizer.get_profile(),
            'actor_child': self.organizer_child,
            'actee':self.to_user.get_profile(),
            'actee_child':self.to_child,
            'message':self.playdate.details,
            'playdate':self.playdate,
            'playdate_url':self.playdate_url,
        }

        create_message(self.playdate.organizer, self.to_user, message_type, ctx, category='Playdate Request', associated_item=self.playdate.id)

        send_invite_email(self.to_user.email, self.playdate.invite_design, ctx)


    
    def notify_invitee(self, notify, ctx, message_type):
        if not notify:
            return True

        ctx.update({ 
          'this_invite':self,            
        })


        create_message(self.playdate.organizer, self.to_user, message_type, ctx, respond=False)

        email_pref = get_message_preference(self.to_user, 'playdate_attendee_related')

        if email_pref:
            send_email(self.to_user.email, message_type, ctx)        

    def notify_organizer(self, notify, message_type):

        if not notify:
            return True
        
        ctx = {
            'actor':self.to_user.get_profile(),
            'actor_child':self.to_child,
            'actee': self.playdate.organizer.get_profile(),
            'actee_child': self.organizer_child,
            'response':self.response,
            'playdate':self.playdate,
            'active_invite':self,
        }

        create_message(self.to_user, self.playdate.organizer, message_type, ctx, respond=False)

        email_pref = get_message_preference(self.playdate.organizer, 'playdate_host_related')

        if email_pref:
            send_email(self.playdate.organizer.email, message_type, ctx)

        
class PlaydateInviteFB(PlaydateInvite):
    playdate = models.ForeignKey(Playdate, related_name="fb_invites", db_index=True)
    facebook_contact = models.ForeignKey(ContactFB)
    organizer_child = models.ForeignKey(Child, related_name='my_fb_invitees')
    is_user = False
    type = 'facebook'
    
    objects = CacheBotManager()

    class Meta:
        app_label='playdates'
        unique_together = ("playdate","facebook_contact")
        


    def accept_and_notify(self, notify=True):
        changed = self.accept()

        if changed:
            self.notify_organizer(notify, 'playdate_attendance_confirmed')
    
            ctx = {
                   'name':self.to,
                   'organizer': self.playdate.organizer,
                   'playdate':self.playdate,
                   'type':self.type,
            }
    
            self.playdate.notify_invitees(ctx, 'notify_attendees_accept', [ (self.type, self.id, self), ])
    
    
    def to(self):
        return self.facebook_contact.first_name + ' ' + self.facebook_contact.last_name

    to = property(to)

    def notify_invitee(self, notify, ctx, message_type):
        if not notify:
            return True

        # how do you notify facebook users? -- no email address - or is there? - i can collect it when they click through.

        return True

    def playdate_url(self):
        return 'http://'+settings.WWW_HOST+reverse("view_playdate_with_fb", kwargs={"playdate_id":self.playdate_id, "invite_id":self.id })
    playdate_url = property(playdate_url)
   
    def invite_invitee(self, message_type):
    
        ctx = {
            'actor': self.playdate.organizer.get_profile(),
            'actor_child': self.organizer_child,
            'message':self.playdate.details,
            'playdate':self.playdate,
            'invite_id':self.id,
            'contact': self.facebook_contact,
        }


        actee_fb_id = self.facebook_contact.facebook_id
        access_token = list(self.playdate.organizer.fbuser.all())[0].access_token
        args = {
                'link': self.playdate_url,
                'attribution':'Playdation',
                'name':'You Have a Playdate Invite',
                'description':"Playdation is what the other parents and I are now using to schedule our children's playdates.",
                'picture':'http://'+settings.WWW_HOST+'/static/images/feed-invite.png',
                'actions':{'name':'See Your Invite', 'link':self.playdate_url }
                } 

        post_to_other_facebook(access_token,actee_fb_id, message_type, ctx, **args)


    def notify_organizer(self, notify, message_type):

        if not notify:
            return True
        
        ctx = {
            'contact': self.facebook_contact,
            'actee': self.playdate.organizer.get_profile(),
            'actee_child': self.organizer_child,
            'response':self.response,
            'playdate':self.playdate,
            'playdate_url':self.playdate_url,
            'active_invite':self,
        }

        create_message_anon(self.playdate.organizer, message_type, ctx)

        email_pref = get_message_preference(self.playdate.organizer, 'playdate_host_related')

        if email_pref:
            send_email(self.playdate.organizer.email, message_type, ctx)
