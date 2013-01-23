from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.validators import email_re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse

from metrics.models import *
import re
from datetime import datetime

@login_required
def main(request, template_name='metrics/main.html'):

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("acct_login"))

    report = None
    report_date = datetime.now()
    report_id = None
    if request.method == 'POST':
        post = request.POST
        report_id = post["report_id"]

        if "day" in post:
            day = post["day"]
            month = post["month"]
            year = post["year"]
            report_date=datetime(int(year), int(month), int(day))

    reports = PDReport.objects.all()
    
    if report_id is None:
        report = reports[0]
    else:
        report = PDReport.objects.get(id=report_id)

    metrics = report.get_metrics(when=report_date)
    count_all = 0
    for metric in metrics:
        count_all = count_all + metric["count"]


    ctx = {
        'metrics':metrics,
        'reports':reports,
        'report':report,
        'report_date':report_date,
        'count_all':count_all,
    }
    if not request.user.is_superuser:
        raise Exception('No Dice')
    
    return render_to_response(template_name,
        context_instance = RequestContext(request, ctx)
    )
