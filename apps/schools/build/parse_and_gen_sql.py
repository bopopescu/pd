from django.core.management import setup_environ
import sys

sys.path.append('/var/www/playdation.net')
sys.path.append('/var/www/playdation.net/playdation')
sys.path.append('/var/www/playdation.net/playdation/apps')

from playdation import settings

setup_environ(settings)

from schools.models import School

import xml.sax.handler
from copy import copy
 
class SchoolHandler(xml.sax.handler.ContentHandler):
  def __init__(self, callback):
    self.max = 9993997
    self.count = 0
    self.capture = 0
    self.curele = ''
    self.inSchool = 0
    self.mapping = {}
    self.buffer = ''
    self.callback = callback
    self.desired_tmpl = {
        'universal-id': '',
        'name': '',
        'city': '',
        'zip': '',
        'state':'',
        'lat': '',
        'lon': '',
        'subtype':'',
        'type':'',
    }
    self.ds = {}
 
  def startElement(self, name, attributes):
    if name == "school":
      self.inSchool = 1
      self.ds = copy(self.desired_tmpl)

    if self.inSchool:
      if name in self.ds:
        if not len(self.ds[name]):
          self.capture = 1
          self.curele = name
 
  def characters(self, data):
    if self.capture:
      self.buffer += data
 
  def endElement(self, name):
    if self.capture:
#        if self.curele == 'name':
#            print self.buffer
        self.ds[self.curele] = self.buffer
        self.buffer = ""
        self.capture = 0
    
    if name == "school":
      self.count = self.count + 1
      self.inSchool = 0
      if self.count < self.max:
        self.callback(self.count,self.ds)


def cb(count,ds):
  school = School()

  school.name = ds["name"]
  school.gsid = ds["universal-id"]
  school.city = ds["city"]
  if len(ds["zip"]) > 6:
    ds["zip"] = ds["zip"][:6]
  school.zip = ds["zip"]
  school.state = ds["state"]
  school.lat = ds["lat"]
  school.lon = ds["lon"]

  if len(ds["subtype"]) > 50:
    ds["subtype"] = 'special'
  school.type = ds["subtype"]

  sql =   'insert into schools_school values ("'+ds["universal-id"]+'","'+ ds["name"] + '","' + ds["subtype"] + '","' + ds["city"] + '","' + ds["state"] + '","' + ds["zip"] + '","' + ds["lat"] + '","' + ds["lon"] + '",0);'

  print sql
  

import xml.sax
import pprint
import sys

parser = xml.sax.make_parser(  )
handler = SchoolHandler(cb)
parser.setContentHandler(handler)
#parser.parse("schools.xml")
parser.parse(sys.argv[1]) #"local-greatschools-feed-WY.xml")
# pprint.pprint(handler.mapping)
