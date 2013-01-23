from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from views import * 

urlpatterns = patterns('',                                          
    url(r"^view/(?P<school_id>\w+)/$", "schools.views.view_school", name="view_school"),
    url(r"^zip_search/$", "schools.views.search_school_zip", name="search_school_zip"),
)
