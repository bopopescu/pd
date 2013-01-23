from django.db.models import get_models, signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _

from notify import models as notify


email_header = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Email</title>
</head>
<body style="font-family:Tahoma, Geneva, sans-serif; background:#fff;">
<table width="100%" border="0" cellspacing="0" cellpadding="0" style="background:#fff; font-family:Tahoma, Geneva, sans-serif; font-size:12px;">
    <tr>
        <td align="center">
        <table width="600" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td>
                <table width="600" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td height="30">
                        </td>
                    </tr>
                    <tr>
                        <td align="left">
                        <a href="http://"""+settings.WWW_HOST+"""/home"><img src="http://"""+settings.WWW_HOST+"""/static/images/img_logo.png" width="284" height="68" alt="logo" style="border:0; margin:0; padding:0; vertical-align:top;" /></a>
                        </td>
                    </tr>
                    <tr>
                        <td height="40">
                        </td>
                    </tr>
                </table>
                </td>
            </tr>
            <tr>
                <td>
                <table width="600" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td align="left" style="font-size:22px; color:#6c6b6b; line-height:30px;  font-family:'Times New Roman', Times, serif; align:left;">
"""                        

email_footer = """
                        </td>
                    </tr>
                    <tr>
                        <td height="25">
                        </td>
                    </tr>
                </table>
                </td>
            </tr>
            <tr>
                <td>
                <table width="520" border="0" cellspacing="0" cellpadding"0" style=" background:#f2f2f2;" >
                            <tr>
                                <td height="15" colspan="3">
                                </td>
                            </tr>
                            <tr>
                                <td width="30">
                                </td>
                                <td width="460" style="font-size:11px; font-family:Tahoma, Geneva, sans-serif; color:#2a80b7;">
                                <a href="http://"""+settings.WWW_HOST+ """/home" style="color:#2a80b7; text-decoration:none;">Log into your Playdation account for details.</a>
                                </td>
                                <td width="30">
                                </td>
                            </tr>
                            <tr>
                                <td height="10" colspan="3">
                                </td>
                            </tr>
                        </table>
                </td>
            </tr>
            
            <tr>
                <td height="81">
                
                </td>
            </tr>
            <tr>
                <td align="left" valign="top">
                <table width="600" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td valign="top"><img src="http://www."""+settings.WWW_HOST+"""/static/images/img_line_long.png" width="600" height="1" alt="" style="margin:0; padding:0; border:0; vertical-align:top;" /></td>
  </tr>
  <tr>
    <td style="font-family:Tahoma, Geneva, sans-serif; font-size:10px; color:#aaa; line-height:19px; letter-spacing:1px;">This message is service email related to your use of Playdation. To change your email settings, <a href="http://"""+settings.WWW_HOST+ """/account/settings/communication" style="color:#2a80b7; text-decoration:none;">click here.</a> Please add notification@playdation.com to your address book to ensure deliverability of all future Playdation email. Playdation, Inc. 412 Broadway, Floor2, New York City, NY 10013</td>
  </tr>
</table>

                </td>
            </tr>
            <tr>
                <td height="30">
                </td>
            </tr>
        </table>
        </td>
    </tr>
</table>
</body>
</html>
"""

basic_footer = """
                        </td>
                    </tr>
                    <tr>
                        <td height="25">
                        </td>
                    </tr>
                </table>
                </td>
            </tr>
        </table>
        </td>
    </tr>
</table>
</body>
</html>

"""


join_invitation_content = """
Your friend {{ actor.name }} and some of the other parents you may know are using Playdation and would like you to join them!<br><br>

Playdation makes it super easy to schedule activities for your children with their friends.<br><br>

Click <a href="{{accept_url}}">here</a> to accept {{ actor.first_name}}'s invitation<br><br>

Already a Playdation member?<br>
Click <a href="http://"""+settings.WWW_HOST+"""/{% url view_profile actor.user_id %}">here</a> to connect with {{ actor.name }}<br><br><br>

-The Playdation Team<br><br>

<span style="font-size:small; line-height:1;">Please do not reply to this message; it was sent from an unmonitored email address.  This message was intended for {{ email }}. Please remember to add mail@playdation.com to your address book to ensure deliverability of all future playdate invitations!</span>
"""

