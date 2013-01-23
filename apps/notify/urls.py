from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from notify.views import *

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url': 'inbox/'}),
    url(r'^inbox/$', inbox, name='messages_inbox'),
    url(r'^outbox/$', outbox, name='messages_outbox'),
    
    url(r'^reply/(?P<message_id>[\d]+)/$', reply, name='messages_reply'),
    url(r'^view/(?P<message_id>[\d]+)/$', view, name='message_detail'),

    url(r'^delete/(?P<message_id>[\d]+)/$', delete, name='messages_delete'),
    
    url(r'^undelete/(?P<message_id>[\d]+)/$', undelete, name='messages_undelete'),
    url(r'^trash/$', trash, name='messages_trash'),
    url(r'^get_updates/$', get_updates, name='ajax_get_updates'),
    url(r'^delete_update/$', delete_update, name='delete_update'),
    url(r"^update_status/$", "notify.views.update_status", name="update_status"),
    url(r"^send_message/$", "notify.views.send_message", name="send_message"),
)
