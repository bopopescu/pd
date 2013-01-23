from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic

from itertools import *
from mydebug import *
import simplejson

from cachebot.managers import CacheBotManager

    
class InviteDesign(models.Model):
    subject = models.CharField(max_length=140, db_index=True, null=True, blank=True)
    html = models.TextField(_("Design HTML"))
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(_("Design Description"), null=True, blank=True)
    small_image = models.URLField(max_length=200, null=True, blank=True)
    big_image = models.URLField(max_length=200, null=True, blank=True)

    objects = CacheBotManager()


    class Meta:
        app_label='playdates'


def create_playdate_invite_design(title=None, subject=None, html=None, small_image=None, big_image=None, description=None):
    if html is None:
        raise Exception("Can not create playdate invite design without HTML")

    if title is None:
        raise Exception("Can not create playdate invite design without Title")

    update = False
    pdid = None
    try:
        pdid = InviteDesign.objects.get(title=title)
        if pdid.html == html \
                and (description is not None and pdid.description == description) \
                and (small_image is not None and pdid.small_image == small_image) \
                and (big_image is not None and pdid.big_image == big_image) \
                and (subject is not None and pdid.subject == subject):
            return True # unchanged
    except InviteDesign.DoesNotExist:
        pdid = InviteDesign()

    pdid.html = html
    pdid.small_image = small_image
    pdid.big_image = big_image
    pdid.description = description
    pdid.title = title
    pdid.subject = subject
    
    pdid.save()
