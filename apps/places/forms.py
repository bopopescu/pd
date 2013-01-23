from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib import messages

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from django.forms.formsets import formset_factory

from django.core.validators import validate_email

from emailconfirmation.models import EmailAddress

from profiles.models import Profile
from profiles.models import Child
from profiles.models import Adult_Child

import datetime
import re

from django.utils.safestring import mark_safe

from account.forms import CustomSelectDateWidget

from widgets import *
from models import *

from mydebug import *

from django.core.validators import email_re




RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')


alnum_re = re.compile(r"^\w+$")
