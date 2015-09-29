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

import time
import urllib2, urllib
import sqlite3 as lite

debug = True

con = lite.connect('temp.db',isolation_level=None)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS SensorData(Id INTEGER PRIMARY KEY, time STRING, sensorid STRING, sensortype STRING, sensordata STRING);")

def read_sensor_data():
	s = cur.execute("SELECT Id,time,sensortype,sensorid,sensordata FROM SensorData ORDER BY RANDOM() LIMIT 1;")
	if s:
		r = s.fetchone()
		if r:
			id,t,sensortype,sensorid,sensordata = r
			return [ str(id), str(sensortype), str(sensorid), str(t), str(sensordata) ]

def delete_sensor_data(id):
	cur.execute("DELETE FROM SensorData WHERE Id=%s" % str(id))

def post_reading(reading):
	# reading is a tupe like this (  'sensor_type','sensor_id' , 'time' , 'val_ciphertext' )

	data=[('sensorid',reading[1]),('sensortype',reading[0]),('time',reading[2]),('val',reading[3])]
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

while True:
	r = read_sensor_data()
	if r:
		ret = post_reading(r[1:])
		if ret == 0:
			delete_sensor_data(r[0])
		else:
			if debug:
				print ret
			time.sleep(5)
	time.sleep(1)