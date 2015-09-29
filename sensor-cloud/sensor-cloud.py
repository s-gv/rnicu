'''
Copyright (c) 2013 Sagar G V

E-mail: sagar.writeme@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import webapp2
import jinja2
import re
import math
import os
import sensorstore

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class MainPage(webapp2.RequestHandler):
    def get(self):
        ''' /
            This page lists all tags that stored in the database.
        '''
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())

class DataPage(webapp2.RequestHandler):
    def get(self):
        ''' /data
            This page lists all (time,value) pairs for the tag requested in the most recent first order
        '''
        tag = self.request.get('tag')
        graph = self.request.get('graph')
        if graph:
            ''' display a graph '''
            tag = self.request.get('tag')
            reliableSeries = []
            unreliableSeries = []
            fullSeries = []
            lastReliable = None
            for dp in sensorstore.GetVals(tag):
                # scan series from right to left on x-axis
                fullSeries = [(dp[0], dp[1])] + fullSeries
                series = reliableSeries if dp[2] else unreliableSeries
                if lastReliable != dp[2]:
                    # create a new line
                    series.append([(dp[0], dp[1])])
                else:
                    series[-1] = [(dp[0], dp[1])] + series[-1]
                lastReliable = dp[2]
            template_values = {
                            'yName': tag,
                            'reliableSeries': reliableSeries,
                            'unreliableSeries': unreliableSeries,
                            'fullSeries': fullSeries
                    }
            template = JINJA_ENVIRONMENT.get_template('sensordataplot.html')
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(template.render(template_values))
        else:
            ''' display raw CSV '''
            self.response.headers['Content-Type'] = 'text/plain'
            for i in sensorstore.GetVals(tag):
                self.response.write(str(i[0])+','+str(i[1])+','+str(i[2])+'\n')


class UploadPage(webapp2.RequestHandler):
    def post(self):
        ''' /upload
            This page creates adds an entry (tag,time,value,gate)
        '''
        tag = self.request.get('tag')
        time = self.request.get('time')
        value = self.request.get('value')
        gate = self.request.get('gate')

        rval = sensorstore.AddVal(tag,time,value,gate)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(str(rval))

class BulkUploadPage(webapp2.RequestHandler):
    def post(self):
        ''' /bulkupload
            This page creates adds an entries (tag,time,value,gate)
        '''
        tag = self.request.get('tag')
        tvgs = self.request.get('tvgtuples')
        rval = sensorstore.AddBulkVals(tag,tvgs)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(str(rval))


application = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/data',DataPage),
        ('/upload',UploadPage),
        ('/bulkupload', BulkUploadPage)
], debug=True)
