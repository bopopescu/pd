from django.db.models import get_models, signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _

from playdates import models as playdates
from playdates import invites as invites

# terminology
# actor - the person who is doing the action - joined, invited, rsvped, cancelled, commented, added to playlist, liked, tagged, posted, added, modified,
# actee - the person who is being done the action on - the recipient of the playdate invite, the recipient of the playlist request, the child being tagged, .
# object - photo, link, playdate, 


content_male = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Male_Email</title>
</head>

<body>
<table width="100%" border="0" cellspacing="0" cellpadding="0" style="background:#fff; color:#7b7b7b;">
  <tr>
    <td align="center"><table width="476" border="0" align="center" cellpadding="0" cellspacing="0">
        <tr>
          <td height="12"></td>
        </tr>
        <tr>
          <td style="text-align:center;"><a href="#"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_logo.png" width="229" height="51" alt="" style="border:0; vertical-align:top; margin:0; padding:0;" /></a></td>
        </tr>
        <tr>
          <td height="13"></td>
        </tr>
        <tr>
          <td style="font-size:16px; line-height:20px; font-family:Arial, Helvetica, sans-serif; text-align:center;"><strong style="color:#043351;">{{ actor.first_name }} {{ actor.last_name }} </strong> sent you a playdate invitation on behalf of {{ actor_child.first_name }}. <br />
            Click <a href="{{playdate_url}}" style="color:#fb8d3a; text-decoration:none;">here</a> to view your invitation! </td>
        </tr>
        <tr>
          <td height="20"></td>
        </tr>
        <tr>
          <td><table width="476" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td colspan="3"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_top.png" width="476" height="104" alt="" style="vertical-align:top; margin:0; padding:0; border:0;" /></td>
              </tr>
              <tr>
                <td width="39"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_left.png" width="39" height="90" alt="" style="vertical-align:top; margin:0; padding:0; border:0;" /></td>
                <td width="217" style="background:#d7c9a2;"><table width="398" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                      <td style="color:#8b7c53; font-family:Georgia, 'Times New Roman', Times, serif; font-size:15px;
    font-style:italic; text-align:center;">{% if email %}{%else%}for you{%endif%}</td>
                    </tr>
                    <tr>
                      <td style="color:#8b7c53; font-family:Georgia, 'Times New Roman', Times, serif; font-style:italic; text-align:center; font-size:60px;">{% if email %}Your Child{% else %}{{ actee_child.first_name }}{% endif %}</td>
                    </tr>
                  </table></td>
                <td width="39"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_right.png" width="39" height="90" alt="" style="vertical-align:top; margin:0; padding:0; border:0;" /></td>
              </tr>
              <tr>
                <td colspan="3"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_bottom.png" width="476" height="116" alt="" style="vertical-align:top; margin:0; padding:0; border:0;"/></td>
              </tr>
            </table></td>
        </tr>
        <tr>
          <td style="height:30px;"></td>
        </tr>
        <tr>
          <td><table width="476" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td width="105"></td>
                <td width="266"><table width="266" border="0" cellspacing="0" cellpadding="0" style="color:#404040;">
                    <tr>
                      <td rowspan="4" width="76"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_email_open.png" width="73" height="64" alt="" style="vertical-align:middle; border:0; margin:0; padding:0;" /></td>
                      <td style="font-family:Tahoma, Geneva, sans-serif; width:190px; font-weight:bold; font-size:11px; height:14px; line-height:14px;">{{ actor.first_name }} is hosting a Playdate </td>
                    </tr>
                    <tr>
                      <td style="font-family:Tahoma, Geneva, sans-serif; font-size:11px; height:14px; line-height:14px;">{{ playdate.event.start }}</td>
                    </tr>
                    <tr>
                      <td style="font-family:Tahoma, Geneva, sans-serif; font-size:11px; height:14px; line-height:14px;">At {{ playdate.address }}</td>
                    </tr>
                    <tr>
                      <td style=" height:16px; line-height:16px; font-size:11px; font-family:Tahoma, Geneva, sans-serif;"><a href="{{playdate_url}}" style="color:#3f71c3; text-decoration:none;">Details</a></td>
                    </tr>
                  </table></td>
                <td width="105"></td>
              </tr>
              <tr>
                <td colspan="3" height="15"></td>
              </tr>
              <tr>
                <td colspan="3" style="color:#7b7b7b; font-size:12px; text-align:center; font-family:Arial, Helvetica, sans-serif;"></td>
              </tr>
            </table></td>
        </tr>
        <tr>
          <td height="20"></td>
        </tr>
      </table></td>
  </tr>
