from django.db.models import get_models, signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _

from metrics import models as metrics


def create_report_types(app, created_models, verbosity, **kwargs ):
    metrics.create_report_type('New Users', 'Profile', group='source')
    metrics.create_report_type('New Children', 'Child')
    metrics.create_report_type('New Facebook Connects', 'FacebookUser')
    metrics.create_report_type('New Playdates Created', 'Playdate')
    metrics.create_report_type('Email Invitations to Playdation Sent', 'JoinInvitationEmail')
    metrics.create_report_type('FB Contacts Invited', 'ContactFB',)



signals.post_syncdb.connect(create_report_types, sender=metrics)
