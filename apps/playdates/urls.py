from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from views import * 

urlpatterns = patterns('',                                          
    url(r"^new/$", "playdates.views.new_playdate", name="new_playdate"),
    url(r"^new/(?P<key>\w+)/$", "playdates.views.new_playdate", name="new_playdate_with_key"),
    url(r"^new/(?P<key>\w+)/(?P<start>\d+)/(?P<end>\d+)/", "playdates.views.new_playdate", name="new_playdate_with_key_and_time"),
    
    url(r"^view/(?P<playdate_id>\d+)/$", "playdates.views.view_playdate", name="view_playdate"),

    url(r"^list/(?P<child_id>\d+)/$", "playdates.views.list_playdates", name="list_playdates"),
    url(r"^list/$", "playdates.views.list_playdates", name="list_playdates"),
    url(r"^viewem/(?P<playdate_id>\d+)/(?P<token>\w+)/$", "playdates.views.view_playdate_with_token", name="view_playdate_with_token"),
    url(r"^viewfb/(?P<playdate_id>\d+)/(?P<invite_id>\d+)$", "playdates.views.view_playdate_with_fb", name="view_playdate_with_fb"),
    url(r"^(?P<playdate_id>\d+)/playdate_in_place_save/$", "playdates.views.playdate_in_place_save", name="playdate_in_place_save"),
    url(r"^(?P<playdate_id>\d+)/playdate_in_place_save_date/$", "playdates.views.playdate_in_place_save_date", name="playdate_in_place_save_date"),
    url(r"^(?P<playdate_id>\d+)/save_optional_info/$", "playdates.views.save_optional_info", name="save_optional_info"),
    url(r"^pd_fb_login/(?P<playdate_id>\d+)/(?P<invite_id>\d+)$", "playdates.views.pd_fb_login", name="pd_fb_login"),
    url(r"^pd_fb_auth/(?P<playdate_id>\d+)/(?P<invite_id>\d+)$", "playdates.views.pd_fb_auth", name="pd_fb_auth"),
    url(r"^set_invite_choices", "playdates.views.set_invite_choices", name="set_invite_choices"),
    url(r"^get_oc_pd_friends/$", "playdates.views.get_oc_pd_friends", name="get_oc_pd_friends"),
    url(r"^get_fb_friends/$", "playdates.views.get_fb_friends", name="get_fb_friends"),
    url(r"^get_e_friends/$", "playdates.views.get_e_friends", name="get_e_friends"),
    url(r"^cancel/(?P<playdate_id>\d+)/$", "playdates.views.cancel_playdate", name="cancel_playdate"),
)
