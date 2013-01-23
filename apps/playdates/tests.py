from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)



from profiles.models import Child, Adult_Child, Profile, FacebookUser
from friends.models import Friendship, FriendshipInvitation
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from django.db import connection

from models import *


def create_user(username, email, password):
    user = User()
    user.username = username
    user.email = email.strip().lower()
    user.set_password(password)
    user.save()

    return user

def create_primary_email(user, email):
    ea = EmailAddress()
    ea.user=user
    ea.email=email
    ea.verified=True
    ea.primary=True
    ea.save()

def create_profile(user, fname, lname, zip):

    profile = Profile()        
    profile.user = user
    profile.first_name = fname
    profile.last_name = lname
    profile.zip_code = zip

    profile.save()
    
    return profile 


def create_child(fname, lname, gender, birthdate):
    child = Child(first_name=fname, last_name=lname, gender=gender, birthdate = birthdate)

    child.save()
    return child

def create_fbuser(user, fbid, access_token):
    fbuser = FacebookUser()        
    fbuser.user = user
    fbuser.facebook_id = fbid
    fbuser.last_name = lname
    fbuser.access_token = access_token

    fbuser.save()
    return fbuser

def create_adult_child(adult, child, relation):
    adult_child = Adult_Child( adult = adult, child = child, relation = relation, can_view_schedule = True)
    adult_child.save()
    return adult_child


from playdates import models as playdates
from notify import models as notify

# terminology
# actor - the person who is doing the action - joined, invited, rsvped, cancelled, commented, added to playlist, liked, tagged, posted, added, modified,
# actee - the person who is being done the action on - the recipient of the playdate invite, the recipient of the playlist request, the child being tagged, .
# object - photo, link, playdate, 

#notify.create_message_content('message', 'playdate_request_received', '{{ actor.first_name }}\'s child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="#">here</a> for details')
#notify.create_message_content('message', 'playdate_request_received', '{{ actor_child.first_name }} {{ actor_child.last_name}}  has invited your child to a playdate.', 'subject')
#notify.create_message_content('email', 'playdate_request_received', '{{ actor.first_name }}\'s child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="#">here</a> for details')
#notify.create_message_content('email', 'playdate_request_received', '{{ actor_child.first_name }} {{ actor_child.last_name}}  has invited your child to a playdate.', 'subject')



#notify.create_message_content('message', 'playdate_request_received', '{{ actor.first_name }}\'s child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="#">here</a> for details')
#notify.create_message_content('message', 'playdate_request_received', '{{ actor_child.first_name }} {{ actor_child.last_name}}  has invited your child to a playdate.', 'subject')
#notify.create_message_content('email', 'playdate_request_received', '{{ actor.first_name }}\'s child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="#">here</a> for details')
#notify.create_message_content('email', 'playdate_request_received', '{{ actor_child.first_name }} {{ actor_child.last_name}}  has invited your child to a playdate.', 'subject')


notify.create_message_content('message', 'playdate_request_received', '{{ actor.first_name }}\'s child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="{% url view_playdate playdate.id %}">here</a> for details')
notify.create_message_content('message', 'playdate_request_received', '{{ actor_child.first_name }} {{ actor_child.last_name}}  has invited your child to a playdate.', 'subject')
notify.create_message_content('email', 'playdate_request_received', '{{ actor.first_name }}\'s child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="{% if email %}{% url view_playdate_with_token invite_id token %}{% else %}{% url view_playdate playdate.id %}{% endif %}">here</a> for details')
notify.create_message_content('email', 'playdate_request_received', '{{ actor_child.first_name }} {{ actor_child.last_name}}  has invited your child to a playdate.', 'subject')


notify.create_message_content('message', 'playdate_attendance_confirmed', '{% if email %}{{email}}{% else %}{{ actor.first_name }}\'s child {{ actor_child.first_name }}{% endif %} has accepted your invitation to {{ actee_child.first_name }}\'s playdate. ')
notify.create_message_content('message', 'playdate_attendance_confirmed', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }} {{ actor_child.last_name}}{%endif%}  has accepted your playdate invite', 'subject')
notify.create_message_content('email', 'playdate_attendance_confirmed', '{% if email %}{{email}}{% else %}{{ actor.first_name }}\'s child {{ actor_child.first_name }}{%endif%} has accepted your invitation to {{ actee_child.first_name }}\'s playdate. ')
notify.create_message_content('email', 'playdate_attendance_confirmed', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }} {{ actor_child.last_name}}{%endif%}  has accepted your playdate invite', 'subject')

notify.create_message_content('message', 'playdate_attendance_declined', '{% if email %}{{email}}{% else %}{{ actor.first_name }}\'s child {{ actor_child.first_name }}{%endif%} has declined to attend {{ actee_child.first_name }}\'s playdate.')
notify.create_message_content('message', 'playdate_attendance_declined', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }} {{ actor_child.last_name}}{%endif%}  has declined your playdate invite', 'subject')
notify.create_message_content('email', 'playdate_attendance_declined', '{% if email %}{{email}}{% else %}{{ actor.first_name }}\'s child {{ actor_child.first_name }}{%endif%} has declined to attend {{ actee_child.first_name }}\'s playdate.')
notify.create_message_content('email', 'playdate_attendance_declined', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }} {{ actor_child.last_name}}{%endif%} has declined your playdate invite.', 'subject')
 



