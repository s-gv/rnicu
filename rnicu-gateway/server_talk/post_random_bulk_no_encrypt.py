'''
post-random simulates a gateway connected to a temperature sensor tag.

    Copyright (C) 2013  Sagar G V
    E-mail : sagar.writeme@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import httplib
import urllib
import time
import random
import urllib2, urllib
import json

debug = True

def post_readings(readings):
    # readings is a tupe like this ( 'sensor_type','sensor_id' , [ ('time0' , 'val0'), ('time1, 'val1') . . . ] )
    tvpairs_j = json.dumps(readings[2])
    data=[('sensorid',str(readings[1])), ('sensortype',str(readings[0])), ('tvpairs',tvpairs_j)]
    data=urllib.urlencode(data)
    #path='http://localhost:8080/sensor/bulkupdate' 
    path='https://rnicu-cloud.appspot.com/sensor/bulkupdate' 
    req=urllib2.Request(path, data)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
        
    try:
        response = urllib2.urlopen(req).read()
        rcode = int(response[0:2])
        if debug:
            print response
        return rcode
    except Exception as e:
        print str(e)
        return -1

start = int(time.mktime(time.gmtime()))*1000
n = 1331
delta = 15*60*1000

tvpairs = [] # list of (time, value) tuples

# prepare a list of 'n' readings
for i in range(n):
    t = str(start + i*delta) # time in ms since epoch
    v = str(36 + (i%20)*1.0/20 + random.random()/10.0) # some random temperature reading
    tvpairs.append( (t, v) )

print post_readings(('temperature','1239',tvpairs))
