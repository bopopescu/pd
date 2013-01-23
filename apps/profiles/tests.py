from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)



from profiles.models import Child, Adult_Child, Profile, FacebookUser
from friends.models import Friendship
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
    family["child"+str(i)]=child
    adult_child = create_adult_child(user, child, 'P')
    adult_child = create_adult_child(user2, child, 'P')
    i=i+1

families.append(family)

# print str(families)


# create friendships

i=1
while i < 3:
    friendship = Friendship(from_child = families[0]["child"+str(i)], to_child = families[1]["child"+str(i)])
    friendship.save()
    i=i+1


child1 = families[0]["child1"]
child2 = families[1]["child1"]

bd = datetime.date.today() - datetime.timedelta(i*365)
child3 = create_child('LoneBunny'+str(i),'Jackson','male', bd)
child3.save()

child4 = create_child('LoneBunny'+str(i),'Jackson','male', bd)
child4.save()

friendship = Friendship(from_child = child2, to_child = child3)
friendship.save()

user = families[0]["father"]

for friend in child1.friends.all():
    print " child's friends: " + str(friend.id)

for adult in child1.adults.all():
    print " child's parents: " + str(adult.id)

for child in user.children.all():
    print " user's children: " + str(child.id)




# user's child's friends
#for child in adult.children.filter(.friends.all():
#    print " user's child's friends " + str(child)

#userlist = User.objects.filter(


#select ac2.user_id
#from child_friend f, adult_child ac1, adult_child ac2
#where ac1.user_id = USER
#and ac.child_id = f.child1_id
#and f.child2_id = ac2.child_id

#user's children's friends' parents

# select ac2.child_id, ac2.adult_id from profiles_adult_child ac1, profiles_adult_child ac2, profiles_friendship f where ac1.adult_id=72 and ac1.child_id = f.from_child_id and f.to_child_id = ac2.child_id;




# child's friends parents
#for adult in child1.friends.adults.all():
#    print " child's friends parents: " + str(adult)