email_confirmation_content = """
Howdy,<br><br>

Please confirm your Playdation account by clicking this link:
<a href="{{ activate_url }}">{{activate_url}}</a><br><br>

Once you confirm, you will have full access to Playdation and all future notifications will be sent to this email address.<br><br>

- The Playdation Team<br><br>

<small>If you received this message in error and did not sign up for a Playdation account, ignore this message. Please do not reply to this message; it was sent from an unmonitored email address. This message is a service email related to your use of Playdation. For general inquiries or to request support with your Playdation account, please visit us at Playdation Support. Please remember to add notification@playdation.com to your address book to ensure deliverability of all future playdate invitations!</small>
"""


welcome_email_content = """
{{ actor.get_profile.first_name }}, <br><br>

Welcome to Playdation!
<br><br>

We're excited you're here! Playdation is a free service for parents to help you plan your child's social life.
<br><br>

<b>Get started on Playdation:</b>
<br><br>
<b>1.  Discover other parents on Playdation</b><br>
Browse our <a href="http://"""+settings.WWW_HOST+"""/{% url suggested_friends %}">Possible Friends</a> feature or use our Search tool to find parents you already know that are using Playdation.<br><br>

<b>2. Make fun plans for your kids</b><br>
<a href="http://"""+settings.WWW_HOST+"""/{% url new_playdate %}">Schedule a Playdate</a> for the upcoming week or go to your child's very own <a href="http://"""+settings.WWW_HOST+"""/{% url view_calendar %}">Calendar</a> to enter their availability to play with their friends.<br><br>

<b>3. Check back often</b><br>
Visit <a href="http://"""+settings.WWW_HOST+"""/home">Playdation</a> often to find fun child-friendly events in your area and good friends to enjoy them with!

<br><br>

<a href="http://"""+settings.WWW_HOST+"""/home">Click. Connect. Create some play!</a><br><br>

<i>-The Playdation Team (<a href="http://www.twitter.com/playdation">@playdation</a>)</i><br><br>

<span style="font-size:85%; line-height:1;">Please do not reply to this message; it was sent from an unmonitored email address.  This message was intended for {{ actor.user.email }}.
Please remember to add notification@playdation.com to your address book to ensure deliverability of all future playdate invitations!</span>
"""

email_confirmation_content = """
Howdy,<br><br>

Please confirm your Playdation account by clicking this link:
{{ activate_url }}<br><br>

Once you confirm, you will have full access to Playdation and all future notifications will be sent to this email address.<br><br>

-The Playdation Team<br><br>

<small>If you received this message in error and did not sign up for a Playdation account, ignore this message. Please do not reply to this message; it was sent from an unmonitored email address. This message is a service email related to your use of Playdation. For general inquiries or to request support with your Playdation account, please visit us at Playdation Support. Please remember to add notification@playdation.com to your address book to ensure deliverability of all future playdate invitations!</small>
"""


beta_invite_content = """
Dear Parent,<br><br>

Earlier this year you signed up for a free service that promised to make your life easier and provide more opportunity for your children to play. Well, after tens of thousands of hours of writing computer code, designing pixels and architecting the product, we are proud to take the wraps of Playdation.  Playdation is a free service to help you manage <a href="http://www.playdation.com">your child's social life</a>.   

<br><br>
As parents ourselves, we have tried to address some of the most challenging problems around child socializing and scheduling.  Hopefully we got it right.  We aren't perfect, however, and there may still be a few bugs and ways to make the product even better!  We are counting on our users to tell us about things we did wrong or how we can make the service even more valuable for you. Please go to <a href="http://www.playdation.com">www.playdation.com</a> to sign up and start using Playdation today!  

<br><br>
The more friends that you invite to use Playdation, the more valuable the service becomes so please do spread the word!  We're sure you are anxious to get started so go ahead and <a href="http://www.playdation.com">Click, Connect, Create Some Play</a>! 

<br><br>
cheers,<br>
<i>-The Playdation Team</i>
"""

