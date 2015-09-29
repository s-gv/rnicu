'''
Copyright (c) 2013-14 Sagar G V

E-mail: sagar.writeme@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import httplib
import urllib
import time
import random
import urllib2, urllib
import sys
from datetime import datetime

url = 'https://sensor-cloud.appspot.com/upload'
#url = 'http://localhost:8080/upload' 
n = 10 # Number of psuedo-random readings to post
tag = 'testTag1' # tag of the sensor


def post_reading(reading):
    # reading is a tupe like this ( 'tag', 'time' , 'val', 'gate' ). gate is either true or false
        
    data=[('tag',str(reading[0])),('time',str(reading[1])),('value',str(reading[2])),('gate', str(reading[3]))]
    data=urllib.urlencode(data)
    path=url
    req=urllib2.Request(path, data)
    req.add_header("Content-type", "application/x-www-form-urlencoded")

    try:
        response = urllib2.urlopen(req).read()
        rcode = int(response)
        return rcode
    except:
        return -1

def main():
    print 'Will send %s samples to %s\nIf the return value is 0, its OK. Any other return value is an error' % (n, url)
    for i in range(n):
        t = int((datetime.now() - datetime.utcfromtimestamp(0)).total_seconds() * 1000)
        v = 36 + (i%20)*1.0/20 + random.random()/10.0
        g = "true" # do you believe the reading is reliable?
        if i > n/2:
            g = "false"
        packet = (tag,str(t),str(v),str(g))
        print post_reading(packet)
        time.sleep(1)

if __name__ == "__main__":
    main()
