'''
post-random simulates a gateway connected to a temperature sensor tag.
When called from the command line, a random temperature reading between 90 and 110 is sent with a timestamp corresponding to when the script was called.

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
import Crypto.Cipher.AES as AES
from Crypto import Random

debug = True
key = 'rnicusecretpaswd'
signature = 'rnicuprojectauthsignature'
iv = Random.new().read(AES.block_size)
mode = AES.MODE_CBC
encryptor = AES.new(key, mode,iv)

def post_reading(reading):
	# reading is a tupe like this (  'sensor_type','sensor_id' , 'time' , 'val' )
	if len(reading[3]) < 7:
		r = reading[3] + ' '*(7-len(reading[3]))
	else:
		r = reading[3]
	
	plaintext = r + signature # 7+25 chars
	ciphertext = str(iv).encode('hex') + encryptor.encrypt(plaintext).encode('hex')
	print '\nplaintext sensor data: '+plaintext,'\n\nciphertext sensor data: '+ciphertext

	data=[('sensorid',reading[1]),('sensortype',reading[0]),('time',reading[2]),('val',ciphertext)]
	data=urllib.urlencode(data)
	path='https://rnicu-web.appspot.com/sensor/update'#'http://localhost:8080/sensor/update' 
	req=urllib2.Request(path, data)
	req.add_header("Content-type", "application/x-www-form-urlencoded")

	response = urllib2.urlopen(req).read()
	rcode = int(response[0:2])
	if debug:
		print response
	return rcode

print post_reading(('temperature','005',str(int(time.mktime(time.localtime()))*1000),str(90+random.randint(0,20))))