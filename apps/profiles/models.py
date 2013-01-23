from django.db import models
from django.utils.translation import ugettext_lazy as _

# from idios.models import ProfileBase
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from emailconfirmation.models import EmailAddress
import datetime, re
from mydebug import *
from schools.models import School
from photos.models import Photo, Album, AnonPhoto
from notify.models import create_update, create_user_update
from places.models import Zip
from django.db import connection
from django.contrib.contenttypes import generic

from playdates.invites import InviteDesign
from cachebot.managers import CacheBotManager


GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
)


# default_photo=Photo.objects.get(id=1)


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='_profile_cache', db_index=True)

    first_name = models.CharField(_("first_name"), max_length=50, null=True, blank=True, db_index=True)
    last_name = models.CharField(_("last_name"), max_length=50, null=True, blank=True, db_index=True)
    zip_code = models.ForeignKey(Zip, null=True, blank=True, db_index=True)
    about = models.TextField(_("about"), null=True, blank=True)
    birthdate = models.DateField(_("birthday"), blank=True, null=True)
    gender = models.CharField(_("gender"), max_length=6, choices=GENDER_CHOICES, null=False)
    phone = models.CharField(_("phone"), max_length=15, null=True, blank=True)
    school_display = models.BooleanField(default=True)
    li_profile =  models.URLField(_("li_profile"), null=True, blank=True, verify_exists=False)
    fb_profile = models.URLField(_("fb_profile"), null=True, blank=True, verify_exists=False)
    tw_profile = models.URLField(_("tw_profile"), null=True, blank=True, verify_exists=False)
    photo = models.ForeignKey(Photo, null=True, blank=True, default=settings.DEFAULT_PROFILE_PHOTO_ID, db_index=True) #should be a constant
    album = models.ForeignKey(Album, null=True, blank=True, db_index=True)
    fb_id = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    fb_account_linked = models.BooleanField(default=False)
    fb_stream_publish = models.BooleanField(default=False)
    fb_login = models.BooleanField(default=False)
    source = models.CharField(max_length=150, default='Direct')
    create_date = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)

    _photo = None
    _acc = None # adult_child cache
    _all_friends = None
    _all_pending = None
    _all_friend_invites = None
    _pending_received = None
    _pending_sent = None
    objects = CacheBotManager()

    def name(self):
        return self.first_name + ' ' + self.last_name
    name = property(name)

    def possessive(self):
        if self.gender == 'male':
            return 'his'
        return 'her'

    possessive = property(possessive)

    def third_object(self):
        if self.gender == 'male':
            return 'him'
        return 'her'

    third_object = property(third_object)

    
    
    def can_view_photo(self, user):
        return True

    def can_upload_photo(self, user):
        return user == self.user

    def set_profile_language(self):
        return 'set as your profile photo'

    def get_children_friends(self):
        if getattr(self, '_all_friends') is None:  

            query = "select friends.from_child_id,friends.to_child_id,friends.from_user_id from profiles_adult_child ac, profiles_friendship friends where ac.adult_id = "+str(self.user_id)+" and ac.child_id = friends.to_child_id"

            cursor = connection.cursor()
            cursor.execute(query)

            child_list = {}

            for row in cursor.fetchall():
                from_child_id = row[0]
                to_child_id = row[1]
                from_user_id = row[2]
                child_list[str(from_child_id)] = { 'to_child': to_child_id, 'parent': from_user_id }
            
            self._all_friends = child_list
        
        return self._all_friends
        
    def get_which_child_friend(self, child):
        friends = self.get_children_friends()
        if str(child.id) in friends:
            full_dict = friends[str(child.id)]
            return str(full_dict["to_child"])
        
        return None

    def get_friend_parent(self, child):
        friends = self.get_children_friends()
        if str(child.id) in friends:
            full_dict = friends[str(child.id)]
            return str(full_dict["parent"])
        
        return None


    def is_child_in_network(self, child):
        friends = self.get_children_friends()
        if str(child.id) in friends:
            return True
        else:
            return False

    def is_pending_sent(self, child):
        pending = self.get_pending_sent()
        if str(child.id) in pending:
            return True
        else:
            return False

    def is_pending_received(self, child):
        pending = self.get_pending_received()
        if str(child.id) in pending:
            return True
        else:
            return False

    
    def get_pending_sent(self):
        if getattr(self, '_pending_sent') is None:
            all_friend_invites = self.get_all_friend_invites()
            pending_sent = {}

            mpc = self.manage_playlist_children
            children = []

            for c in mpc:
                children.append(c.child)


            for item in all_friend_invites:
                if item.from_child in children:
                    pending_sent[str(item.to_child_id)] = item.from_child


            self._pending_sent = pending_sent

        return self._pending_sent
    
    
    def get_pending_received(self):
        if getattr(self, '_pending_received') is None:
            all_friend_invites = self.get_all_friend_invites()
            pending_received = {}

            mpc = self.manage_playlist_children
            children = []

            for c in mpc:
                children.append(c.child)

            for item in all_friend_invites:
                if item.to_child in children:
                    pending_received[str(item.from_child_id)] = item.to_child
                    
            self._pending_received = pending_received

        return self._pending_received


    def get_all_friend_invites(self):
        if getattr(self, '_all_friend_invites') is None:  

            mpc = self.manage_playlist_children
            children = []

            for c in mpc:
                children.append(c.child)

            pending_list = {}
            from friends.models import FriendshipInvitation
            from django.db.models import Q
            
            query_list = list(FriendshipInvitation.objects.cache().select_related('from_child','from_child__album','from_child__photo','from_child__school','to_child','to_child__album','to_child__photo','to_child__school').filter(Q(to_child__in=children) | Q(from_child__in=children)).all())
            all_friend_invites = []
            for f in query_list:
                if not self.is_child_in_network(f.to_child):
                    all_friend_invites.append(f)
            
            
            self._all_friend_invites = all_friend_invites
                    
        return self._all_friend_invites


    def get_photo(self):
        if getattr(self, '_photo') is None:  
            self._photo = self.photo
        return self._photo

    def get_mp(self):
        photo = self.get_photo()
        return photo.mp
    
    def get_sp(self):
        photo = self.get_photo()
        return photo.sp
    
    def get_profile(self):
        small_profile_pic = ''
        medium_profile_pic = ''
        if self.photo_id == settings.DEFAULT_PROFILE_PHOTO_ID and self.fb_account_linked:
            small_profile_pic = 'http://graph.facebook.com/' + self.fb_id +'/picture?type=square'
            medium_profile_pic = 'http://graph.facebook.com/' + self.fb_id +'/picture?type=normal'
        else:
            small_profile_pic = self.photo.prof50.url
            medium_profile_pic = self.photo.prof125.url

        tolog(small_profile_pic)
        profile = { 
            'id':self.user.id,
            'gender':self.gender, 
            'small_profile_pic':small_profile_pic,
            'medium_profile_pic':medium_profile_pic,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'zip_code':self.zip_code,
            'location':self.zip_code,
            'name': self.name,
            'possessive': self.possessive,
            'third_object': self.third_object,
        }
        return profile        

    def third_person(self):
        if self.gender == 'male':
            return 'He'
        return 'She'
    third_person = property(third_person)

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            album = Album(title="Profile Photos", created_by=self.user)
            album.save()
            self.album=album;
            new=True
            # create first update
            up = create_update(self.user, "user_joined")
            create_user_update(self.user, up)

        
        super(Profile, self).save(*args, **kwargs)
        if new:
            self.album.owner = self
            self.album.save()

    def set_profile_pic(self, np):
        self.photo=np
        self.save()


    def schools(self):
        schools_dict = {}
        schools = []
        for adult_child in self.display_children:
            if adult_child.child.school is not None:
                schools_dict[adult_child.child.school.id] = adult_child.child.school

        schools = schools_dict.values()
        return schools
    
    schools=property(schools)

    def get_acc(self):
        if self._acc is None:
            self._acc = list(Adult_Child.objects.cache().select_related('child','child__photo','child__album','child__school').filter(adult=self.user))

        return self._acc

    def get_ac(self, child):
        for ac in self.get_acc():
            if ac.child == child:
                return ac
        return None

    def filter_ac(self, attr):
        ac = []
        for adult_child in self.get_acc():
            check = getattr(adult_child, attr)
            if check:
                ac.append(adult_child)

        return ac

    def admin_children(self):
        ac = []
        for adult_child in self.get_acc():
            if adult_child.access_role == 'admin':
                ac.append(adult_child)

        return ac

    admin_children=property(admin_children)

    def has_children(self):
        if len(self.admin_children) > 0:
            return True
        
        return False


    def view_photo_children(self):
        return self.filter_ac('can_view_photos')

    view_photo_children=property(view_photo_children)

    
    def upload_photo_children(self):
        return self.filter_ac('can_upload_photos')

    upload_photo_children=property(upload_photo_children)


    def display_children(self):
        return self.filter_ac('can_display_child')
    
    display_children=property(display_children)

    def manage_playlist_children(self):
        return self.filter_ac('can_edit_playlist')

    manage_playlist_children=property(manage_playlist_children)

    def view_playlist_children(self):
        return self.filter_ac('can_view_playlist')

    view_playlist_children=property(view_playlist_children)

    def edit_schedule_children(self):
        return self.filter_ac('can_edit_schedule')

    edit_schedule_children=property(edit_schedule_children)


    def view_schedule_children(self):
        return self.filter_ac('can_view_schedule')

    view_schedule_children=property(view_schedule_children)


    def edit_playlist_children(self):
        return self.filter_ac('can_edit_playlist')

    edit_playlist_children=property(edit_playlist_children)

    def get_facebook_user(self):
        if not hasattr(self, "_fb_user"):
            try:
                fb_user = FacebookUser.objects.get(user = self.user)
                self._fb_user = fb_user
            except FacebookUser.DoesNotExist:
                self._fb_user = None
        return self._fb_user


    def run_getAppUsers_query(self):
        from account.graphapi import GraphAPI
        fb_user = self.get_facebook_user()

        fb_api = GraphAPI(fb_user.access_token)
        fql="SELECT uid FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1=%s) AND is_app_user" % fb_user.facebook_id
        query_result = fb_api.fql(fql)
 
        friend_fbids = []
        
        for friend in query_result:
            friend_fbids.append(str(friend[u"uid"]))
           
        return friend_fbids

    def get_playdation_contact_friend_users(self):

        contact_list = self.user.contactemail.filter(user__isnull=False)

        friend_list = []
        for contact in contact_list:
            if not self.user == contact.user:
                friend_list.append(contact.user)

        return friend_list


    def get_playdation_contact_non_users(self):

        contact_non_user_list = self.user.contactemail.filter(user__isnull=True)

        return contact_non_user_list



    def get_playdation_fb_friend_users(self, fb_ids):
        friend_list=list(User.objects.filter(fbuser__facebook_id__in=fb_ids).all())
        
