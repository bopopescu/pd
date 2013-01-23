from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from datetime import datetime

from mydebug import *
from django.contrib.contenttypes import generic

from imagekit.models import ImageModel
from comments.models import Comment
from cachebot.managers import CacheBotManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from specs import *

class Album(models.Model):
    title = models.CharField(_('title'), max_length=101)
    date_added = models.DateTimeField(_('date published'), default=datetime.now)
    created_by = models.ForeignKey(User, related_name='albums', null=True, blank=True, db_index=True)
    description = models.TextField(_('description'), blank=True)
    comments = generic.GenericRelation(Comment)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    owner = generic.GenericForeignKey('content_type', 'object_id')

    objects = CacheBotManager()

   
    class Meta:
        app_label='photos'
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = _('gallery')
        verbose_name_plural = _('galleries')

    def can_view_album(self, user):
        if not user.is_authenticated():
            return False

        owner = self.owner
        return owner.can_view_photo(user)

    def can_upload_photo(self, user):
        if not user.is_authenticated():
            return False
        owner = self.owner
        return owner.can_upload_photo(user)

    def can_delete_photo(self, user):
        if not user.is_authenticated():
            return False

        owner = self.owner
        return owner.can_upload_photo(user)

    def owner_name(self):
        return self.owner.name

    def set_profile_language(self):
        if not user.is_authenticated():
            return False

        return self.owner.set_profile_language()
        


    owner_name = property(owner_name)

class AnonSpec(object):
    size = None
    base_img = '/static/images/placeholder_prof'
    base_ext = '.jpg'

    def __init__(self, size = None):
        if size is not None:
            self.size = size
        else:
            self.size = '50'

    def url(self):
        return self.base_img + self.size + self.base_ext

    url = property(url)


class AnonPhoto(object):
    def prof50(self):
        pa = AnonSpec(size='50')
        return pa

    prof50 = property(prof50)

    def prof125(self):
        pa = AnonSpec(size='125')
        return pa

    prof125 = property(prof125)




class Photo(ImageModel):
    caption = models.CharField(max_length=201)
    original_image = models.ImageField(upload_to='photos')
    date_added = models.DateTimeField(_('date added'), default=datetime.now)
    album = models.ForeignKey(Album, related_name='photos', db_index=True)

    comments = generic.GenericRelation(Comment)

    objects = CacheBotManager()

    class IKOptions:
        spec_module = 'photos.specs'
        cache_dir = 'photos/'
        image_field = 'original_image'
        preprocessor_spec = Original

    class Meta:
        app_label='photos'
        ordering = ['-date_added']
        get_latest_by = 'date_added'
        verbose_name = _("photo")
        verbose_name_plural = _("photos")


    def mp(self):
        return self.prof125.url

    def sp(self):
        return self.prof50.url

    def can_view_photo(self, user):
        if not user.is_authenticated():
            return False

        owner = self.album.owner
        return owner.can_view_photo(user)

    def can_view_comments(self, user):

        return self.can_view_photo(user)

    def can_delete_photo(self, user):
        if not user.is_authenticated():
            return False

        owner = self.album.owner
        return owner.can_upload_photo(user)

def create_image(id, album, caption, image_location):
    try:
        np = Photo.objects.get(id=id)
        if np.caption == caption:
            return np
    except Photo.DoesNotExist:     
        np = Photo()

    f = open(image_location, 'r')
    from django.core.files import File
    im = File(f)
    
    np.caption = caption
    np.original_image = im
    np.album = album

    np.save()

    return np
 
    

def create_album(id,title):
    try:
        na = Album.objects.get(id=id)
        if na.title == title:
            return na
    except Album.DoesNotExist:     
        na = Album()

    na.title = title
    na.save()
    return na 


def get_photos_for_children(children, num = None):
    albums = []
    cids = []
    for c in children:
        cids.append(c.id)

    if num is None:
        num = 999

    from django.contrib.contenttypes.models import ContentType
    prt = ContentType.objects.get(app_label="profiles", model="child")

    photos = Photo.objects.cache().filter(album__content_type=prt, album__object_id__in=cids)[0:num]

    return photos

