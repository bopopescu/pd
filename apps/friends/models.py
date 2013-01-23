
from django.utils.translation import ugettext as _

from random import random

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from profiles.models import Profile, Child, Adult_Child, Friendship, FacebookUser
from notify.models import create_message, create_update, send_email, get_message_preference

from cachebot.managers import CacheBotManager
from datetime import datetime, timedelta, date
from django.db.models import Q
from itertools import *

from mydebug import *

from mailer import send_mail, send_html_mail

if "emailconfirmation" in settings.INSTALLED_APPS:
    from emailconfirmation.models import EmailAddress
else:
    EmailAddress = None

class GoogleToken(models.Model):
    user = models.ForeignKey(User, related_name='googletokens')
    token = models.TextField()
    token_secret = models.CharField(max_length=100)
   
    def get_token(self):
        import pickle
        return pickle.loads(str(self.token))

IMPORTED_TYPES = (
    ("V", "VCard Import"),
    ("G", "Google Import"),
    ("O", "Outlook Import"),
)

# A contact is a someone known by a user who may or may not themselves be a user.
class Contact(models.Model):
    # the user who created the contact; switched to owner so I can use 'user' for the actual user this corresponds to
    owner = models.ForeignKey(User, related_name="%(class)s", editable=False, db_index=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, editable=False, related_name='%(class)s_user', db_index=True)
    added = models.DateField(default=date.today, editable=False)
    invited = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    create_date = models.DateTimeField(blank=True, null=True)


    class Meta:
        app_label='friends'
        abstract = True
    

class ContactEmail(Contact):
    first_name = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    last_name = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    import_job = models.IntegerField(null=True, blank=True, db_index=True)
    email = models.EmailField(db_index=True)
    objects = CacheBotManager()

    class Meta:
        unique_together = (('owner','email'))

    def save(self, *args, **kwargs):
        if not self.name and (self.first_name or self.last_name):
            self.name = ("%s %s" % (self.first_name, self.last_name)).strip()
        super(Contact,self).save(*args, **kwargs)
        return self

    def send_invite(self):
        self.invited = True
        self.create_date = datetime.now()

        JoinInvitationEmail.objects.send_invitation(self.owner, self, self.email, message=None)        

        self.save()

    def key(self):
        return 'ce_' + str(self.id)
    key = property(key)

        

def contact_email_update_user(sender, instance, created, *args, **kwargs):
    if created:
        for ce in ContactEmail.objects.filter(email=instance.email).all():
            ce.user=instance
            ce.save()




class ContactFB(Contact):
    facebook_id = models.CharField(max_length=150, db_index=True)
    first_name = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    last_name = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    objects = CacheBotManager()

    class Meta:
        unique_together = (('owner','facebook_id'))

#    def save(self, *args, **kwargs):
#        if not self.name and (self.first_name or self.last_name):
#            self.name = ("%s %s" % (self.first_name, self.last_name)).strip()
#        super(Contact,self).save(*args, **kwargs)
#        return self
    

    def send_invite(self):
        self.invited = True
        self.create_date = datetime.now()

        self.save()

    def key(self):
        return 'fb_' + str(self.id)
    key = property(key)



def contact_fb_update_user(sender, instance, created, *args, **kwargs):
    if created:
        for ce in ContactFB.objects.filter(facebook_id=instance.facebook_id).all():
            ce.user=instance.user
            ce.save()



INVITE_STATUS = (
    ("1", "Created"),
    ("2", "Sent"),
    ("3", "Failed"),
    ("4", "Expired"),
    ("5", "Accepted"),
    ("6", "Declined"),
    ("7", "Joined Independently"),
    ("8", "Deleted")
)


class JoinInvitationEmailManager(models.Manager):
    
    def send_invitation(self, from_user, contact, to_email, message=None):
        salt = sha_constructor(str(random())).hexdigest()[:5]
        confirmation_key = sha_constructor(salt + to_email).hexdigest()

        accept_url = u"http://%s%s" % (
            settings.WWW_HOST,
            reverse("acct_signup_key", args=(confirmation_key,)),
        )
        
        ctx = {
            "SITE_NAME": unicode(Site.objects.get_current()),
            "CONTACT_EMAIL": settings.DEFAULT_FROM_EMAIL,
            "contact": contact,
            "email": to_email,
            "user": from_user,
            "actor": from_user.get_profile(),
            "message": message,
            "accept_url": accept_url,
        }
        