#        friend_list = []
#        for friend_fbid in fb_ids:
#            try:
#                friend_fb_users=FacebookUser.objects.filter(facebook_id=friend_fbid)
#                for friend_fb_user in friend_fb_users:
#                    friend_list.append(friend_fb_user.user)       
#            except FacebookUser.DoesNotExist:      
#                pass

        return friend_list


    def title(self):
        return(self.first_name + " " + self.last_name)

    title = property(title)



class FacebookUser(models.Model):
    user = models.ForeignKey(User,unique=True, related_name="fbuser")
    facebook_id = models.CharField(max_length=150, db_index=True)
    access_token = models.CharField(max_length=150,blank=True,null=True)
    queue_for_pull = models.BooleanField(default=True)
    create_date = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)

    name = models.CharField(max_length=150,blank=True,null=True)


    def get_fb_contacts(self):
        from account.graphapi import GraphAPI
        fb_api = GraphAPI(self.access_token)
        res = fb_api.get_connections("me", "friends")
        friends = res["data"]
        return friends

    def get_name(self):
        if self.name is None:
            
            from account.graphapi import GraphAPI
            fb_api = GraphAPI(self.access_token)
            prof = fb_api.get_object("me")
            self.name = prof["name"]
            self.save()

        return self.name

PRIVACY_CHOICES = (
    ('private','Fully Private'),
    ('playlist','Playlist Only'),
    ('public', 'Public'),                                   
)


