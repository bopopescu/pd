from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from views import * 

urlpatterns = patterns('',                                          
    url(r"^search", "search.views.search", name="search"),
)
