from django.db import models
from profiles.models import Child, FacebookUser, Profile
from playdates.models import Playdate
from friends.models import JoinInvitationEmail, ContactFB
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Count

klasses = {
    'User': User,
    'Profile': Profile,
    'Child': Child,
    'FacebookUser':FacebookUser,
    'JoinInvitationEmail':JoinInvitationEmail,
    'Playdate':Playdate,
    'ContactFB':ContactFB,
}

def get_klass(klass):
    return klasses[klass]

def do_count(klass, when, group):
    end = when
    start = when - timedelta(minutes=60)
    if group is None:
        return  [ { 'count': get_klass(klass).objects.filter(create_date__gte=start, create_date__lte = end).count() }]
    else:
        return list(get_klass(klass).objects.filter(create_date__gte=start, create_date__lte = end).values(group).annotate(count=Count(group)))

class PDReport(models.Model):
    name = models.CharField(max_length=50)
    about = models.TextField(null=True, blank=True)
    klass = models.CharField(max_length=50)
    group = models.CharField(max_length=50, null=True, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)

    def run_count(self, when):
        return do_count(self.klass, when, self.group)

    def get_metrics(self, when):
        start = when.replace(hour=0,minute=1)
        end = start + timedelta(hours=24)
        metrics = self.metrics.filter(when__gte=start , when__lte = end)
        return_list = []
        running_count = None
        for metric in metrics:
            return_list.append({'when':metric.when, 'count': metric.count, 'group':metric.group })

        return return_list


class PDMetric(models.Model):
    report = models.ForeignKey(PDReport, related_name='metrics', db_index=True)
    when = models.DateTimeField()
    count = models.IntegerField()
    group = models.CharField(max_length=50, null=True, blank=True)
    
def run_all_counts(when=datetime.now()):
    reports = PDReport.objects.all()
    for report in reports:
        for count in report.run_count(when):
            group = None
            if report.group is not None:
                group = count[report.group]
            
            args = { 'report':report, 'when':when, 'count':count["count"], 'group':group }
            
            PDMetric(**args).save()
            report.last_run = datetime.now()
            report.save()

def create_report_type(name, klass, group=None, about=None):
    try:
        pdr = PDReport.objects.get(name=name)
        pdr.klass=klass
        pdr.group=group
        pdr.about=about
        pdr.save()
    except PDReport.DoesNotExist:
        PDReport(name=name, klass=klass, group=group, about=about).save() 