GRADE_LEVELS = (
    ('PS','Preschool'),
    ('PK','Pre-Kindergarten'),
    ('K','Kindergarten'),
    ('1','First Grade'),
    ('2', 'Second Grade'),
    ('3', 'Third Grade'),
    ('4', 'Fourth Grade'),
    ('5', 'Fifth Grade'),
    ('6', 'Sixth Grade'),
    ('7', 'Seventh Grade'),                                   
)



class Child(models.Model):
    first_name = models.CharField(_("first_name"), max_length=50, null=True, blank=True, db_index=True)
    last_name = models.CharField(_("last_name"), max_length=50, null=True, blank=True, db_index=True)
    about = models.TextField(_("about"), null=True, blank=True)
    gender = models.CharField(_("gender"), max_length=6, choices=GENDER_CHOICES, null=False)
    birthdate = models.DateField(_("birthday"), null=False)
    school = models.ForeignKey(School, null=True, db_index=True)

    anon_prof_privacy = models.CharField(_("anonymous profile privacy level"), max_length=10, choices=PRIVACY_CHOICES, default='public', null=False)
    basic_prof_privacy = models.CharField(_("basic profile privacy level"), max_length=10, choices=PRIVACY_CHOICES, default='playlist', null=False)
    ext_prof_privacy = models.CharField(_("extended profile privacy level"), max_length=10, choices=PRIVACY_CHOICES, default='playlist', null=False)
    playlist_privacy = models.CharField(_("playlist privacy level"), max_length=10, choices=PRIVACY_CHOICES, default='playlist', null=False)
    photo_privacy = models.CharField(_("photo privacy level"), max_length=10, choices=PRIVACY_CHOICES, default='playlist', null=False)    
    schedule_privacy = models.CharField(_("schedule privacy level"), max_length=10, choices=PRIVACY_CHOICES, default='playlist', null=False)
    template = models.CharField(_("template"), max_length=100, null=True, blank=True)
    playdate_requirements = models.TextField(_("playdate requirements"), null=True, blank=True)

    summer_camp = models.TextField(_("summer camp"), null=True, blank=True, default='')

    diet = models.TextField(_("dietary restrictions"), null=True, blank=True, default='')
    foods = models.TextField(_("favorite foods"), null=True, blank=True, default='')
    shows = models.TextField(_("favorite tv shows, movies, books"), null=True, blank=True, default='')
    toys = models.TextField(_("favorite toys"), null=True, blank=True, default='')
    languages = models.TextField(_("languages spoken"), null=True, blank=True, default='')
    sports = models.TextField(_("sports played"), null=True, blank=True, default='')
    activities = models.TextField(_("favorite activities"), null=True, blank=True, default='')
    places = models.TextField(_("favorite places"), null=True, blank=True, default='')
        
        
    grade_level = models.CharField(_("grade level"), max_length=5, choices=GRADE_LEVELS, null=True, blank=True)
    teacher = models.CharField(_("current teacher"), max_length=50, null=True, blank=True)    
    photo = models.ForeignKey(Photo, null=True, blank=True, default=settings.DEFAULT_PROFILE_PHOTO_ID, db_index=True) #should be a constant
    album = models.ForeignKey(Album, null=True, blank=True, db_index=True, related_name='+')

    default_invite_set = models.BooleanField(_("Can Edit Child Profile"), default=False)
    default_invite = models.ForeignKey(InviteDesign, null=True, blank=True, related_name='')
    create_date = models.DateTimeField(default=datetime.datetime.now, blank=True, null=True)


    albums = generic.GenericRelation(Album)

