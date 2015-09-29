'''
Copyright (c) 2013 Sagar G V

E-mail: sagar.writeme@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from google.appengine.ext import db
import re
import json
import cgi

NUM_OF_TUPLES_PER_ENTITY = 1000

class SensorData(db.Model):
    ''' Models sensor data (tag,timestamp,value). Lists are used as an optimization to lower number of datastore accesses '''
    tag = db.StringProperty()
    ind = db.IntegerProperty() # increased if entity size gets too large and a new entity is created
    times = db.ListProperty(long)
    vals = db.ListProperty(float)
    gates = db.ListProperty(bool) # is that particular reading reliable

''' Internal Functions. Do NOT use outside this module '''

def newEntity(tag,ind,t,v,g):
    e = SensorData()
    e.tag = tag
    e.ind = ind
    updateEntity(e,t,v,g)

def updateEntity(e,t,v,g):
    e.times.append(t)
    e.vals.append(v)
    e.gates.append(g)
    e.put()


''' API to the outside this module '''

def GetVals(tag):
    ''' given a tag, returns an iterator that iterates over (time,value,gate) pairs stored '''
    for entity in SensorData.all().filter('tag =',tag).order('-ind'):
        for (t,val,gate) in reversed(zip(entity.times,entity.vals,entity.gates)):
            yield (t,val,gate)

def AddVal(tag,time,val,gate):
    ''' creates a (tag,time,val,gate) entry in the database. All 4 input arguments are strings.
        Returns:
                0 if success. 
                1 if tagString is invalid (non alphanumeric)
                2 if time is not an Integer
                3 if val is not a float
                -1 if error

    '''
    if not re.match(r'^[A-Za-z0-9]+$',tag):
        return 1
    if not re.match(r'^[0-9]+$',time):
        return 2
    if not re.match(r'^[0-9]*(?:\.[0-9]+)?$',val):
        return 3
    
    g = True
    if gate == "false":
        g = False
    t = int(time)
    v = float(val)

    e = SensorData.all().filter('tag =',tag).order('-ind').get()
    if e:
        ''' a tag of this type already exists. Should I append to the list or create a new entity ? '''
        if len(e.times) < NUM_OF_TUPLES_PER_ENTITY:
            # append to existing entity
            updateEntity(e,t,v,g)
        else:
            # create a new entity
            newEntity(tag,e.ind + 1,t,v,g)
    else:
        ''' entity with this tag does not exist. create a new one '''
        newEntity(tag,0,t,v,g)

    return 0

def AddBulkVals(tag,tvgJSONTuples):
    ''' creates (tag,time,val,gate) entries in the database.
        Returns:
                0 if success. 
                1 if tagString is invalid (non alphanumeric)
                2 if time is not an Integer
                3 if val is not a float
                4 if JSON parse failed
                -1 if error

    '''
    if not re.match(r'^[A-Za-z0-9]+$',tag):
        return 1
    
    try:
        tvgTuples = json.loads(cgi.escape(tvgJSONTuples))
    except:
        return 4
    
    tvgList = []
    for (time, val, gate) in tvgTuples:
        if not re.match(r'^[0-9]+$',time):
            return 2
        if not re.match(r'^[0-9]*(?:\.[0-9]+)?$',val):
            return 3
        g = True
        if gate == "false":
            g = False
        t = int(time)
        v = float(val)
        tvgList.append((t, v, g))

    e = SensorData.all().filter('tag =',tag).order('-ind').get()

    while len(tvgList) > 0:
        if e:
            if len(e.times) < NUM_OF_TUPLES_PER_ENTITY:
                m = NUM_OF_TUPLES_PER_ENTITY - len(e.times)
            else:
                # create new entity
                m = NUM_OF_TUPLES_PER_ENTITY
                last_ind = e.ind
                e = SensorData()
                e.tag = tag
                e.ind = last_ind + 1
        else:
            # first time !
            m = NUM_OF_TUPLES_PER_ENTITY
            e = SensorData()
            e.tag = tag
            e.ind = 0

        chunk = tvgList[:m]
        tvgList = tvgList[m:]

        e.times += [t for (t, v, g) in chunk]
        e.vals += [v for (t, v, g) in chunk]
        e.gates += [g for (t, v, g) in chunk]
        e.put()

    return 0