</table>
</body>
</html>
"""


content_female = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Male_Email</title>
</head>

<body>
<table width="100%" border="0" cellspacing="0" cellpadding="0" style="background:#fff; color:#7b7b7b;">
  <tr>
    <td align="center"><table width="476" border="0" align="center" cellpadding="0" cellspacing="0">
        <tr>
          <td height="12"></td>
        </tr>
        <tr>
          <td style="text-align:center;"><a href="#"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_logo.png" width="229" height="51" alt="" style="border:0; vertical-align:top; margin:0; padding:0;" /></a></td>
        </tr>
        <tr>
          <td height="13"></td>
        </tr>
        <tr>
          <td style="font-size:16px; line-height:20px; font-family:Arial, Helvetica, sans-serif; text-align:center;"><strong style="color:#043351;">{{ actor.first_name }} {{ actor.last_name }} </strong> sent you a playdate invitation on behalf of {{ actor_child.first_name }}. <br />
            Click <a href="{{playdate_url}}" style="color:#fb8d3a; text-decoration:none;">here</a> to view your invitation! </td>
        </tr>
        <tr>
          <td height="20"></td>
        </tr>
        <tr>
          <td><table width="476" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td colspan="3"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/female/img_top.png" width="476" height="104" alt="" style="vertical-align:top; margin:0; padding:0; border:0;" /></td>
              </tr>
              <tr>
                <td width="39"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_left.png" width="39" height="90" alt="" style="vertical-align:top; margin:0; padding:0; border:0;" /></td>
                <td width="217" style="background:#d7c9a2;"><table width="398" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                      <td style="color:#8b7c53; font-family:Georgia, 'Times New Roman', Times, serif; font-size:15px;
    font-style:italic; text-align:center;">{% if email %}{%else%}for you{%endif%}</td>
                    </tr>
                    <tr>
                      <td style="color:#8b7c53; font-family:Georgia, 'Times New Roman', Times, serif; font-style:italic; text-align:center; font-size:60px;">{% if email %}Your Child{% else %}{{ actee_child.first_name }}{% endif %}</td>
                    </tr>
                  </table></td>
                <td width="39"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_right.png" width="39" height="90" alt="" style="vertical-align:top; margin:0; padding:0; border:0;" /></td>
              </tr>
              <tr>
                <td colspan="3"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/male/img_bottom.png" width="476" height="116" alt="" style="vertical-align:top; margin:0; padding:0; border:0;"/></td>
              </tr>
            </table></td>
        </tr>
        <tr>
          <td style="height:30px;"></td>
        </tr>
        <tr>
          <td><table width="476" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td width="105"></td>
                <td width="266"><table width="266" border="0" cellspacing="0" cellpadding="0" style="color:#404040;">
                    <tr>
                      <td rowspan="4" width="76"><img src="http://"""+settings.WWW_HOST+"""/static/images/email/female/img_email_close.png" width="73" height="64" alt="" style="vertical-align:middle; border:0; margin:0; padding:0;" /></td>
                      <td style="font-family:Tahoma, Geneva, sans-serif; width:190px; font-weight:bold; font-size:11px; height:14px; line-height:14px;">{{ actor.first_name }} is hosting a Playdate </td>
                    </tr>
                    <tr>
                      <td style="font-family:Tahoma, Geneva, sans-serif; font-size:11px; height:14px; line-height:14px;">{{ playdate.event.start }}</td>
                    </tr>
                    <tr>
                      <td style="font-family:Tahoma, Geneva, sans-serif; font-size:11px; height:14px; line-height:14px;">At {{ playdate.address }}</td>
                    </tr>
                    <tr>
                      <td style=" height:16px; line-height:16px; font-size:11px; font-family:Tahoma, Geneva, sans-serif;"><a href="{{ playdate_url }}" style="color:#3f71c3; text-decoration:none;">Details</a></td>
                    </tr>
                  </table></td>
                <td width="105"></td>
              </tr>
              <tr>
                <td colspan="3" height="15"></td>
              </tr>
              <tr>
                <td colspan="3" style="color:#7b7b7b; font-size:12px; text-align:center; font-family:Arial, Helvetica, sans-serif;"></td>
              </tr>
            </table></td>
        </tr>
        <tr>
          <td height="20"></td>
        </tr>
      </table></td>
  </tr>
</table>
</body>
</html>
"""

