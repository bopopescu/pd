from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from django.db import connection
from django import db

from mydebug import * 

from models import MessagePreference, MessagePreferenceDefaults, Update, InternalMessage, Email, FBPost, create_message_content, create_message, get_message_content, inbox_count_for, create_update, send_email
from profiles.models import Child
from django.contrib.auth.models import User
from playdates.models import *
import time

max_limit=5


create_message_content('facebook', 'playdate_request_received', '{{ actor.first_name }} {{ actor.last_name}} has a special invitation to you on Playdation.')
#create_message_content('facebook', 'playdate_request_received', '{{ actor.first_name }} {{ actor.last_name}} has a special personal invitation for you to Playdation. Click <a href="here">here</a> to retrieve it!')



#user = User.objects.get(email='example@demo.com')

#db.reset_queries()

#thing = user.updates.select_related('update').filter(update__deleted__isnull=True)[:max_limit]

#thing = user.updates.select_related('update').filter(update__deleted='0')[:max_limit]

#for e in thing:
#    print e.update.id

# print len(connection.queries)

#create_message_content('message', 'playdate_attendance_maybe', '{% if email %}{{email}}{% else %}{{ actor.first_name }} child {{ actor_child.first_name }}{%endif%} has responded maybe to attend {{ actee_child.first_name }} playdate.')
#create_message_content('message', 'playdate_attendance_maybe', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }} {{ actor_child.last_name}}{%endif%}  has responded maybe to your playdate invite', 'subject')
#create_message_content('email', 'playdate_attendance_maybe', '{% if email %}{{email}}{% else %}{{ actor.first_name }} child {{ actor_child.first_name }}{%endif%} has responded maybe to attend {{ actee_child.first_name }} playdate.')
#create_message_content('email', 'playdate_attendance_maybe', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }} {{ actor_child.last_name}}{%endif%} has responded maybe to your playdate invite.', 'subject')

#create_message_content('update','status_update_other','<b>{{ actor.first_name }}: {{ status }} with {{ actor_child.first_name}}. When: {{ when }}</b>')
#create_message_content('update','status_update_self','<b>{{ actor.first_name }}: {{status}} with {{ actor_children }}. When: {{ when }}</b>')
#create_message_content('update','status_update','<b>{{ actor.first_name }}: {{status}} with {{ actor_children }}. When: {{ when }}</b>')



#create_message_content('facebook', 'user joined', '{{ actor.first_name }} has joined Playdation!')
#
#create_message_content('update', 'user joined', '{{ actor.first_name }} has joined Playdation!')
## create_message_content('update', 'user joined', 'Awesome header!','header')
#
#create_message_content('update', 'user2 joined', 'Awesomeness here!'+str(time.time()))
#
#
#create_message_content('message', 'playdate request sent', '{{ actor.first_name }}\'s child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="#">here</a> for details')
#create_message_content('message', 'playdate request sent', '{{ actor_child.first_name }} {{ actor_child.last_name}}  has invited your child to a playdate.', 'subject')
#
#create_message_content('email', 'playdate request sent', '{{ actor.first_name }}\'s child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="#">here</a> for details')
#create_message_content('email', 'playdate request sent', '{{ actor_child.first_name }} {{ actor_child.last_name}}  has invited your child to a playdate.', 'subject')
#
#
#create_message_content('message','playlist_request_received', '{{ actor.first_name }} wants to add your child {{ actee_child.first_name }} to their child\'s {{ actor_child.first_name }} playlist')
#create_message_content('message','playlist_request_received', 'Someone wants to add your child to their child\'s playlist', 'subject')
# 
#
##print "MSGC: " + get_message_content('message','playdate request sent')
#
#
## msg = FBPost(type='user joined')
##print msg.get_content('header')
#
#user2=User.objects.get(id=1);
#user1=User.objects.get(id=2);
#
#child1=Child.objects.get(id=1);
#child2=Child.objects.get(id=2);
#
#type='playdate request sent'
#
#ctx = {
#    'actor': user1.get_profile(),
#    'actee': user2.get_profile(),
#    'actor_child':child1,
#    'actee_child':child2
#}
#


#post_to_facebook(user2, 'user joined', ctx)

#print str(user1.updates.all())

#ctx = {
#    'profile': user2.get_profile()
#}

#create_update(user1, 'user2 joined', ctx)
#create_update(user1, 'user2 joined', ctx)
#create_update(user1, 'user2 joined', ctx)
#create_update(user1, 'user2 joined', ctx)



#type='playlist_request_received'
#create_message(user1, user2, type, ctx )




#to_list = [ 'braskin@playdation.com', 'boris@playdation.com' ]

#send_email('braskin@playdation.com' ,type, ctx)



# print str(inbox_count_for(user2))

# msg.get_content('header'), msg.get_content(), ctx) 



#   def get_content_part(self, part="body"):
#        try:
#            content = MessageContent.objects.get(medium=self.medium, type=self.type, part=part)
#            return content.content
#        except MessageContent.DoesNotExist:
#            return None
#
#
#
#
# def create_message_content(type, medium, content, part = 'body'):

#class MessageContent(models.Model):
#    # friend_request, photo_tagged, added_child, etcc.
#    type = models.CharField(_('Message Type'), max_length=20)
#    # update , message, email, fbpost
#    medium = models.CharField(_('Medium'), max_length=20, choices = MESSAGE_MEDIA)
#    # subject vs body - some message types don't need a subject
#    part = models.CharField(_('Message Part'), max_length=20, choices = MESSAGE_PARTS)
#    # actual django content template string.
#    content = models.TextField(_("Content"))
#
#    class Meta:
#        unique_together = ("type","medium", "part")
#        app_label='notify'
#