#    adults = models.ManyToManyField(User, through="Adult_Child", related_name="children")

    _photo = None
    _acc = None
    _friends = None

    objects = CacheBotManager()

    def possessive(self):
        if self.gender == 'male':
            return 'his'
        return 'her'

    possessive = property(possessive)

    def can_view_photo(self, user):
        cv = ChildView(user=user, child=self)
        return cv.can_view_child_photos

    def can_upload_photo(self, user):
        cv = ChildView(user=user, child=self)
        return cv.can_upload_child_photos

    def set_profile_language(self):
        return 'set as child profile photo'

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            new = True
            album = Album(title="Profile Photos")
            album.save()
            self.album=album;
        
        super(Child, self).save(*args, **kwargs)
        if new:
            self.album.owner = self
            self.album.save()


    def get_acc(self):
        if self._acc is None:
            self._acc = list(Adult_Child.objects.cache().select_related('adult', 'adult___profile_cache','adult___profile_cache__photo', 'adult___profile_cache_album').filter(child=self))

        return self._acc
        
    def parents(self):
        parents = []
        for ac in self.get_acc():
            if ac.relation == 'P':
                parents.append(ac.adult)

        return parents

    parents = property(parents)


    def caregivers(self):
        parents = []
        for ac in self.get_acc():
            if ac.relation == 'C':
                parents.append(ac.adult)

        return parents

    caregivers = property(caregivers)


    def adults(self):
        parents = []
        for ac in self.get_acc():
            parents.append(ac.adult)

        return parents

    adults = property(adults)


    def friends(self):
        if self._friends is None:

            friends = []
            for fs in Friendship.objects.cache().select_related('from_child','from_child__photo', 'to_child','to_child__album','to_child__photo','to_child__school','to_child__attached_adults').filter(from_child=self.id).all():
                friends.append(fs.to_child)
    
            return friends
            self._friends = friends
        return self._friends
    
    all_friends = property(friends)
    friends = property(friends)

    def set_profile_pic(self, np):
        self.photo=np
        self.save()	

    def age(self):
        from datetime import date
        today = date.today()
        try:
            birthday = date(today.year, self.birthdate.month, self.birthdate.day)
        except:
            birthday = date(today.year, self.birthdate.month, self.birthdate.day-1)

        if birthday > today:
            return today.year - self.birthdate.year - 1
        else:
            return today.year - self.birthdate.year
    age=property(age)


    def anon_photo(crap = None):
        ap = AnonPhoto()
        return ap

    def get_photo(self):
        if getattr(self, '_photo') is None:  
            self._photo = self.photo
        return self._photo

    def get_mp(self):
        photo = self.get_photo()
        return photo.mp
    
    def get_sp(self):
        photo = self.get_photo()
        return photo.sp

    def name(self):
        return(self.first_name + " " + self.last_name)

    title = property(name)
    name = property(name)
    

