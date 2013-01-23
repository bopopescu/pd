from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib.auth.models import User
from profiles.models import Profile, Child

from itertools import *
from mydebug import *
from dateutil import rrule

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.defaultfilters import date
from schedule.utils import OccurrenceReplacer
from cachebot.managers import CacheBotManager
import time

RRULE_WEEKDAYS = {"MO":0,"TU":1,"WE":2,"TH":3,"FR":4,"SA":5,"SU":6}

freqs = ( ("YEARLY", _("Yearly")),
            ("MONTHLY", _("Monthly")),
            ("WEEKLY", _("Weekly")),
            ("DAILY", _("Daily")),
            ("HOURLY", _("Hourly")),
            ("MINUTELY", _("Minutely")),
            ("SECONDLY", _("Secondly")))


class Rule(models.Model):
    """
    This defines a rule by which an event will recur. This is defined by the
    rrule in the dateutil documentation.

    * name - the human friendly name of this kind of recursion.
    * description - a short description describing this type of recursion.
    * frequency - the base recurrence period
    * param - extra params required to define this type of recursion. The params
      should follow this format:

        param = [rruleparam:value;]*
        rruleparam = see list below
        value = int[,int]*

      The options are: (documentation for these can be found at
      http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57)
        ** count
        ** bysetpos
        ** bymonth
        ** bymonthday
        ** byyearday
        ** byweekno
        ** byweekday
        ** byhour
        ** byminute
        ** bysecond
        ** byeaster
    """
    name = models.CharField(_("name"), max_length=32)
    description = models.TextField(_("description"))
    frequency = models.CharField(_("frequency"), choices=freqs, max_length=10)
    params = models.TextField(_("params"), null=True, blank=True)

    class Meta:
        verbose_name = _('rule')
        verbose_name_plural = _('rules')
        app_label = 'schedule'

    def parse_param(self, param_value):
        param = param_value.split('(',1)[0]
        if param in RRULE_WEEKDAYS:
            try:
                return eval("rrule.%s" % param_value)
            except ValueError:
                raise ValueError('rrule parameter improperly formatted. Error on: %s' % param_value)
        try:
            return int(param_value)
        except ValueError:
            raise ValueError('rrule parameter should be integer or weekday constant (e.g. MO, TU, etc.). Error on: %s' % param_value)

    def get_params(self):
        """
        >>> rule = Rule(params = "count:1;bysecond:1;byminute:1,2,4,5")
        >>> rule.get_params()
        {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}
        """
        if self.params is None:
            return {}
        params = self.params.split(';')
        param_dict = []
        for param in params:
            if param.strip() == "":
                continue # skip blanks
            param = param.split(':')
            if len(param) == 2:
                param = (str(param[0]).strip(), [self.parse_param(p.strip()) for p in param[1].split(',')])
                if len(param[1]) == 1:
                    param = (param[0], param[1][0])
                param_dict.append(param)
        return dict(param_dict)

    def __unicode__(self):
        """Human readable string for Rule"""
        return self.name

   


class Event(models.Model):                                                                                                             
    start = models.DateTimeField(_("start"), db_index=True)
    end = models.DateTimeField(_("end"),help_text=_("The end time must be later than the start time."), db_index=True)
    public = models.BooleanField(_("public"), default=False)
    rule = models.ForeignKey(Rule, null = True, blank = True, verbose_name=_("rule"), help_text=_("Select '----' for a one time only event."))
    end_recurring_period = models.DateTimeField(_("end recurring period"), null = True, blank = True, help_text=_("This date is ignored for one time only events."))

    content_type = models.ForeignKey(ContentType)                                                                                      
    object_id = models.IntegerField()                                                                                                  
    activity = generic.GenericForeignKey('content_type', 'object_id')                                                                  
    objects = CacheBotManager()

                                                                                                                                       
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        app_label = 'schedule'
        get_latest_by = 'start' 

    def __unicode__(self):
        date_format = u'l, %s' % ugettext("DATE_FORMAT")
        return ugettext('event %(start)s-%(end)s') % {
            'start': date(self.start, date_format),
            'end': date(self.end, date_format),
        }

    def etype(self):
        return self.content_type.name

    etype = property(etype);

    def get_occurrences(self, start, end):
        """
        >>> rule = Rule(frequency = "MONTHLY", name = "Monthly")
        >>> rule.save()
        >>> event = Event(rule=rule, start=datetime.datetime(2008,1,1), end=datetime.datetime(2008,1,2))
        >>> event.rule
        <Rule: Monthly>
        >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
        >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
        ['2008-02-01 00:00:00 to 2008-02-02 00:00:00', '2008-03-01 00:00:00 to 2008-03-02 00:00:00']

        Ensure that if an event has no rule, that it appears only once.

        >>> event = Event(start=datetime.datetime(2008,1,1,8,0), end=datetime.datetime(2008,1,1,9,0))
        >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
        >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
        []

        """
        persisted_occurrences = self.occurrence_set.all()
        occ_replacer = OccurrenceReplacer(persisted_occurrences)
        occurrences = self._get_occurrence_list(start, end)
        final_occurrences = []
        for occ in occurrences:
            # replace occurrences with their persisted counterparts
            if occ_replacer.has_occurrence(occ):
                p_occ = occ_replacer.get_occurrence(
                        occ)
                # ...but only if they are within this period
                if p_occ.start < end and p_occ.end >= start:
                    final_occurrences.append(p_occ)
            else:
              final_occurrences.append(occ)
        # then add persisted occurrences which originated outside of this period but now
        # fall within it
        final_occurrences += occ_replacer.get_additional_occurrences(start, end)
        return final_occurrences


    def _get_occurrence_list(self, start, end):
        """
        returns a list of occurrences for this event from start to end.
        """
        difference = (self.end - self.start)
        if self.rule is not None:
            occurrences = []
            if self.end_recurring_period and self.end_recurring_period < end:
                end = self.end_recurring_period
            rule = self.get_rrule_object()
            o_starts = rule.between(start-difference, end, inc=False)
            for o_start in o_starts:
                o_end = o_start + difference
                occurrences.append(self._create_occurrence(o_start, o_end))
            return occurrences
        else:
            # check if event is in the period
            if self.start < end and self.end >= start:
                return [self._create_occurrence(self.start)]
            else:
                return []


    def _create_occurrence(self, start, end=None):
        if end is None:
            end = start + (self.end - self.start)
        return Occurrence(event=self,start=start,end=end, original_start=start, original_end=end)



