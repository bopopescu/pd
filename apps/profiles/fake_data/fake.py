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
from photos.models import *

import os, random
from datetime import datetime
from datetime import timedelta

from notify.models import create_message, create_update, send_email, create_user_update, create_user_update_for_child_playlist_adults, create_status_update
from schedule.models import *
import random
from random import randint
from mydebug import *


fb_users = [
    { 'fbid':'100002342320337', 'at':'121631667910635|24d97c01eaf87a860a09b6e9.0-100002342320337|1belbBJfEBcfDNL-BIXQeaNaOL4' },
    { 'fbid':'100002332540404', 'at':'121631667910635|74bf576596178b604302719f.0-100002332540404|CWXHuOXpbga91c1ib09FLLnfaIM' },
    { 'fbid':'100002323270497', 'at':'121631667910635|52ceae496c66e82dc0c0999b.0-100002323270497|2hTcQopVUrZSL0KMJHO7k7J9pH0' },
    { 'fbid':'100002366590459', 'at':'121631667910635|b8f1ee56dd90985148d12a36.0-100002366590459|xU3FFlK_oBTtJtFgVSsZNsOXnko' },
    { 'fbid':'100002363860322', 'at':'121631667910635|7e622945196338817a62c3d0.0-100002363860322|qrdovlee5PwYgYNc-Qo1FgM-DAM' },
    { 'fbid':'100002334460326', 'at':'121631667910635|e3744965507c8b34ff50b1ec.0-100002334460326|tY0SEb2r3C_wviRNl12N8cznE0U' },
]



def create_ca(description):
    ca = CustomActivity(description=description)
    ca.save()
    return ca


fnames = { 
    'male': ['JAMES', 'JOHN', 'ROBERT', 'MICHAEL', 'WILLIAM', 'DAVID', 'RICHARD', 'CHARLES', 'JOSEPH', 'THOMAS', 'CHRISTOPHER', 'DANIEL', 'PAUL', 'MARK', 'DONALD', 'GEORGE', 'KENNETH', 'STEVEN', 'EDWARD', 'BRIAN', 'RONALD', 'ANTHONY', 'KEVIN', 'JASON', 'MATTHEW', 'GARY', 'TIMOTHY', 'JOSE', 'LARRY', 'JEFFREY', 'FRANK', 'SCOTT', 'ERIC', 'STEPHEN', 'ANDREW', 'RAYMOND', 'GREGORY', 'JOSHUA', 'JERRY', 'DENNIS', 'WALTER', 'PATRICK', 'PETER', 'HAROLD', 'DOUGLAS', 'HENRY', 'CARL', 'ARTHUR', 'RYAN', 'ROGER', 'JOE', 'JUAN', 'JACK', 'ALBERT', 'JONATHAN', 'JUSTIN', 'TERRY', 'GERALD', 'KEITH', 'SAMUEL', 'WILLIE', 'RALPH', 'LAWRENCE', 'NICHOLAS', 'ROY', 'BENJAMIN', 'BRUCE', 'BRANDON', 'ADAM', 'HARRY', 'FRED', 'WAYNE', 'BILLY', 'STEVE', 'LOUIS', 'JEREMY', 'AARON', 'RANDY', 'HOWARD', 'EUGENE', 'CARLOS', 'RUSSELL', 'BOBBY', 'VICTOR', 'MARTIN', 'ERNEST', 'PHILLIP', 'TODD', 'JESSE', 'CRAIG', 'ALAN', 'SHAWN', 'CLARENCE', 'SEAN', 'PHILIP', 'CHRIS', 'JOHNNY', 'EARL', 'JIMMY', 'ANTONIO', 'DANNY', 'BRYAN', 'TONY', 'LUIS', 'MIKE', 'STANLEY', 'LEONARD', 'NATHAN', 'DALE', 'MANUEL', 'RODNEY', 'CURTIS', 'NORMAN', 'ALLEN', 'MARVIN'],
    'female': ['MARY', 'PATRICIA', 'LINDA', 'BARBARA', 'ELIZABETH', 'JENNIFER', 'MARIA', 'SUSAN', 'MARGARET', 'DOROTHY', 'LISA', 'NANCY', 'KAREN', 'BETTY', 'HELEN', 'SANDRA', 'DONNA', 'CAROL', 'RUTH', 'SHARON', 'MICHELLE', 'LAURA', 'SARAH', 'KIMBERLY', 'DEBORAH', 'JESSICA', 'SHIRLEY', 'CYNTHIA', 'ANGELA', 'MELISSA', 'BRENDA', 'AMY', 'ANNA', 'REBECCA', 'VIRGINIA', 'KATHLEEN', 'PAMELA', 'MARTHA', 'DEBRA', 'AMANDA', 'STEPHANIE', 'CAROLYN', 'CHRISTINE', 'MARIE', 'JANET', 'CATHERINE', 'FRANCES', 'ANN', 'JOYCE', 'DIANE', 'ALICE', 'JULIE', 'HEATHER', 'TERESA', 'DORIS', 'GLORIA', 'EVELYN', 'JEAN', 'CHERYL', 'MILDRED', 'KATHERINE', 'JOAN', 'ASHLEY', 'JUDITH', 'ROSE', 'JANICE', 'KELLY', 'NICOLE', 'JUDY', 'CHRISTINA', 'KATHY', 'THERESA', 'BEVERLY', 'DENISE', 'TAMMY', 'IRENE', 'JANE', 'LORI', 'RACHEL', 'MARILYN', 'ANDREA', 'KATHRYN', 'LOUISE', 'SARA', 'ANNE', 'JACQUELINE', 'WANDA', 'BONNIE', 'JULIA', 'RUBY', 'LOIS', 'TINA', 'PHYLLIS', 'NORMA', 'PAULA', 'DIANA'] 
}

