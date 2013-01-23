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

def url_handler(name,attributes):
    type = attributes.get("type")
    if type == "School Overview":
        return True
    return False
 
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
        'street':'',
        'level':'',
        'phone':'',
        'district-name':'',
        'url':'',
    }

    self.special_handler = {
        'url':url_handler,
    }
    
    self.ds = {}
 
  def startElement(self, name, attributes):
    if name == "school":
      self.inSchool = 1
      self.ds = copy(self.desired_tmpl)

    if self.inSchool:
      if name in self.ds:
        if name in self.special_handler:
            if not self.special_handler[name](name,attributes):
                return None
            
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
  school = None
  try:
    school = School.objects.get(gsid=ds["universal-id"])
  except:
    school = School()

#  print "called for num:" + str(count) + "val: " + str(ds)

  school.name = ds["name"]
  school.gsid = ds["universal-id"]
  school.city = ds["city"]
  if len(ds["zip"]) > 6:
    ds["zip"] = ds["zip"][:6]
  school.zip = ds["zip"]
  school.state = ds["state"]
  school.lat = ds["lat"]
  school.lon = ds["lon"]
  school.gsurl = ds["url"]

  if len(ds["street"]) > 50:
    ds["street"] = ds["street"][:49]
  
  school.street = ds["street"]

  if len(ds["level"]) > 20:
    ds["level"] = ds["level"][:19]
  
  school.level = ds["level"]


  if len(ds["phone"]) > 20:
    ds["phone"] = ds["phone"][:19]
  
  school.phone = ds["phone"]


  if len(ds["subtype"]) > 50:
    ds["subtype"] = 'special'
  school.type = ds["subtype"]


  if len(ds["district-name"]) > 50:
    ds["district-name"] = ds["district-name"][:49]
  
  school.district_name = ds["district-name"]

#  try:
  print school.gsurl
  school.save()
#  except:
#    raise Exception('FAIL!!! FAIL!!!' + str(ds))

#  print school.gsid
#  print ",".join([ school.gsid, school.lat, school.lon ])
  

import xml.sax
import pprint
import sys

parser = xml.sax.make_parser(  )
handler = SchoolHandler(cb)
parser.setContentHandler(handler)
#parser.parse("schools.xml")
parser.parse(sys.argv[1]) #"local-greatschools-feed-WY.xml")
# pprint.pprint(handler.mapping)
