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



from notify import models as notify

notify.create_message_content('facebook','user_joined', '{{ actor.first_name }} has joined Playdation!')        

notify.create_message_content('update','contact_joined','{{ actor.first_name }} has joined Playdation!')

notify.create_message_content('message','playlist_request_received', '{{ actor.first_name }} wants to add your child {{ actee_child.first_name }} to their child\'s {{ actor_child.first_name }} playlist. <p>{{ message }}</p> click <a href="#" onclick="javascript:accept_friendship({{actor_child.id}},{{actee_child.id}}); return false;">here</a> to accept')

notify.create_message_content('message','playlist_request_received', 'Someone wants to add your child to their child\'s playlist', 'subject')

notify.create_message_content('email','playlist_request_received', '{{ actor.first_name }} wants to add your child {{ actee_child.first_name }} to their child\'s {{ actor_child.first_name }} playlist')

notify.create_message_content('email','playlist_request_received', 'Someone wants to add your child to their child\'s playlist', 'subject')

notify.create_message_content('message','playlist_request_confirmed', '{{ actor.first_name }} has accepted your playlist request. {{ actor_child.first_name }} has been added to {{ actee_child.first_name }}\'s playlist')

notify.create_message_content('message','playlist_request_confirmed', '{{ actor.first_name }} has confirmed your playlist request', 'subject')

notify.create_message_content('email','playlist_request_confirmed', '{{ actor.first_name }} has accepted your playlist request. {{ actor_child.first_name }} has been added to {{ actee_child.first_name }}\'s playlist')

notify.create_message_content('email','playlist_request_confirmed', '{{ actor.first_name }} has confirmed your playlist request', 'subject')

notify.create_message_content('update','friend_new_friend','{{ actor.first_name }} {{ actor.last_name }} has added {{ actee_child.first_name }} to {{ actor_child.first_name }}\'s playlist ')




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

profile = create_profile(user, 'Bison'+str(seed),'Rook', '08816')
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
    child = create_child('Bunny'+str(i),'Jackson','male', bd)
    family["child"+str(i)]=child
    adult_child = create_adult_child(user, child, 'P')
    adult_child = create_adult_child(user2, child, 'P')
    i=i+1
print "here1"

families.append(family)

i=1

print "to_user_email " + families[1]["father"].email + " pwd: adam79"

while i < 3:
    friendshipinv = FriendshipInvitation(from_child = families[0]["child"+str(i)], to_child = families[1]["child"+str(i)], from_user= families[0]["father"], to_user=families[1]["father"], message="Dude. This site is awesome", how_related=4)
    friendshipinv.save_and_notify()
    i=i+1




print "here10"
# print str(families)


# create friendships
i=1
while i < 4:
    friendship = Friendship(from_child = families[0]["child"+str(i)], to_child = families[1]["child"+str(i)])
    friendship.save()
    i=i+1

benchild = Child.objects.get(id=105)
i=1
while i < 4:
    friendship = Friendship(from_child = families[0]["child"+str(i)], to_child = benchild)
    friendship.save()
    i=i+1

benchild = Child.objects.get(id=1)
i=1
while i < 4:
    friendship = Friendship(from_child = families[0]["child"+str(i)], to_child = benchild)
    friendship.save()
    i=i+1