lnames = ['SMITH', 'JOHNSON', 'WILLIAMS', 'JONES', 'BROWN', 'DAVIS', 'MILLER', 'WILSON', 'MOORE', 'TAYLOR', 'ANDERSON', 'THOMAS', 'JACKSON', 'WHITE', 'HARRIS', 'MARTIN', 'THOMPSON', 'GARCIA', 'MARTINEZ', 'ROBINSON', 'CLARK', 'RODRIGUEZ', 'LEWIS', 'LEE', 'WALKER', 'HALL', 'ALLEN', 'YOUNG', 'HERNANDEZ', 'KING', 'WRIGHT', 'LOPEZ', 'HILL', 'SCOTT', 'GREEN', 'ADAMS', 'BAKER', 'GONZALEZ', 'NELSON', 'CARTER', 'MITCHELL', 'PEREZ', 'ROBERTS', 'TURNER', 'PHILLIPS', 'CAMPBELL', 'PARKER', 'EVANS', 'EDWARDS', 'COLLINS', 'STEWART', 'SANCHEZ', 'MORRIS', 'ROGERS', 'REED', 'COOK', 'MORGAN', 'BELL', 'MURPHY', 'BAILEY', 'RIVERA', 'COOPER', 'RICHARDSON', 'COX', 'HOWARD', 'WARD', 'TORRES', 'JAMES', 'AHMED', 'COHEN', 'LEVY', 'GOLDBERG', 'JOBS','GATES','PUMA']


def get_random_gender():
    return random.choice(["male","female"])

def get_random_bd(year_range = None):
    if year_range is None:
        year_range=range(3,11)
    year = random.choice(year_range)
    month = random.choice(range(1,12))

    bd = datetime.now() - timedelta(days=(year*365 - month*30))
    return bd

def get_random_fname(gender):
    fname = fnames[gender][random.choice(range(0,len(fnames[gender])))]
    return fname.title()

def get_random_lname():
    lname = lnames[random.choice(range(0,len(lnames)))]
    return lname.title()


from places.models import Zip
def get_random_zip():
    zip_idx = random.choice(range(18880,18944))
    zipc = Zip.objects.get(id=zip_idx)
    zc = zipc.zip
    
    return zipc


base_dir ='/var/www/playdation.net/playdation/apps/profiles/fake_data/'
def kid_photo(gender):
    pdir = base_dir + 'kid_photos/'+gender+'/'
    return get_random_photo(pdir)

def adult_photo(gender):
    pdir = base_dir + 'adult_photos/'+gender+'/'
    return get_random_photo(pdir)

def get_random_photo(pdir):
    a = random.choice(os.listdir(pdir))
    loc = pdir+a
    return loc


def create_user(email = None):

    if email is None:
        email = 'demos+' + str( random.choice(range(1,1000000)) ) + '@playdation.com'

    password = 'play';
    user = User()

    user.username = 'susername' + str( random.choice(range(1,1000000)) )

    user.email = email.strip().lower()

    user.set_password(password)

    user.save()

    return user

def create_profile(user, gender=None, lname=None):

    if gender is None:
        gender = get_random_gender()


    fname = get_random_fname(gender)

    if lname is None:
        lname = get_random_lname()

    zc = get_random_zip()
    photo = adult_photo(gender)

    profile = Profile()        
    profile.user = user
    profile.first_name = fname
    profile.last_name = lname
    profile.zip_code = zc
    profile.gender = gender

    profile.save()

    f = open(photo, 'r')
    np = Photo(album=profile.album, caption="Profile", original_image=File(f))
    np.save()

    profile.set_profile_pic(np)

    return profile 

from django.core.files import File  # you need this somewhere


