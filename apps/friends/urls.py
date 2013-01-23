from django.conf.urls.defaults import *
from django.conf import settings
from views import * 

urlpatterns = patterns('',
#   url(r'^invite/(?P<contact_id>[0-9]+)/$', invite_contact, name="invite_contact"),
#   url(r'^edit/(?P<contact_id>[0-9]+)/$', edit_contact, name="edit_contact"),
#   url(r'^edit/(?P<friend>[-\w\.]+)/$', edit_friend, name="edit_friend"),
#   url(r'^add/(?P<friend>[-\w\.]+)/$', add_friend, name="add_friend"),
#   url(r'^remove/(?P<contact_id>[0-9]+)/$', remove_contact, name="remove_contact"),
#   url(r'^remove/(?P<friend>[-\w\.]+)/$', remove_friend, name="remove_friend"),
#   url(r'^invite/$', invite_users, name="invite_users"),
#   url(r'^invite/imports/$', invite_imported, name="invite_imported"),
#   url(r'^recommended/$', recommended_friends, name="recommended_friends"),
#   url(r'^invitations/$', invitations_sent, name="invitations_sent"),
#   url(r'^requests/$', requests_received, name="requests_received"),
#   url(r'^accept/(?P<friend>[\w\.]+)/$', accept_friendship, name="accept_friend"),
#   url(r'^decline/(?P<friend>[\w\.]+)/$', reject_friendship, name="reject_friendship"),
#   url(r'^join/(?P<key>[a-z0-9]+)/?$', accept_invitation, name="friends_accept_join"),
#   url(r'^addressbook/$', addressbook, name="edit_contacts"),
#   url(r'^import/file/$', import_file_contacts, name="import_file_contacts"),
#   url(r'^import/google/$', import_google_contacts, name="import_google_contacts"),
#   url(r'^(?P<user>[-\w\.]+)/$', view_friends, name="view_friends"),
#   url(r'^$', edit_friends, name="edit_friends"),

    url(r'^join/(?P<key>[a-z0-9]+)/?$', "friends.views.accept_invitation", name="friends_accept_join"),

    url(r"^suggested/(?P<child_id>\d+)/$", "friends.views.suggested_friends", name="suggested_friends"),
    url(r"^suggested/$", "friends.views.suggested_friends", name="suggested_friends"),
    url(r'^add_friend/$', "friends.views.add_friend", name="add_friend"),
    url(r'^confirm_friend/$', "friends.views.confirm_friend", name="confirm_friend"),
    url(r'^remove_friend_suggestion/$', "friends.views.remove_friend_suggestion", name="remove_friend_suggestion"),
    url(r"^view/(?P<child_id>\d+)/$","friends.views.view_playlist", name="view_playlist"),
    url(r"^view/$","friends.views.view_playlist", name="view_playlist"),
    url(r"^get_profiles/(?P<child_id>\d+)/$","friends.views.get_profiles", name="get_profiles"),
    url(r"^contacts/$", "friends.views.contacts", name="contacts"),
    url(r"^remove_contact/(?P<contact_id>\d+)/(?P<contact_type>\w+)/$","friends.views.remove_contact", name="remove_contact"),
)

