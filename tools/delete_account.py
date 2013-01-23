
from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)


from django.contrib.auth.models import User
import re
from django.db.models import Q
from account.views import remove_account

# email = 'boris@riskborn.com';
email = 'boris@playdation.com';

user = User.objects.get(email=email)

remove_account(user)