def get_age(bd):    
    from datetime import date
    today = date.today()
    try:
        birthday = date(today.year, bd.month, bd.day)
    except:
        birthday = date(today.year, bd.month, bd.day-1)

    if birthday > today:
        return today.year - bd.year - 1
    else:
        return today.year - bd.year

def calc_grade_level(age):
    gl = age - 5
    if gl < 1:
        return None
    else:
        return gl






schools = [
           "Beacon School",
           "The Twon School",
           "PS 150",
           "The Chapin School",
           "Immaculate Conception School",
           "Hewitt School",
           ]


from schools.models import *

school_range_start=3613490
def get_school():
    gsid = school_range_start + random.choice(range(0,30))
    sch = School.objects.get(gsid=gsid)

#    schn = schools[random.choice(range(0,len(schools) ) ) ]
#    sch,created = School.objects.get_or_create(name=schn, type="E")
    return sch


def create_child(lname=None, year_range=None):
    gender = get_random_gender()
    fname = get_random_fname(gender)
    if year_range is not None:
        birthdate = get_random_bd(year_range = year_range)
    else:
        birthdate = get_random_bd()
    photo = kid_photo(gender)
    age = get_age(birthdate)
    grade_level = calc_grade_level(age)
    school = get_school()

    child = Child(first_name=fname, last_name=lname, gender=gender, birthdate = birthdate, grade_level = grade_level, school=school)
    child.save()
    
    f = open(photo, 'r')
    np = Photo(album=child.album, caption="Profile", original_image=File(f))
    np.save()
    child.set_profile_pic(np)

    return child


def create_fbuser(user, fb):

    fbid = fb["fbid"]
    at = fb["at"]

    try:
        fbuser = FacebookUser.objects.get(facebook_id=fbid, access_token=at)
        fbuser.user = user
        fbuser.save()
    except FacebookUser.DoesNotExist:
        fbuser = FacebookUser()
        fbuser.user = user
        fbuser.facebook_id = fbid
        fbuser.access_token = at
        fbuser.save()

    return fbuser

def create_adult_child(adult, child, relation):
    adult_child = Adult_Child( adult = adult, child = child, relation = relation, can_view_schedule = True)
    adult_child.set_admin_perms()
    adult_child.save()
    return adult_child


def create_friend(fromc, toc):
    from_user = fromc.parents[0]
    to_user = toc.parents[0]
    friendship_inv = FriendshipInvitation(from_child = fromc, from_user=from_user, to_child = toc, to_user=to_user)
    friendship_inv.save()
    friendship_inv.accept()


def connect_ac_kids(user, kids):
    for kid in kids:
        create_adult_child(user,kid,'P')


def tossh():
    if random.choice(range(0,10)) < 5:
        return True
    else:
        return False

def tosst():
    if random.choice(range(0,9)) < 3:
        return True
    else:
        return False

def tossq():
    if random.choice(range(0,12)) < 3:
        return True
    else:
        return False

status_updates = [
                  "Off to see Rango at Loews Lincoln Square",
                  "Going to the park",
                  "Checking out that awesome new place",
                  "Helping with homework",
                  "Zoo time! Off to the Central Park Zoo. Kids are excited about the zebras!",
                  "Just finished reading a bed time story. Nighty night.",
                  "Gymboree, here we come!",
                  "Taking the kids to a birthday party at Chuck E. Cheese.",
                  "Going to the 72nd street playground",
                  ]


times = [
         "Now",
         "Now",
         "Now",
         "In two hours",
         "In three hours",
         "This evening",
         "In an hour",
         "In five minutes",         
         ]






def create_status_feed(us, parents = None):
    for i in range(0,10):
        if parents is not None:
            user = parents[random.choice(range(0, len(parents)))]
        else:
            user = us

        ac_list = user.get_profile().manage_playlist_children
        children = []
        for ac in ac_list:
            children.append(ac.child)

        ac_child = children[random.choice(range(0, len(children) ) ) ]
        ctx = { 
               'actor':user.get_profile(),
               'actor_children':ac_child.first_name,
               'status':status_updates[random.choice(range(0, len(status_updates) ) ) ],
               'when':times[random.choice(range(0, len(times)))], 
               }
        
        up = create_status_update(us, 'status_update', ctx)
        create_user_update(us, up)
        exclude_users = []
        exclude_users = exclude_users + create_user_update_for_child_playlist_adults(ac_child, up, exclude = exclude_users)





