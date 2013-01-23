from django import forms
from django.conf import settings
from django.forms.extras.widgets import SelectDateWidget

from django.forms.formsets import formset_factory

from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
import re
RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

alnum_re = re.compile(r"^\w+$")



class CustomSelectDateWidget(Widget):
    """
    A Widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """
    none_value_month = (0, 'Month')
    none_value_day = (0, 'Day')
    none_value_year = (0, 'Year')
    
    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'
    attrs_day = None
    attrs_month = None
    attrs_year = None

    def __init__(self, attrs=None, years=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        if "class_year" in self.attrs:
            self.attrs_year = self.attrs["class_year"]
            del self.attrs["class_year"]

        if "class_month" in self.attrs:
            self.attrs_month = self.attrs["class_month"]
            del self.attrs["class_month"]

        if "class_day" in self.attrs:
            self.attrs_day = self.attrs["class_day"]
            del self.attrs["class_day"]
        
        
        self.required = required
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year+10)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            year_val = month_val = day_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = MONTHS.items()
        if not (self.required and value):
            month_choices.append(self.none_value_month)
        month_choices.sort()       
        local_attrs = self.build_attrs(id=self.month_field % id_)
        s = Select(choices=month_choices)

        
        
        if self.attrs_month is not None:
            local_attrs.update( {'class':self.attrs_month })

        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        day_choices = [(i, i) for i in range(1, 32)]
        if not (self.required and value):
            day_choices.insert(0, self.none_value_day)
        local_attrs['id'] = self.day_field % id_
        if self.attrs_day is not None:
            local_attrs.update({'class': self.attrs_day })
        
        s = Select(choices=day_choices)
        select_html = s.render(self.day_field % name, day_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        if not (self.required and value):
            year_choices.insert(0, self.none_value_year)
        local_attrs['id'] = self.year_field % id_

        if self.attrs_year is not None:
            local_attrs.update({ 'class': self.attrs_year })       
        
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        if y == m == d == "0":
            return None
        if y and m and d:
            return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)