def create_playdate_invite_designs(app, created_models, verbosity, **kwargs):
    playdates.create_playdate_invite_design(title="Basic", small_image="http://www.cnn.com", big_image="http://www.cnn.com",description="Basic Vanilla Invite",html="Yo. Is your kid coming or not? He better. It will rock." )

def create_playdate(organizer, organizer_child, phone, address, when_from, when_until):
    pd = Playdate(organizer=organizer, organizer_child=organizer_child, phone=phone, address=address, when_from=when_from, when_until=when_until ).save()
    



#pdid=P



#    organizer = models.ForeignKey(User)
#    organizer_child = models.ForeignKey(Child)
#    is_dropoff = models.BooleanField(_("Is this a dropoff"), default=False)        
#    about = models.TextField(_("Activity"), null=True, blank=True)
#    phone = models.CharField(_("phone"), max_length=15,null=False, blank=True)
#    message = models.TextField(_("Organizer Message"), null=True, blank=True)
#    max_participants = models.PositiveIntegerField(_("Maximum Number of Participants"), null=True, blank=True)
#    expire_option = models.CharField(_("Expiration Option"), max_length=5, choices=EXPIRE_OPTIONS, null=True, blank=True)
#    invite_design = models.ForeignKey(PlaydateInviteDesign)
#    address = models.TextField(_("Address"), null=False)
#    when_from =  models.DateTimeField(_("From When"), null=False) 
#    when_until = models.DateTimeField(_("Util When"), null=False)
#    class Meta:
#        app_label='playdates'
#        unique_together = ("organizer_child","when_from","when_until")
#
#
 
from notify import models as notify

import datetime
import random


families = []
family = {}

# family unit 1
seed = random.randint(1,10000)
user = create_user('bunnyjack'+str(seed),'bisonrooka'+str(seed)+'@hotmail.com','adam79')
user2 = create_user('bettyjack'+str(seed),'bettyrooka'+str(seed)+'@hotmail.com','adam79')

family["father"]=user
family["mother"]=user2

qrofile = create_profile(user, 'Bison'+str(seed),'Rook', '08816')
profile = create_profile(user2, 'Bisette'+str(seed),'Rook', '08816')

i=1
while i < 4:
    bd = datetime.date.today() - datetime.timedelta(i*365)
    child = create_child('Bunny'+str(i),'Jackson','male', bd)
#    print "Child -- " + str(child)
    adult_child = create_adult_child(user, child, 'P')
    adult_child = create_adult_child(user2, child, 'P')
    family["child"+str(i)]=child
    i=i+1


families.append(family)
family = {}

# family unit 2
seed = random.randint(1,10000)
user = create_user('bunnyjack'+str(seed),'boris.raskin+user1'+str(seed)+'@gmail.com','adam79')
user2 = create_user('bettyjack'+str(seed),'boris.raskin+user2'+str(seed)+'@gmail.com','adam79')
create_primary_email(user, 'boris.raskin+user1'+str(seed)+'@gmail.com')
create_primary_email(user2, 'boris.raskin+user2'+str(seed)+'@gmail.com')

family["father"]=user
family["mother"]=user2

profile = create_profile(user, 'Bison'+str(seed),'Rook', '08816')
profile = create_profile(user2, 'Bisette'+str(seed),'Rook', '08816')

i=1
while i < 4:
    bd = datetime.date.today() - datetime.timedelta(i*365)
    child = create_child('Busty'+str(i),'Jackson','male', bd)
    family["child"+str(i)]=child
    adult_child = create_adult_child(user, child, 'P')
    adult_child = create_adult_child(user2, child, 'P')
    i=i+1

families.append(family)


from playdates import models as playdates

playdates.create_playdate_invite_design(title="Basic", small_image="http://www.cnn.com", big_image="http://www.cnn.com",description="Basic Vanilla Invite",html="Yo. Is your kid coming or not? He better. It will rock." )

pd = playdates.Playdate()


when_from = datetime.datetime.now() + datetime.timedelta(days=1, hours=2)
when_until = datetime.datetime.now() + datetime.timedelta(days=1, hours=3)


pd.organizer=families[0]["father"]
pd.organizer_child=families[0]["child1"]
pd.phone='732-432-7794'
pd.message='come play with me'
pd.address='5 Sterling Court, East Brunswick, NJ 08816'
pd.when_from=when_from
pd.when_until=when_until
pd.save()


pdi = playdates.PlaydateInviteUser()

pdi.playdate=pd
pdi.to_user=families[1]["father"]
pdi.to_child=families[1]["child1"]

pdi.save_and_invite()

pdi.accept_and_notify()


pde = playdates.PlaydateInviteEmail()

pde.playdate=pd
pde.email='johnybr@yahoo.com'
pde.token=pde.assign_token()

print "token -- " + pde.token

pde.save_and_invite()
pde.accept_and_notify()

print families

print families[0]["father"].email
print families[1]["father"].email

for x in pd.invitees:
    print str(x)