content_kids = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Index</title>
</head>

<body style="margin:0; padding:0; border:0; background:#fff;">
<table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin:0; padding:0; border:0; background:#fff;">
    <tr>
        <td align="center" valign="top"><table width="600" border="0" cellspacing="0" cellpadding="0">
                <tr>
                    <td><table width="600" border="0" cellspacing="0" cellpadding="0">
                            <tr>
                                <td height="36"></td>
                            </tr>
                            <tr>
                                <td style=" text-align:center; font-size:14px; color:#7b7b7b; line-height:18px; font-family:Arial, Helvetica, sans-serif;"><font style=" color:#043351; font-weight:bold;">Christine  Desantis</font> sent you a Playdate invitation.<br />
                                    Click the <a href="#" style=" color:#fb8d3a; text-decoration:none;">envelope</a> below to view your invitation !</td>
                            </tr>
                            <tr>
                                <td height="19"></td>
                            </tr>
                        </table></td>
                </tr>
                <tr>
                    <td><table width="600" border="0" cellspacing="0" cellpadding="0">
                            <tr>
                                <td valign="bottom"><img src="http://www.netnova.info/email_playdate/images/img_top.png" width="600" height="192" alt="" style="border:0; padding:0; margin:0; vertical-align:bottom;" /></td>
                            </tr>
                            <tr>
                                <td><table width="600" border="0" cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td height="87" width="164"><img src="http://www.netnova.info/email_playdate/images/img_left.png" width="164" height="87" alt="" style="margin:0; padding:0; border:0; vertical-align:top;" /></td>
                                            <td width="285" height="87" style="background:#fdeb6b;"><table width="285" border="0" cellspacing="0" cellpadding="0">
                                                    <tr>
                                                        <td style="font-family:Georgia, 'Times New Roman', Times, serif; font-style:italic; font-size:12px; padding:0 0 0 55px; text-align:left; color:#8b7c53;">for you</td>
                                                    </tr>
                                                    <tr>
                                                        <td style=" font-family:Georgia, 'Times New Roman', Times, serif; font-size:40px; font-style:italic; text-align:left; padding:0 0 0 70px; color:#a77130;">Michelle</td>
                                                    </tr>
                                                </table></td>
                                            <td height="87" width="151"><img src="http://www.netnova.info/email_playdate/images/img_right.png" width="151" height="87" alt="" style="margin:0; padding:0; border:0; vertical-align:top;" /></td>
                                        </tr>
                                    </table></td>
                            </tr>
                            <tr>
                                <td valign="top"><img src="http://www.netnova.info/email_playdate/images/img_bottom.png" width="600" height="120" alt="" style="margin:0; padding:0; border:0; vertical-align:top;" /></td>
                            </tr>
                        </table></td>
                </tr>
                <tr>
                    <td><table width="600" border="0" cellspacing="0" cellpadding="0">
                            <tr>
                                <td height="30"></td>
                            </tr>
                            <tr>
                                <td align="center"><table width="275" border="0" cellspacing="0" cellpadding="0">
                                        <tr>
                                            <td valign="middle" align="left" width="75"><img src="http://www.netnova.info/email_playdate/images/img_email.png" width="66" height="47" alt="" style="margin:0; padding:0; border:0; vertical-align:middle;" /></td>
                                            <td width="200"><table width="200" border="0" cellspacing="0" cellpadding="0">
                                                    <tr>
                                                        <td style="font-family:Tahoma, Geneva, sans-serif; font-size:11px; font-weight:bold; color:#404040; text-align:left;">Christine is hosting a Playdate</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="font-family:Tahoma, Geneva, sans-serif; font-size:11px; color:#404040; text-align:left;">Saturday, March 19th 2011<br />
                                                            5PM At her house<br />
                                                            <a href="#" style="color:#3f71c3; text-decoration:none;">Details</a></td>
                                                    </tr>
                                                </table></td>
                                        </tr>
                                    </table></td>
                            </tr>
                            <tr>
                                <td height="20"></td>
                            </tr>
                            <tr>
                                <td style="font-family:Arial, Helvetica, sans-serif; font-size:12px; color:#7b7b7b; text-align:center;"> The pool will be open and we will have snacks and drinks.</td>
                            </tr>
                            <tr>
                                <td height="49"></td>
                            </tr>
                        </table></td>
                </tr>
                <tr>
                    <td><table width="600" border="0" cellspacing="0" cellpadding="0">
                            <tr>
                                <td><img src="http://www.netnova.info/email_playdate/images/img_line.png" width="600" height="25" alt="" style="margin:0; padding:0; border:0; vertical-align:middle;" /></td>
                            </tr>
                            <tr>
                                <td style="font-family:Arial, Helvetica, sans-serif; font-size:11px; color:#a9a9a9; text-align:left;">This message is service email related to your use of Playdation. To change your email settings, <a href="#" style="color:#3f71c3; text-decoration:none;">click here</a></td>
                            </tr>
                            <tr>
                                <td><img src="http://www.netnova.info/email_playdate/images/img_line.png" width="600" height="25"  alt="" style="margin:0; padding:0; border:0; vertical-align:middle;" /></td>
                            </tr>
                            <tr>
                                <td style="font-family:Arial, Helvetica, sans-serif; font-size:11px; color:#a9a9a9; text-align:left;"> Please add <a href="mailto:mail@playdation.com" style="color:#a9a9a9; text-decoration:none;">mail@playdation.com</a> to your address book to ensure deliverability of all future Playdation email. </td>
                            </tr>
                            <tr>
                                <td><img src="http://www.netnova.info/email_playdate/images/img_line.png" width="600" height="25" alt="" style="margin:0; padding:0; border:0; vertical-align:middle;" /></td>
                            </tr>
                            <tr>
                                <td style="font-family:Arial, Helvetica, sans-serif; font-size:11px; color:#a9a9a9; text-align:left;">Playdation, Inc. 412 Broadway, Floor 2, New York City, NY 10013</td>
                            </tr>
                        </table></td>
                </tr>
                <tr>
                    <td height="30"></td>
                </tr>
            </table></td>
    </tr>
