from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from views import * 

urlpatterns = patterns('',                                          
#    url(r'^$', direct_to_template, { "template": "homepage.html", }, name="old_home"),
    url(r"^$", "home.views.home", name="home"),
    url(r"^new$", "home.views.new_home", name="new_home"),
    url(r"^get_condensed_calendar/(?P<child_id>\d+)/$", "home.views.get_condensed_calendar", name="get_condensed_calendar"),
    url(r"^get_signup_friends/$","home.views.get_signup_friends", name="get_signup_friends"),
    url(r"^import_generic", "home.views.import_generic", name="import_generic"),
    url(r"^save_email_list", "home.views.save_email_list", name="save_email_list"),
    url(r"^get_non_user_contacts", "home.views.get_non_user_contacts", name="get_non_user_contacts"),
    url(r"^invite_by_email", "home.views.invite_by_email", name="invite_by_email"),
    url(r"^import_email_list", "home.views.import_email_list", name="import_email_list"),
    url(r"^import_facebook_friends/$","home.views.import_facebook_friends", name="import_facebook_friends"),
    url(r"^get_suggested_friends/$","home.views.get_suggested_friends", name="get_suggested_friends"),
)