#    anon_photo = property(anon_photo)

ACCESS_ROLES = (
    ('admin', 'Admin'),
    ('full', 'Full'),
    ('minimal', 'Minimal'),
    ('custom', 'Custom'),
)
        

RELATION_TYPES = (
    ("P","parent"),
    ("GP","grandparent"),
    ("N","nanny"),                             
    ("C","caregiver"),
)


    
class Adult_Child(models.Model):
    adult = models.ForeignKey(User, related_name='attached_children', db_index=True)
    child = models.ForeignKey(Child, related_name='attached_adults', db_index=True)
    relation = models.CharField(max_length=5, choices = RELATION_TYPES)
    can_edit_profile = models.BooleanField(_("Can Edit Child Profile"), default=False)
    can_view_schedule = models.BooleanField(_("Can View Child Schedule"), default=False)
    can_edit_schedule = models.BooleanField(_("Can Edit Child Schedule"), default=False)
    can_view_playlist = models.BooleanField(_("Can View Child Playlist"), default=False)
    can_edit_playlist = models.BooleanField(_("Can Edit Child Playlist"), default=False)
    can_view_photos = models.BooleanField(_("Can View Photos"), default=False)
    can_upload_photos = models.BooleanField(_("Can Upload Photos"), default=False)        
    access_role = models.CharField(_("Access Role"), max_length=10, choices=ACCESS_ROLES, default='admin', null=False)
    can_display_child = models.BooleanField(_("Show Child on Profile?"), default=False)

    objects = CacheBotManager()


    def set_admin_perms(self):
        self.can_edit_profile = self.can_view_schedule = self.can_edit_schedule = self.can_view_playlist = self.can_edit_playlist = True
        self.can_view_photos = self.can_upload_photos = self.can_display_child = True
        self.access_role='admin'

    def is_admin(self):
        if self.access_role == 'admin':
            return True
        return False

    is_admin = property(is_admin)