</table>
</body>
</html>
"""






def create_playdate_invite_designs(app, created_models, verbosity, **kwargs):
    invites.create_playdate_invite_design(title="Male", subject="{% if email %}Your Child{% else %}{{ actee_child.first_name }}{% endif %} has received a playdate request!", small_image="http://www.cnn.com", big_image="http://www.cnn.com",description="Basic Male Vanilla Invite",html=content_male )
    invites.create_playdate_invite_design(title="Female", subject="{% if email %}Your Child{% else %}{{ actee_child.first_name }}{% endif %} has received a playdate request!", small_image="http://www.cnn.com", big_image="http://www.cnn.com",description="Basic Female Vanilla Invite",html=content_female )
    invites.create_playdate_invite_design(title="Toddler", subject="You are invited", small_image="http://www.cnn.com", big_image="http://www.cnn.com",description="Basic Vanilla Invite",html="Yo. Is your kid coming or not? He better. It will rock." )
  

def create_playdate_activities(app, created_models, verbosity, **kwargs):
    playdates.create_pd_activity('Indoor Play')
    playdates.create_pd_activity('Outdoor Play')
    playdates.create_pd_activity('Sports')
    playdates.create_pd_activity('Arts & Crafts')
    playdates.create_pd_activity('Board Games')
    playdates.create_pd_activity('Video Games')
    playdates.create_pd_activity('Cooking')
    playdates.create_pd_activity('Homework')
    playdates.create_pd_activity('Music')
    playdates.create_pd_activity('Other')

    
signals.post_syncdb.connect(create_playdate_invite_designs, sender=playdates)
signals.post_syncdb.connect(create_playdate_activities, sender=playdates)
