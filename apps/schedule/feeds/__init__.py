# from schedule.models import Calendar
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from schedule.feeds.atom import Feed
from schedule.feeds.icalendar import ICalendarFeed
from django.http import HttpResponse
import datetime, itertools