class ChildPhotoTag(models.Model):
    photo = models.ForeignKey(Photo, related_name="tagged_children")
    child = models.ForeignKey(Child, related_name="tagged_photos")

class PhotoTagNonUser(models.Model):
    photo = models.ForeignKey(Photo, related_name="tagged_nonusers")
    nonuser = models.CharField(max_length=50)


class FriendshipManager(CacheBotManager):
    
    def are_friends(self, user1, user2):
        if self.filter(from_child = user1, to_child=user2).count() > 0:
            return True
        return False
    
    def remove(self, user1, user2):
        self.filter(from_child=user1, to_child=user2).delete()
        self.filter(from_child=user2, to_child=user1).delete()


    def friends_for_user(self, user):
        return user.attached_children.all().child.attached_adults.all()
#        all_friends = self.filter(from_child=user)
#        return(all_friends)


class Friendship(models.Model):
    """
    A friendship is a bi-directional association between two users who
    have both agreed to the association.
    """
    
    from_child = models.ForeignKey(Child, related_name="are_friends", editable=False, db_index=True)
    to_child = models.ForeignKey(Child, related_name="+", editable=False)
    from_user = models.ForeignKey(User, related_name="+", db_index=True)
    to_user = models.ForeignKey(User, related_name="+", db_index=True)
    
    added = models.DateField(default=datetime.date.today, editable=False)
    
    objects = FriendshipManager()
    
    class Meta:
        unique_together = (('from_child','to_child'))


    def save(self, *args, **kwargs):
        
        symmetric_friendship = Friendship()
        symmetric_friendship.from_child=self.to_child
        symmetric_friendship.from_user=self.to_user

        symmetric_friendship.to_child=self.from_child     
        symmetric_friendship.to_user=self.from_user     
        

        super(Friendship,self).save(*args, **kwargs)
        super(Friendship,symmetric_friendship).save(*args, **kwargs)

        return self


class ChildView(object):
    user = None
    child = None
    in_friends = None
    pending_received = None
    pending_sent = None
    my_child = False
    is_parent = None
    is_caretaker = None    
    adult_child = None
    
    def __init__(self, user=None, child=None, adult_child = None, **kwargs):
        if not (isinstance(user, User) or isinstance(user, AnonymousUser)):
            raise Exception("must pass user object to childview")
            
        self.user = user
        
        if not isinstance(child, Child):
            raise Exception("must pass child object to childview")

        self.child = child
        
        if adult_child is not None:
            if not isinstance(adult_child, Adult_Child):
                raise Exception("adult_child must be an Adult_Child object")

            self.adult_child = adult_child
            self.my_child = True

        else:
            if isinstance(user, User):
                ac = user.get_profile().get_ac(child)
