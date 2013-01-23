from django.db import models
from django.contrib.auth.models import User
from cachebot.managers import CacheBotManager


class Place(models.Model):
    owner = models.ForeignKey(User, related_name="places", db_index=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    objects = CacheBotManager()

    class Meta:
        app_label='places'


class Zip(models.Model):
    zip = models.CharField(max_length=10, db_index=True, unique=True)
    state = models.CharField(max_length=2)
    lat = models.CharField(max_length=10)
    lon = models.CharField(max_length=10)
    city = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    state_full = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    objects = CacheBotManager()

    class Meta:
        app_label='places'

    def __str__(self):
        return self.city + ' ' + self.state
  

class Zip_Prox(models.Model):
    zip = models.ForeignKey(Zip, related_name='zip_prox', db_index = True)
    prox_zip = models.ForeignKey(Zip, related_name='+', db_index = True)
    dst = models.CharField(max_length=5)
    
    objects = CacheBotManager()

    class Meta:
        app_label='places'
