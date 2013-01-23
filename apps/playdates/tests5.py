from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)



from profiles.models import Child, Adult_Child, Profile, FacebookUser, Friendship
from friends.models import ContactFB
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from django.db import connection

from models import *
from schedule.models import *
from django.core.validators import email_re
from datetime import datetime
import re
from time import time

from django.core.validators import email_re

from management import create_playdate_invite_designs, create_playdate_activities


create_playdate_invite_designs('blah','blah','blah')
create_playdate_activities('blah','blah','blah')
    