beta_2_invite_content = """
Dear Parents,<br><br>
 
Earlier this year you signed up for a free service that promised to make your life as a parent easier and provide more opportunities for your children to play.  Well, after a ton of hard work, we are pleased to present Playdation.  Playdation is a free service designed to help you privately manage your child's busy social life.  As parents ourselves, we have tried to address some of the biggest challenges surrounding child socializing and scheduling.   Please go to <a href="http://www.playdation.com/t/beta_invite">www.playdation.com</a> to start start planning your child's social life today!   If you like what you see, be sure to tell other parents you know since the more parents that use Playdation, the more valuable the product becomes.  We know you are eager to get started so <a href="http://www.playdation.com/t/beta_invite">Click, Connect, Create Some Play</a>!

<br><br> 
Cheers,<br>
<i>-The Playdation Team</i>

"""


def create_message_pref_defaults(app, created_models, verbosity, **kwargs ):
    notify.create_message_pref_default('playdate_invite', True)
    notify.create_message_pref_default('playdate_attendee_related', True)
    notify.create_message_pref_default('playdate_host_related', True)
    notify.create_message_pref_default('playdate_suggested', True)
    notify.create_message_pref_default('friend_related', True)
    notify.create_message_pref_default('possible_friend', True)
    notify.create_message_pref_default('pending_friend_reminder', True)
    notify.create_message_pref_default('pending_playdate_reminder', True)
    notify.create_message_pref_default('playdate_24hour', True)
    notify.create_message_pref_default('facebook', True)
    notify.create_message_pref_default('playdation', True)
    notify.create_message_pref_default('update_calendar_reminder', True)
    notify.create_message_pref_default('user_messages', True)
    notify.create_message_pref_default('special_offers', True)



    

# terminology
# actor - the person who is doing the action - joined, invited, rsvped, cancelled, commented, added to playlist, liked, tagged, posted, added, modified,
# actee - the person who is being done the action on - the recipient of the playdate invite, the recipient of the playlist request, the child being tagged, .
# object - photo, link, playdate, 