nk = [1,1,1,2,2,2,2,2,2,3,3,3]
def create_family(lname=None, email=None, num_kids=None, year_range = None, fb = None):

    if lname is None:
        lname = get_random_lname()

    # create kids
    num_kids_index = random.choice(range(1,10))
    if num_kids is None:
        num_kids = nk[num_kids_index]

    kids = []
    for i in range(0,num_kids):
        c = create_child(lname=lname, year_range=year_range)
        kids.append(c)

    # mother
    if lname is None:
        lname = get_random_lname()

    gender = 'female'
    user = create_user(email=email)

    if fb is not None:
        create_fbuser(user, fb)

    profile = create_profile(user, lname=lname, gender=gender)

    connect_ac_kids(user, kids)

    # father
    if random.choice(range(1,15)) > 9:
        is_father = True
    else:
        is_father = False

    if is_father:
        user = create_user()
        profile = create_profile(user, lname=lname, gender='male')
        connect_ac_kids(user, kids)

    return kids

def create_events_for_month(child):
    i=0
    now = datetime.now()
    while i < 30:
        now = now + timedelta(days=1)
        if now.isoweekday() < 6:
            activity = create_ca("School")
            start = now.replace(hour=8,minute=30,second=0)
            end = now.replace(hour=15, minute=30, second=0)
            event = create_event(start, end, activity )
            evp = create_eventplan(child, event, "1")
    
            if tossh():
                if tossh():
                    activity = create_ca("Available")
                    sh = end.hour
                    sh = sh + randint(1,3)
                    start = end.replace(hour=sh,minute=0,second=0)
                    end = start + timedelta(hours=1)
                    event = create_event(start, end, activity )
                    evp = create_eventplan(child, event, "2")
                else:
                    activity = create_ca("Playdate Invite")
                    sh = end.hour
                    sh = sh + randint(1,3)
                    start = end.replace(hour=sh,minute=0,second=0)
                    end = start + timedelta(hours=1)
                    event = create_event(start, end, activity )
                    evp = create_eventplan(child, event, "4")
                    
    
            if tossq():
                activity = create_ca("Birthday Party!")
                sh = end.hour
                sh = sh + randint(1,4)
                start = end.replace(hour=sh,minute=0,second=0)
                end = start + timedelta(hours=2)
                event = create_event(start, end, activity )
                evp = create_eventplan(child, event, "3")
                
        else:
            if tossh():
                activity = create_ca("Soccer Practice")
                start = now.replace(hour=9,minute=30,second=0)
                end = now.replace(hour=14, minute=30, second=0)
                event = create_event(start, end, activity )
                evp = create_eventplan(child, event, "1")
    
                activity = create_ca("Violin Practice")
                start = now.replace(hour=16,minute=30,second=0)
                end = now.replace(hour=18, minute=30, second=0)
                event = create_event(start, end, activity )
                evp = create_eventplan(child, event, "1")
                    
            else:
                activity = create_ca("Available")
                start = now.replace(hour=9,minute=30,second=0)
                end = now.replace(hour=17, minute=30, second=0)
                event = create_event(start, end, activity )
                evp = create_eventplan(child, event, "2")
    
    
        i = i+1




email='example@demo.com'


try:
    us = User.objects.filter(email=email)
    for foo in us.all():
        foo.email='old_'+str( random.choice(range(1,1000000)) )+'@something.net'
        foo.save()
except:
    raise


fb_info = fb_users.pop(0)
observer_kids = create_family(lname='Botwin',email=email, num_kids = 2, year_range=range(4,11), fb=fb_info)

for child in observer_kids:
    create_events_for_month(child)

us = User.objects.get(email=email)

# create_fbuser(us, fbid, access_token)

families = []

for i in range(0,20):
    fb_info = None

    kd = create_family(fb = fb_info)
    families.append(kd)


parents = []    
friends_cohort = []
for kd in families:
    for k in kd:
        for ok in observer_kids:
            if k.age <= ok.age + 1  and k.age >= ok.age - 1:
                create_friend(ok, k)
                print "creating friends"
                if not k in friends_cohort:
                    friends_cohort.append(k)
                    print "adding to cohort"
                    for p in k.parents:
                        print "running for parent"
                        if not p in parents:
                            print "adding to parents"
                            parents.append(p)


unrelated_families = []

for i in range(0,50):
    fb_info = None
    if len(fb_users):
        fb_info = fb_users.pop(0)

    kd = create_family(fb = fb_info)
    unrelated_families.append(kd)


for kd in unrelated_families:
    for k in kd:
        for ok in observer_kids:
            if k.age <= ok.age + 1  and k.age >= ok.age - 1:
                if not k in friends_cohort:
                    friends_cohort.append(k)




for k in friends_cohort:
    i = 0
    while i < 5:
        i = i + 1
        rand_k = friends_cohort[random.choice(range(0, len(friends_cohort)))]
        if k == rand_k:
            continue
        try:
            print "creating friend for cohort"
            create_friend(k, rand_k)
        except:
            pass

create_status_feed(us, parents=parents) #, observer_kids)
