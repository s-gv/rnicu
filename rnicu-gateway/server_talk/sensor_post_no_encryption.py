'''	sensor-post reads sensor data from a sql lite database and posts it to the server

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
import os
import glob
import time
import re
import urllib2, urllib

debug = True
proxy = "" # "noauthproxy.serc.iisc.ernet.in:3128"
sensor_regex = r'.*(temperature|SpO2)\.([0-9]+)$'

def read_sensors():
        paths = []
        files = []
        ids = []
        
        while True:
                # open new files
                new_paths = [path for path in glob.glob(os.getcwd()+'/*.*') if path not in paths and re.match(sensor_regex,path)]
                new_files = [open(path) for path in new_paths]
                new_ids = [(re.match(sensor_regex,path).group(1), re.match(sensor_regex,path).group(2) ) for path in new_paths]
                
                #goto end of file
                for fil in new_files:
                        fil.seek(0,2)
                
                paths = paths + new_paths
                files = files + new_files
                ids = ids + new_ids
                
                
                for i in range(len(files)):
                        line = files[i].readline()
                        if line: # got a new reading
                                yield (ids[i],line.strip())
                time.sleep(0.1)

def post_reading(reading):
        # reading is a tupe like this (  ('sensor_type','sensor_id') , 'val' )
        
        data=[('sensorid',str(reading[0][1])),('sensortype',str(reading[0][0])),('time',str(int(time.mktime(time.localtime()))*1000)),('val',str(reading[1]))]
        data=urllib.urlencode(data)
        path='https://rnicu-web.appspot.com/sensor/update' 
        req=urllib2.Request(path, data)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        
        try:
                response = urllib2.urlopen(req).read()
                rcode = int(response[0:2])
                if debug:
                        print response
                return rcode
        except:
                return -1

for reading in read_sensors():
        if debug:
                print reading
        post_reading(reading)