def create_notify_types(app, created_models, verbosity, **kwargs):
    notify.create_message_content('facebook','user_joined', '')        

    notify.create_message_content('update','user_joined', 'Welcome to Playdation! This is your first update. As you make plans with other parents, important updates will appear here.')        

    notify.create_message_content('update','contact_joined','{{ actor.first_name }} has joined Playdation!')

    notify.create_message_content('update','status_update_other','{{ actor.first_name }}: {{ status }} with {{ actor_child.first_name}}.')
    notify.create_message_content('update','status_update_self','{{ actor.first_name }}: {{status}} with {{ actor_children }}.')
    notify.create_message_content('update','status_update','{{ actor.first_name }}: {{status}} with {{ actor_children }}.')
    
    notify.create_message_content('message','playlist_request_received', 
                                  '{{ actee_child.first_name }} has received a friend request from {{ actor_child.first_name }}.')        
       
    notify.create_message_content('message','playlist_request_received',
                                  '{{actee_child.first_name}} has received a friend request!', 'subject')
    
    notify.create_message_content('email','playlist_request_received',
                                  '{{ actee_child.first_name }} has received a friend request from {{ actor_child.first_name }} on Playdation. <a href="http://'+settings.WWW_HOST+'{% url messages_inbox %}">[View Details Here]</a>')  

    notify.create_message_content('email','playlist_request_received',
                                  '{{actee_child.first_name}} has received a friend request on Playdation!', 'subject')

    notify.create_message_content('message','playlist_request_confirmed',
                                  '{{ actee_child.first_name }} and {{ actor_child.first_name }} are now connected!', 'subject')
    notify.create_message_content('message','playlist_request_confirmed',
                                  '{{ actor_child.first_name }} has accepted {{ actee_child.first_name }}\'s friend request. {{ actee_child.first_name }} and {{ actor_child.first_name }} are now connected on Playdation.')

    notify.create_message_content('email','playlist_request_confirmed',
                                  '{{ actee_child.first_name }} and {{ actor_child.first_name }} are now connected!', 'subject')

    notify.create_message_content('email','playlist_request_confirmed',
                                  '{{ actor_child.first_name }} has accepted {{ actee_child.first_name }}\'s friend request. {{ actee_child.first_name }} and {{ actor_child.first_name }} are now connected on Playdation.')
    
    notify.create_message_content('update','friend_new_friend','{{ actor.first_name }} {{ actor.last_name }} has added {{ actee_child.first_name }} to {{ actor_child.first_name }}\'s playlist ')

    notify.create_message_content('message', 'playdate_request_received', 
                                  '{{ actor.first_name }}\ child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="{% url view_playdate playdate.id %}">here</a> for details')
    notify.create_message_content('message', 'playdate_request_received', 
                                  '{{ actor_child.first_name }} has invited your child to a playdate.', 'subject')
    notify.create_message_content('email', 'playdate_request_received', 
                                  '{{ actor.first_name }} child {{ actor_child.first_name }} has invited your child {{ actee_child.first_name }} to a playdate. Click <a href="{% if email %}{% url view_playdate_with_token playdate.id token %}{% else %}{% url view_playdate playdate.id %}{% endif %}">here</a> for details')
    notify.create_message_content('email', 'playdate_request_received', 
                                  '{{ actor_child.first_name }} has invited your child to a playdate.', 'subject')
    notify.create_message_content('facebook', 'playdate_request_received', 
                                  '')

    notify.create_message_content('message', 'playdate_canceled', "{{ organizer.name }} has canceled the playdate you were planning on attending. <a href='{{active_invite.playdate_url}}'>[View Playdate Details]</a>")
    notify.create_message_content('message', 'playdate_canceled', "{{ organizer.name }} has canceled the playdate you were planning on attending.", 'subject')
    notify.create_message_content('email', 'playdate_canceled', "{{ organizer.name }} has canceled the playdate you were planning on attending. <a href='{{active_invite.playdate_url}}'>[View Playdate Details]</a>")
    notify.create_message_content('email', 'playdate_canceled', "{{ organizer.name }} has canceled the playdate you were planning on attending.", 'subject')

    notify.create_message_content('message', 'playdate_attendance_confirmed', "{% if email %}{{email}}{% else %}{{ actor.first_name }}'s child {{ actor_child.first_name }}{% endif %} has accepted your invitation on Playdation. <a href='{{playdate.direct_url}}'>[View Details]</a> ")
    notify.create_message_content('message', 'playdate_attendance_confirmed', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }} {%endif%}  has accepted your invite', 'subject')
    notify.create_message_content('email', 'playdate_attendance_confirmed', "{% if email %}{{email}}{% else %}{{ actor.first_name }}'s child {{ actor_child.first_name }}{%endif%} has accepted your invitation on Playdation. <a href='{{playdate.direct_url}}'>[View Details]</a> ")
    notify.create_message_content('email', 'playdate_attendance_confirmed', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }}{%endif%} has accepted your invite', 'subject')

    notify.create_message_content('message', 'playdate_attendance_maybe', "{% if email %}{{email}}{% else %}{{ actor.first_name }}'s child {{ actor_child.first_name }}{%endif%} is unsure whether he/she is able to attend {{ actee_child.first_name }}'s activity. <a href='{{playdate.direct_url}}'>[View Details]</a>")
    notify.create_message_content('message', 'playdate_attendance_maybe', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }}{%endif%} has responded maybe to your invite', 'subject')
    notify.create_message_content('email', 'playdate_attendance_maybe', "{% if email %}{{email}}{% else %}{{ actor.first_name }}'s child {{ actor_child.first_name }}{%endif%} is unsure whether he/she is able to attend {{ actee_child.first_name }}'s activity. <a href='{{playdate.direct_url}}'>[View Details]</a>")
    notify.create_message_content('email', 'playdate_attendance_maybe', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }}{%endif%} has responded maybe to your invite.', 'subject')

    notify.create_message_content('message', 'playdate_attendance_declined', "{% if email %}{{email}}{% else %}{{ actor.first_name }}'s child {{ actor_child.first_name }}{%endif%} is unable to attend {{ actee_child.first_name }}'s activity. <a href='{{playdate.direct_url}}'>[View Details]</a>")
    notify.create_message_content('message', 'playdate_attendance_declined', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }}{%endif%} has declined your invite', 'subject')
    notify.create_message_content('email', 'playdate_attendance_declined', "{% if email %}{{email}}{% else %}{{ actor.first_name }}'s child {{ actor_child.first_name }}{%endif%} is unable to attend {{ actee_child.first_name }}'s activity. <a href='{{playdate.direct_url}}'>[View Details]</a>")
    notify.create_message_content('email', 'playdate_attendance_declined', '{% if email %}{{email}}{% else %}{{ actor_child.first_name }}{%endif%} has declined your invite.', 'subject')

    notify.create_message_content('message', 'notify_attendees_accept', 'Activity Update!', 'subject')
    notify.create_message_content('message', 'notify_attendees_accept', """
    {{ invite.to }} has accepted {{organizer.get_profile.name}}\'s activity invite on behalf of {{ invite.possessive }} child. <a href="{{active_invite.playdate_url}}">[View Details]</a>
    """
    )
    
    notify.create_message_content('email', 'notify_attendees_accept', 'Activity Update!', 'subject')
    notify.create_message_content('email', 'notify_attendees_accept', """
    {{ invite.to }} has accepted {{organizer.get_profile.name}}\'s activity invite on behalf of {{invite.possessive}} child. <a href="{{active_invite.playdate_url}}">[View Details]</a>
    """
    )

    notify.create_message_content('email', 'join_invitation', join_invitation_content)
    notify.create_message_content('email', 'join_invitation', '{{ actor.first_name }} has invited you to Playdation!', 'subject')

    notify.create_message_content('email', 'welcome_email', welcome_email_content)
    notify.create_message_content('email', 'welcome_email', 'Welcome to Playdation!', 'subject')


    notify.create_message_content('email', 'email_confirmation', email_confirmation_content)
    notify.create_message_content('email', 'email_confirmation', 'Confirm e-mail address for Playdation.', 'subject')

    notify.create_message_content('email', 'beta_invite', beta_invite_content)
    notify.create_message_content('email', 'beta_invite', "Your Child's Social Life", 'subject')

    notify.create_message_content('email', 'beta_2_invite', beta_2_invite_content)
    notify.create_message_content('email', 'beta_2_invite', "Plan Your Child's Social Life!", 'subject')

    notify.create_message_content('email', 'message_received', 'Message Received on Playdation', 'subject')
    notify.create_message_content('email', 'message_received', 'You have just received a message from a friend on Playdation. Click <a href="http://'+settings.WWW_HOST+'{% url messages_inbox %}">here</a> to view the message.')
    

    notify.create_message_content('email','header', email_header)
    notify.create_message_content('email','footer', email_footer)
    notify.create_message_content('email','basic_footer', basic_footer)

    

signals.post_syncdb.connect(create_notify_types, sender=notify)
signals.post_syncdb.connect(create_message_pref_defaults, sender=notify)