#            ac = Adult_Child.objects.get(adult=self.user, child=child)            
                if ac is not None:
                    self.adult_child = ac
                    self.my_child = True

        if self.adult_child is not None:
            if self.adult_child.relation == 'P':
                self.is_parent = True
            elif self.adult_child.relation == 'C':
                self.is_caretaker = True
                
        for key in kwargs:
            if hasattr(self,key):
                setattr(self,key,kwargs[key])
    


#=========================================

    def key(self):
        which_child_friend_id = self.user.get_profile().get_which_child_friend(self.child)
        parent_id = self.user.get_profile().get_friend_parent(self.child)
        
        if which_child_friend_id is None:
            return ''


        key = str(which_child_friend_id) + '_' + str(parent_id) + '_' + str(self.child.id)
        
        return key


    def is_in_friends(self):
        if isinstance(self.user, AnonymousUser):
            return False

        if self.in_friends is None:
            self.in_friends = self.user.get_profile().is_child_in_network(self.child)
            
        return self.in_friends

    is_in_friends = property(is_in_friends)


    def is_pending_sent(self):
        if isinstance(self.user, AnonymousUser):
            return False

        if self.pending_sent is None:
            self.pending_sent = self.user.get_profile().is_pending_sent(self.child)
            
        return self.pending_sent

    is_pending_sent = property(is_pending_sent)


    def is_pending_received(self):
        if isinstance(self.user, AnonymousUser):
            return False

        if self.pending_received is None:
            self.pending_received = self.user.get_profile().is_pending_received(self.child)

        return self.pending_received

    is_pending_received = property(is_pending_received)



    
    def has_required_access(self, required_access):
        if required_access == 'private':
            return False
        elif required_access == 'playlist':
            return self.is_in_friends
        elif required_access == 'public':
            return self.user.is_authenticated()
        else:
            raise Exception('invalid required access'+ str(required_access))


 # just checks whether child is in ac for this parent
    def is_child_mine(self):
        return self.my_child

    is_child_mine = property(is_child_mine)

    def can_admin_child(self):
        if self.my_child:
            return self.adult_child.is_admin
        
        return False

    def can_edit_child_schedule(self):
        if self.my_child:
            return self.adult_child.can_edit_schedule
        
        return False

    can_edit_child_schedule = property(can_edit_child_schedule)
    

    def can_upload_child_photos(self):
        if self.my_child:
            return self.adult_child.can_upload_photos
        
        return False

    can_upload_child_photos = property(can_upload_child_photos)


    def can_edit_child_playlist(self):
        if self.my_child:
            return self.adult_child.can_edit_playlist
        
        return False

    can_edit_child_playlist = property(can_edit_child_playlist)

    def can_edit_child_profile(self):
        if self.my_child:
            return self.adult_child.can_edit_profile
        
        return False

    can_edit_child_profile = property(can_edit_child_profile)

    def can_display_child_on_profile(self):
        if self.my_child:
            return self.adult_child.can_display_child
        
        return False
    
    can_display_child_on_profile = property(can_display_child_on_profile)

# ---------------
# view permissions - can depend on network connection
# ---------------

    def can_view_child_schedule(self):
        if self.my_child:
            if self.adult_child.can_view_schedule:
                return True

        return self.has_required_access(self.child.schedule_privacy)
    can_view_child_schedule = property(can_view_child_schedule)

    def can_view_child_photos(self):
        if self.my_child:
            if self.adult_child.can_view_photos:
                return True

        return self.has_required_access(self.child.photo_privacy)

    can_view_child_photos = property(can_view_child_photos)

    def can_view_child_playlist(self):
        if self.my_child:
            if self.adult_child.can_view_playlist:
                return True

        return self.has_required_access(self.child.playlist_privacy)

    can_view_child_playlist = property(can_view_child_playlist)

    def can_view_child_anon_profile(self):
        if self.my_child:
            return True

        return self.has_required_access(self.child.anon_prof_privacy)

    can_view_child_anon_profile = property(can_view_child_anon_profile)

    def can_view_child_basic_profile(self):
        if self.my_child:
            return True

        return self.has_required_access(self.child.basic_prof_privacy)

    can_view_child_basic_profile = property(can_view_child_basic_profile)


    def can_view_child_extended_profile(self):
        if self.my_child:
            return True

        return self.has_required_access(self.child.ext_prof_privacy)

    can_view_child_extended_profile = property(can_view_child_extended_profile)


