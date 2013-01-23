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

def build_sql(zip1, zip2, distance):
    print "insert into places_zip_prox values ( " + str(zip1) + "," + str(zip2) +"," + str(int(dst)) + " );"

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


for zzz in zips:
    for xxx in zips:
        if zzz['z'] == xxx['z']:
            continue
        
        dst = calculate_distance(float(zzz['lat']),float(zzz['lon']),float(xxx['lat']),float(xxx['lon']))
        if dst < max_distance:
            build_sql(zzz['z'], xxx['z'], dst)
#            print zzz['z'] + " -> " + xxx['z'] + " = " + str(dst)




# '35020', 'AL', ' 33.405559', ' -86.95141', 'Bessemer', 'Alabama'