#        subject = render_to_string("friends/join_invite_subject.txt", ctx)
#        subject = subject.rstrip()
#        email_message = render_to_string("friends/join_invite_message.txt", ctx)

        send_email(to_email, 'join_invitation', ctx = ctx, skip_footer = True)        

#        send_html_mail(subject, 'text message', email_message, settings.DEFAULT_FROM_EMAIL, [to_email])

#        send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, [to_email])        

        return self.create(from_user=from_user, contact=contact, message=message, status="2", confirmation_key=confirmation_key)


class JoinInvitationEmail(models.Model):
    from_user = models.ForeignKey(User, related_name="join_from")
    contact = models.ForeignKey(ContactEmail)
    message = models.CharField(max_length=2000, null=True, blank=True)
    sent = models.DateField(default=date.today)
    status = models.CharField(max_length=1, choices=INVITE_STATUS)
    confirmation_key = models.CharField(max_length=40)
    create_date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    
    objects = JoinInvitationEmailManager()
    
    def accept(self, new_user, notify_friends=False):
        # mark invitation accepted
        self.status = "5"
        self.save()
    
    class Meta:
        ordering=['-sent']


class FriendshipInvitationManager(CacheBotManager):
    
    def invitations(self, *args, **kwargs):
        return self.filter(*args, **kwargs).exclude(status__in=["6", "8"])


def friend_set_for(user):
    return set([obj["friend"] for obj in Friendship.objects.friends_for_user(user)])



INVITE_STATUS = (
    ("1", "Created"),
    ("2", "Sent"),
    ("3", "Failed"),
    ("4", "Expired"),
    ("5", "Accepted"),
    ("6", "Declined"),
    ("7", "Joined Independently"),
    ("8", "Deleted")
)


HOW_RELATED = (
    ("1", "We attend the same School"),
    ("2", "We live in the same Neighborhood"),
    ("3", "We have common friends"),
    ("4", "We are friends in real life"),
    ("5", "Other")
)

HOW_RELATED_HASH = {
    "1": "We attend the same school",
    "2": "We live in the same neighborhood",
    "3": "We are friends or have friends in common",
    "4": "We are friends in real life",
    "5": "Other"
}

class FriendshipInvitation(models.Model):
    from_user = models.ForeignKey(User, related_name="invitations_from_user", db_index=True)
    to_user = models.ForeignKey(User, related_name="invitations_to_user", db_index=True)
    from_child = models.ForeignKey(Child, related_name="invitations_from_child", db_index=True)
    to_child = models.ForeignKey(Child, related_name="invitations_to_child", db_index=True)

    how_related = models.CharField(max_length=1, choices=HOW_RELATED, default='5')
    message = models.CharField(max_length=2000, null=True, blank=True)
    sent = models.DateField(default=date.today)
    status = models.CharField(max_length=1, choices=INVITE_STATUS)
    
    objects = FriendshipInvitationManager()
    
    def accept(self, notify_friends=False):
        if not Friendship.objects.are_friends(self.to_child, self.from_child):
            friendship = Friendship(to_child=self.to_child, from_child=self.from_child, from_user=self.from_user, to_user=self.to_user)
            friendship.save()
            self.status = "5"
            self.save()

    def how_related_verbose(self):
        if self.how_related is not None:
            return HOW_RELATED_HASH[self.how_related]
        return ''
    how_related_verbose = property(how_related_verbose)
    
    def save_and_notify(self, notify=True):
        self.save()
        # notify user that they have a friend request

        if not notify:
            return True

        ctx = {
            'actor': self.from_user.get_profile(),
            'actee': self.to_user.get_profile(),
            'actor_child':self.from_child,
            'actee_child':self.to_child,
            'message':self.message
        }

        create_message(self.from_user, self.to_user, 'playlist_request_received', ctx, category='Friend Request', associated_item=self.id )

        email_pref = get_message_preference(self.to_user, 'friend_related')

        if email_pref:
            send_email(self.to_user.email, 'playlist_request_received', ctx)

        

    def accept_and_notify(self, notify=True):
        self.accept()
        # notify user that friend request accepted
        # notify friends that connection has been made

        if not notify:
            return True

        ctx = {
            'actor': self.to_user.get_profile(),
            'actee': self.from_user.get_profile(),
            'actor_child':self.to_child,
            'actee_child':self.from_child
        }

        create_message(self.to_user, self.from_user, 'playlist_request_confirmed', ctx, category='Message', respond=False )

        email_pref = get_message_preference(self.from_user, 'friend_related')

        if email_pref:
            send_email(self.from_user.email, 'playlist_request_confirmed', ctx)

    
    def decline(self):
        if not Friendship.objects.are_friends(self.to_child, self.from_child):
            self.status = "6"
            self.save()

    class Meta:
        unique_together = (('from_child','to_child'))


