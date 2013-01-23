from django.conf import settings

from account.models import Account, AnonymousAccount
from django.contrib import messages

def account(request):
    if request.user.is_authenticated():
        try:
            account = Account._default_manager.get(user=request.user)
        except Account.DoesNotExist:
            account = AnonymousAccount(request)
    else:
        account = AnonymousAccount(request)
    return {
        "account": account,
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "support@example.com")
    }

def analytics_tracking(request):
    response = """
<script type="text/javascript">
  var _kmq = _kmq || [];
  function _kms(u){
    setTimeout(function(){
      var s = document.createElement('script'); var f = document.getElementsByTagName('script')[0]; s.type = 'text/javascript'; s.async = true;
      s.src = u; f.parentNode.insertBefore(s, f);
    }, 1);
  }
  _kms('//i.kissmetrics.com/i.js');_kms('""" + settings.KISS_ID + """');
</script>
<script type='text/javascript' src='/static/js/playdation.js'></script>
    """

    if request.user.is_authenticated():
        event = request.session.pop('event', None)

        if event is not None:
            response = response + """
<script>
try { 
  Track.record('""" + event + """'); 
} catch (e) { }
</script>
"""
        

    return { 'analytics_tracking': response }

def user_message_top(request):
    response = '<!-- nothing happend -->'

    message_text = None
    for message in messages.get_messages(request):
        if message_text is None:
            message_text = message

    if message_text is not None:
        response = """
<script type='text/javascript' src='/static/js/playdation.js'></script>
<script>
    Message.display('""" + str(message_text) + """'); 
</script>
        """
        
    return { 'user_message_top': response }
