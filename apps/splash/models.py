from django.db import models
from datetime import datetime, timedelta
from django.conf import settings


# Create your models here.

class WaitingList(models.Model):
    email = models.EmailField(db_index=True)
    zip_code = models.CharField(max_length=7)
    signup_date = models.DateTimeField(default=datetime.now)