# always a user.
# Child A is a friendsuggestion for Child B if:
# 1) Parent A has imported Parent B's email address but hasn't friended a child yet
# 2) Child A age +- 1 year = Child B age
# 3) Parent A has imported Parent B's as a friend but hasn't friended a child yet  

# 4)friendsuggestion is destroyed (hidden) when a friendshipinvitation is sent, when the user destroys it in the UI
# 5)friendsuggestion is created when a contact becomes a user and has kids of the right ages


SUGGEST_BECAUSE_EMAIL=0
SUGGEST_BECAUSE_FB=1
SUGGEST_BECAUSE_SCHOOL=2


SUGGEST_WHY_CHOICES = (
    (SUGGEST_BECAUSE_EMAIL, "They are an email contact"),
    (SUGGEST_BECAUSE_FB,"They are a facebook friend."),
    (SUGGEST_BECAUSE_SCHOOL,"Their child goes to the same school."),
)


class FriendSuggestion(models.Model):
    child = models.ForeignKey(Child, related_name="suggested_friends", db_index=True)
    suggested_child = models.ForeignKey(Child, related_name="+")
    why = models.IntegerField(null=True, blank=True, choices=SUGGEST_WHY_CHOICES)
    active = models.BooleanField(default=True)

    objects = CacheBotManager()


def populate_friend_suggestion(child, user = None):

    users = []
    if user is None:
       for p in child.parents:
            users.append(p)
    else:
        users.append(user)

    contact_list = chain( User.objects.filter(contactemail_user__owner__in=users).all(), User.objects.filter(contactfb_user__owner__in=users).all())
    contact_ids = []
    for cid in contact_list:
        contact_ids.append(int(cid.id))

    if not len(contact_ids):
        return True

    friend_invitations = FriendshipInvitation.objects.filter(Q(from_child = child) | Q(to_child = child)).all()
    outstanding_fis = []
    for fi in friend_invitations:
        if fi.to_child == child:
            outstanding_fis.append(fi.from_child_id)
        elif fi.from_child == child:
            outstanding_fis.append(fi.to_child_id)

    child_bd_min = child.birthdate - timedelta(days=365)
    child_bd_max = child.birthdate + timedelta(days=365)

    possible_friends_qs = Child.objects.filter(birthdate__gte = child_bd_min, birthdate__lte = child_bd_max, attached_adults__adult__in=contact_ids)
    if len(outstanding_fis):
        possible_friends_qs = possible_friends_qs.exclude(id__in=outstanding_fis)

    possible_friends = list(possible_friends_qs.all())

    for p in possible_friends:
        if child == p:
            continue
        
        fs, _ = FriendSuggestion.objects.get_or_create(child=child, suggested_child=p)
        fs, _ = FriendSuggestion.objects.get_or_create(child=p, suggested_child=child)
    
    return True


def friendinvite_destroys_friendsuggest(sender, instance, created, *args, **kwargs):
    if created:
        for fs in FriendSuggestion.objects.filter(Q(child = instance.from_child_id, suggested_child = instance.to_child_id) | Q(child = instance.to_child_id, suggested_child = instance.from_child_id)).all():
            fs.active = False
            fs.save()



# SIGNALS
#signals.pre_save.connect(friendship_invitation, sender=FriendshipInvitation)
signals.post_save.connect(contact_email_update_user, sender=User)
signals.post_save.connect(contact_fb_update_user, sender=FacebookUser)
signals.post_save.connect(friendinvite_destroys_friendsuggest, sender=FriendshipInvitation)

#signals.post_save.connect(friendsuggestion_update_user, sender=User)
#signals.post_save.connect(contact_create_for_friendship, sender=Friendship)
#signals.post_save.connect(friendship_destroys_suggestions, sender=Friendship)
#signals.pre_delete.connect(delete_friendship, sender=Friendship)
#signals.post_save.connect(suggest_friend_from_invite, sender=JoinInvitation)
