from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from views import * 

urlpatterns = patterns('',                                          
    url(r"^setstatus", "mobile.views.setstatus", name="mobile_setstatus"),
)
