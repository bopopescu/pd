#!/usr/bin/python
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    if ((lat1 == lat2) and (lon1 == lon2)):
        return 0

#    try:
    delta = lon2 - lon1
    a = math.radians(lat1)
    b = math.radians(lat2)
    C = math.radians(delta)
    x = math.sin(a) * math.sin(b) + math.cos(a) * math.cos(b) * math.cos(C)
    distance = math.acos(x) # in radians
    distance  = math.degrees(distance) # in degrees
    distance  = distance * 60 # 60 nautical miles / lat degree
    distance = distance * 1.15077945 # conversion to miles
    distance  = round(distance)
    return distance;
#    except:
#        return 0

def build_sql(zip, school, distance):
    print "insert into schools_zip_school_prox values ( " + str(zip) + "," + str(school) +"," + str(int(dst)) + " );"

#lat1 = '40.434239';
#lon1 = '-74.40504';
#lat2 = '40.598142';
#lon2 = '-73.97229';

#dst = calculate_distance(float(lat1),float(lon1),float(lat2),float(lon2))

zips = []

f = open('zz','r')

max_distance = 20
import re

for line in f:
    parts = line.split(',')
    zip_code = parts[0].replace("'","")
    if not (re.match('^[0-9]{5}$',zip_code)):
        continue
    lat = float(parts[2].replace("'",""))
    lon = float(parts[3].replace("'",""))
    zips.append({ 'z': zip_code, 'lat':lat, 'lon':lon })


s = open('ss','r')

for ssss in s:
    line = ssss.rstrip()
    parts = line.split(',')
    zzz = {}
    zzz['school'] = parts[0]
    zzz['lat'] = float(parts[1])
    zzz['lon'] = float(parts[2])

    for xxx in zips:
#        if zzz['z'] == xxx['z']:
#            continue
        

        dst = calculate_distance(zzz['lat'],zzz['lon'],xxx['lat'],xxx['lon'])
        if dst < max_distance:
            build_sql(zzz['school'], xxx['z'], dst)
#            print "lat1:" + str(zzz['lat'])
#            print "lon1:" + str(zzz['lon'])
#            print "lat2:" + str(xxx['lat'])
#            print "lon2:" + str(xxx['lon'])

#            print zzz['school'] + " -> " + xxx['z'] + " = " + str(dst)

