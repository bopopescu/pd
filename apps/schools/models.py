from django.db import models
from cachebot.managers import CacheBotManager
from places.models import Zip
SCHOOL_TYPES = (
    ("P","preschool"),
    ("K","kindergarten"),
    ("E","elementary"),
    ("M","middle"),
    ("A","all"),
)

class School(models.Model):
    gsid = models.CharField(max_length=15, db_index=True, unique=True)
    name = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True )
    state = models.CharField(max_length=2, null=True, blank=True, db_index=True)
    zip = models.CharField(max_length=8, null=True, blank=True, db_index=True)
    lat = models.CharField(max_length=15, null=True, blank=True)
    lon = models.CharField(max_length=15, null=True, blank=True)
    district_name = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    level = models.CharField(max_length=20, null=True, blank=True)
    gsurl = models.CharField(max_length=300, null=True, blank=True)

    pd = models.BooleanField(default=False)

    objects = CacheBotManager()

    def summary(self):
        summary = ''
        if self.city is not None:
            summary = summary + self.city + "'s"
            
        summary = summary + ' ' + self.name 
        
        if self.level is not None:
            summary = summary + ' serves grades ' + self.level
            
        if self.district_name is not None and len(self.district_name) > 0:
            summary = summary + ' in the ' + self.district_name
            
        summary = summary + '.'
        
        return summary
        
        

    summary = property(summary)

    def short_name(self):
        if len(self.name) > 20:
            return self.name[0:17]+"..."
        return self.name
    short_name = property(short_name)



class Zip_School_Prox(models.Model):
    zip = models.ForeignKey(Zip, related_name='school_prox', db_index = True)    
    school = models.ForeignKey(School, related_name='+', db_index = True)
    dst = models.CharField(max_length=5)
    name = models.CharField(max_length=100, null=True, blank=True)
  
    class Meta:
        unique_together = ("zip", "school")

    objects = CacheBotManager()



class PD_School(models.Model):
    name = models.CharField(max_length=100, db_index=True)
