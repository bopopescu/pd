from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from datetime import datetime

class Comment(models.Model):
    user = models.ForeignKey(User, related_name='+', blank=True, null=True)
    user_email = models.EmailField(blank = True, null=True)
    added = models.DateTimeField(default=datetime.now)
    comment = models.TextField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    item = generic.GenericForeignKey('content_type', 'object_id')
               
                                                                                                                                       
    class Meta:
        app_label = 'comments'
        ordering = ["-added"]

