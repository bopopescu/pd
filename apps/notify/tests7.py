from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from django.db import connection
from django import db

from mydebug import * 

from models import *
from profiles.models import Child
from django.contrib.auth.models import User
from playdates.models import *
import time

def get_plural(num, word):
   suffix = ''
   if num > 1:
     suffix = 's'

   return str(num) + ' ' + word + suffix


def get_status_date_format(when):
  from datetime import datetime, timedelta
  now = datetime.now()
  future = False
  diff = None
  if when < now:
    diff = now - when
  else:
    diff = when - now
    future = True

  HOUR = 60 * 60
  TWO_HOUR = 2 * HOUR
  EIGHT_HOUR = 4 * HOUR

  str_when = ''

  if diff.days >= 1:
    num = int(diff.days)
    str_when = get_plural(num, 'day')

  elif diff.seconds > 8 * HOUR:
    num = int(diff.seconds / HOUR)
    str_when = get_plural(num, 'hour')

  elif diff.seconds > HOUR:
    num_hours = int(diff.seconds / HOUR)
    hours_str_when = get_plural(num_hours, 'hour')

    num_minutes = ((diff.seconds - num_hours * HOUR) / 60)
    minutes_str_when = get_plural(num_minutes, 'minute')

    str_when = hours_str_when + ' ' + minutes_str_when


  else:
    num = int(diff.seconds / 60)
    str_when = get_plural(num, 'minute')

  if future:
    str_when = 'in ' + str_when
  else:
    str_when = str_when + ' ago'

  return str_when


from datetime import datetime, timedelta

when = datetime.now() + timedelta(hours=12)

gsdf = get_status_date_format(when)

print str(gsdf)


