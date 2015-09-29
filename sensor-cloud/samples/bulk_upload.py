'''
Copyright (c) 2014 Sagar G V

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
import json

url = 'https://sensor-cloud.appspot.com/bulkupload'
#url = 'http://localhost:8080/bulkupload' 
n = 2213 # Number of psuedo-random readings to post
tag = 'testTag4' # tag of the sensor


def post_bulk_readings(tag, tvgList):
    # readings is like this ( 'tag', [ ('time0' , 'val0', 'gate0'),  ('time1' , 'val1', 'gate1'). . . ] ). gate is either true or false
        
    data=[('tag',str(tag)),('tvgtuples',json.dumps(tvgList))]
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
    tvgList = []
    print "Generating readings . . ."
    for i in range(n):
        t = int((datetime.now() - datetime.utcfromtimestamp(0)).total_seconds() * 1000)
        v = 36 + (i%20)*1.0/20 + random.random()/10.0
        g = "true" # do you believe the reading is reliable?
        if i > n/2:
            g = "false"
        tvg = (str(t),str(v),str(g))
        print tvg
        tvgList.append(tvg)
        time.sleep(0.01)
    print "Send all the above readings in bulk . . ."
    print post_bulk_readings(tag, tvgList)

if __name__ == "__main__":
    main()
