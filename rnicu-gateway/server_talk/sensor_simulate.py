'''	sensor-simulate simulates a sensor and writes into a sql lite database

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

import random
import time
import sqlite3 as lite
import Crypto.Cipher.AES as AES
from Crypto import Random


sensortype = "temperature"
sensorid = "1234"
debug = True
key = 'rnicusecretpaswd'
signature = 'rnicuprojectauthsignature'




con = lite.connect('temp.db',isolation_level=None,timeout=20.0)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS SensorData(Id INTEGER PRIMARY KEY, time STRING, sensorid STRING, sensortype STRING, sensordata STRING);")

while True:
	t = str(int(time.mktime(time.localtime()))*1000)
	reading = 26.2 + random.random()
	reading = str(reading)
	if len(reading) < 7:
		r = reading + ' '*(7-len(reading))
	else:
		r = reading[:7]
	plaintext = r + signature
	
	iv = Random.new().read(AES.block_size)
	mode = AES.MODE_CBC
	encryptor = AES.new(key, mode,iv)
	
	ciphertext = encryptor.encrypt(plaintext).encode('hex')
	msg = str(iv).encode('hex') + ciphertext
	
	cur.execute('''INSERT INTO SensorData (time,sensorid,sensortype,sensordata) VALUES('%(time)s', '%(sensorid)s', '%(sensortype)s','%(reading)s');'''
						% {
						'sensorid': sensorid,
						'time':t,
						'sensortype':sensortype,
						'reading':msg
						}) 
	print t,plaintext
	time.sleep(5)
con.close()
	