#=====================================

    def gender_pretty(self,gender):
        if gender == 'male':
            return 'Boy'
        else:
            return 'Girl'

    def grade_pretty(self,grade):
        suffix = ['th'] + ['st','nd','rd'] + 17*['th'] + ['st','nd','rd'] + 7*['th'] + ['st']
        if grade is not None and len(grade) > 0 and not re.match('^[0-9]+$',grade):
            return grade
        elif grade is not None and len(grade) > 0:
            return grade+suffix[int(grade)] + " Grade"
        else:
            return ""

    def anon_profile(self):

        profile = { 
            'id':self.child.id,
#            'photo':self.child.anon_photo(),
            'gender':self.gender_pretty(self.child.gender), 
            'age':self.child.age, 
            'school':'Private', 
            'small_profile_pic':self.child.anon_photo().prof50.url,
            'medium_profile_pic':self.child.anon_photo().prof125.url,
            'first_name':'Private',
            'last_name':'Private',
            'name': 'Private',
            'grade_level':'Private',
            'teacher':'Private',
            'playdate_requirements':'Private',
            'about': 'Private',
            'diet': 'Private',
            'foods': 'Private',
            'shows': 'Private',
            'toys': 'Private',
            'places': 'Private',
            'languages': 'Private',
            'sports': 'Private',
            'activities': 'Private',
            'summer_camp': 'Private',
            'possessive': self.child.possessive,
            'pending_sent': self.is_pending_sent,
            'pending_received': self.is_pending_received,
            'is_child_mine':self.is_child_mine,
            'is_in_friends':self.is_in_friends,
            'can_view_child_extended_profile':self.can_view_child_extended_profile,
            'can_view_child_basic_profile':self.can_view_child_basic_profile,
                   }
        return profile

    anon_profile=property(anon_profile)

    def basic_profile(self):
        profile = self.anon_profile
        profile.update({
            'school':self.child.school,
            'name': str(self.child.first_name) + ' ' + str(self.child.last_name),
            'first_name':self.child.first_name,
            'last_name':self.child.last_name,
            'grade_level':self.grade_pretty(self.child.grade_level),
            'teacher':self.child.teacher,
            'small_profile_pic':self.child.photo.prof50.url,
            'medium_profile_pic':self.child.photo.prof125.url,
            'album':self.child.album,
            'playdate_requirements':self.child.playdate_requirements,                                
            'about':self.child.about,
            'summer_camp':self.child.summer_camp,
        })
        if profile["playdate_requirements"] is None:
            profile["playdate_requirements"] = ''
        return profile

    basic_profile=property(basic_profile)

    def extended_profile(self):
        profile = self.basic_profile
        profile.update({
            'diet': self.child.diet,
            'foods': self.child.foods,
            'shows':self.child.shows,
            'toys':self.child.toys,
            'languages':self.child.languages,
            'sports':self.child.sports,
            'activities':self.child.activities,
            'places':self.child.places,
        })
        return profile

    
    extended_profile=property(extended_profile)
    

    def get_profile(self):
        if self.can_view_child_extended_profile:
            return self.extended_profile        
        if self.can_view_child_basic_profile:
            return self.basic_profile
        else:
            return self.anon_profile
 
    profile = property(get_profile)

def create_childview(user, child, adult_child = None):
    cv = ChildView(user=user, child=child, adult_child = adult_child)
    
    return cv

def get_cv_list_from_ac(user, list_of_ac):
    lst = []
    for ac in list_of_ac:
        if not isinstance(ac, Adult_Child):
            raise Exception('get_cv_list_from_ac requires ac objects to operate on')

        lst.append(create_childview(user=user, child=ac.child))


    return lst