class Occurrence(models.Model):
    event = models.ForeignKey(Event, verbose_name=_("event"))
    start = models.DateTimeField(_("start"))
    end = models.DateTimeField(_("end"))
    cancelled = models.BooleanField(_("cancelled"), default=False)
    original_start = models.DateTimeField(_("original start"))
    original_end = models.DateTimeField(_("original end"))

    objects = CacheBotManager()

    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")
        app_label = 'schedule'

    def moved(self):
        return self.original_start != self.start or self.original_end != self.end
    moved = property(moved)


EVENT_STATUS = (
    ("1", "Busy"),
    ("2", "Available"),   
    ("3", "Plan"),
)    

    
class EventPlan(models.Model):                                                                                                         
    child = models.ForeignKey(Child, related_name='events', db_index=True)
    event = models.ForeignKey(Event, related_name='children', db_index=True)
    status = models.CharField(max_length=1, choices=EVENT_STATUS, default='1')
    _event = None
    
    class Meta:
        app_label='schedule'


    objects = CacheBotManager()

    def busy(self):
        if self.status == '1':
            return True
        return False

    busy = property(busy)

    def avail(self):
        if self.status == '2':
            return True
        return False

    avail = property(avail)

    def plan(self):
        if self.status == '3':
            return True
        return False
    plan = property(plan)

    def get_event(self):
        if self._event is None:
            self._event = self.event
        
        return self._event

    get_event = property(get_event)

    def start(self):        
        return self.get_event.start
    
    start = property(start)

    def start_epoch(self):
        return int(time.mktime(self.get_event.start.timetuple())) 
    
    start_epoch = property(start_epoch)
    
    def end(self):
        return self.get_event.end
    
    end = property(end)

    def end_epoch(self):
        return int(time.mktime(self.get_event.end.timetuple())) 
    
    end_epoch = property(end_epoch)

    def remove_availability_for_this_timeslot(self):
        event = self.get_event
        event_start = event.start
        event_end = event.end
        day_start = event_start.replace(hour=0,minute=1,second=0)
        day_end = event_end.replace(hour=23,minute=59,second=0)
 
#        todebug("removing availiability for: " + str(self.id));
        event_list = list(self.child.events.select_related('event').filter(event__start__gte = day_start, event__end__lte = day_end, event__end__gt = event_start, event__start__lt=event_end))

        ep = self
        for epl in event_list:
            if epl != ep:
                if epl.avail:
                    if ep.start <= epl.start and ep.end >= epl.end:
#                        todebug("availability fully contained within event. will delete")
                        epl.delete()
                    elif ep.start > epl.start and ep.end < epl.end:
#                        todebug("event fully contained within availability. will split availability")
                        new_event = create_event(ep.end, epl.end, epl.event.activity)
                        new_ep = create_eventplan(epl.child, new_event, '2')
        
                        epl.event.end = ep.start
                        epl.event.save()
        
                    elif ep.start > epl.start and ep.end >= epl.end:
#                        todebug("event starts within availability and ends at the end or after end of availability. will cut end time of availability")
                        epl.event.end = ep.start
                        epl.event.save()
                    elif ep.start <= epl.start and ep.end < epl.end:
#                        todebug("event starts before or at start of availability and ends during availabiliyt. will cut start time of availability")
                        epl.event.start = ep.end
                        epl.event.save()
                    else:
                        pass
#                        print "unrelated blah"


  
class Activity(models.Model):                                                                                                          
    event = generic.GenericRelation(Event)                                                                                             
    type = 'abstract'
    direct_url = None

    class Meta:
        abstract = True
        app_label='schedule'
        
        
class CustomActivity(Activity):
    description = models.CharField(max_length=100)
    type = 'custom'
    deleteable = True

    def save_from_opts(self, opts):
        self.description = opts["description"]        

    class Meta:
        app_label='schedule'
    
    def summary(self):
        return self.description

    def summary_body(self):
        return ""
    

activity_map = { 'custom': CustomActivity }

def create_activity(opts):
    ca = activity_map[opts["activity"]]()
    ca.save_from_opts(opts)
    ca.save()
    return ca

def create_event(start, end, activity):
    ev = Event(start=start, end=end, activity=activity)
    ev.save()
    return ev

def create_eventplan(child, event, status):
    es = EventPlan(child=child, event=event, status=status)
    es.save()
    return es
