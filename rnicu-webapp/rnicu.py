'''
    rnicu-webapp accepts sensor data securely, makes them available anonymously and helps to visualize the sensor data

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

import webapp2
import jinja2
import os
import cgi
from google.appengine.ext import db
from google.appengine.api import users
import re
import Crypto.Cipher.AES as AES
from Crypto import Random
import math
import json

sensor_types = r'(temperature|SpO2)' # example: r'(temp|spo|hr)'

plot_bands = { # [(from,to,'color','label'),..]
        'temperature' : [(-100,35,'rgba(68, 170, 213, 0.2)','hypothermia'),(35,37.8,'rgba(0, 255, 0, 0.2)','normal'),(37.8,100,'rgba(255, 0, 0, 0.2)','fever')]
        }

sensor_data_encryption = False
key = 'rnicusecretpaswd'
signature = 'rnicuprojectauthsignature'

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'])

''' See this for a visualization of the schema. https://github.com/s-gv/rnicu-webapp/wiki/Database-Schema '''
class User(db.Model):
    """Models the User table"""
    userName = db.StringProperty()
    isDoctor = db.BooleanProperty()
    isDispenser = db.BooleanProperty()

class Patient(db.Model):
    """Models the Patient table"""

    patientName = db.StringProperty()
    patientFatherName = db.StringProperty()
    location = db.StringProperty()
    doctorId = db.StringProperty()
    notes = db.StringProperty()
    sensorId = db.StringProperty()

class SensorPatientMap(db.Model):
    ''' Maps SensorID to PatientID '''
    sensorId = db.StringProperty()
    patientId = db.IntegerProperty()

class SensorData(db.Model):
    ''' Stores Sensor data for all patients '''
    patientId = db.IntegerProperty()
    type = db.StringProperty()
    ind = db.IntegerProperty() # increased if entity size gets too large and a new entity is created
    times = db.ListProperty(long)
    vals = db.ListProperty(float)

class MainPage(webapp2.RequestHandler):
    ''' /
        This is the main page. If the user is logged in, the dashboard is displayed.
        Otherwise, a link for anonymous data access is presented
    '''
    def get(self):
        user = users.get_current_user()
        if user:
            self.response.headers['Content-Type'] = 'text/html'
            isDispenser = False
            isDoctor = False
            doctorID = 0
            u = User.all().filter("userName =",user.nickname()).get()
            if u:
                isDispenser = u.isDispenser
            u = User.all().filter("userName =",user.nickname()).get()
            if u:
                isDoctor = u.isDoctor
                doctorID = u.key().id()

            err = self.request.get('error')
            note = self.request.get('note')

            template_values = {
                        'isAdminUser': users.is_current_user_admin(),
                        'logoutURL': users.create_logout_url(self.request.uri),
                        'username' : user.nickname(),
                        'isDispenser' : isDispenser,
                        'isDoctor' : isDoctor,
                        'doctorID' : doctorID,
                        'note': note,
                        'err' : err
            }

            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            self.response.headers['Content-Type'] = 'text/html'
            template_values = {
                'loginURL' : users.create_login_url(self.request.uri)
            }
            template = JINJA_ENVIRONMENT.get_template('blank.html')
            self.response.write(template.render(template_values))

class AdminPage(webapp2.RequestHandler):
    ''' /admin
        This page allows admins to view the list of doctors,tag dispensers in the system
    '''
    def get(self):
        user = users.get_current_user()
        err = self.request.get('error')
        if user:
            if users.is_current_user_admin():
                self.response.headers['Content-Type'] = 'text/html'
                template_values = {
                    'username': user.nickname(),
                    'rnicuUsers' : User.all(),
                    'err' : err,
                    'logoutURL': users.create_logout_url(self.request.uri),
                }
                template = JINJA_ENVIRONMENT.get_template('admin.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect(users.create_logout_url('/'))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class UserCreatePage(webapp2.RequestHandler):
    ''' /admin/user/create
        This page allows admins to add a new doctor/tag dispenser to the system
    '''
    def get(self):
        self.redirect('/')
    def post(self):
        if users.get_current_user() and users.is_current_user_admin():
            new_id = cgi.escape(self.request.get('googleid'))
            new_types = self.request.get_all('type')
            new_isDoctor = 'doctor' in new_types
            new_isDispenser = 'dispenser' in new_types

            if re.match(r'^[a-zA-Z0-9._\-]+$',new_id):
                new_user = User()
                new_user.userName = new_id
                new_user.isDoctor = new_isDoctor
                new_user.isDispenser = new_isDispenser
                new_user.put()
                self.redirect('/admin')
            else:
                self.redirect(cgi.escape('/admin?error=ID Invalid'))
        else:
            self.redirect(cgi.escape('/?error=Need to be admin to do that'))

class UserDeletePage(webapp2.RequestHandler):
    ''' /admin/user/(.*)/delete
        Posting to this route removes the specified doctor/tag dispenser from the system
    '''
    def post(self,google_id):
        #self.response.write(google_id)
        if users.get_current_user() and users.is_current_user_admin():
            q = User.all().filter("userName =",google_id).get()
            if q:
                q.delete()
            self.redirect('/admin')
        else:
            self.redirect(cgi.escape('/?error=Need to be admin to do that'))

class PatientCreatePage(webapp2.RequestHandler):
    ''' /patient/new
        This page presents a form the tag dispenser can fill up to add a patient to the system
        and associate sensor tags to that patient
    '''
    def get(self):
        user = users.get_current_user()
        if user:
            u = User.all().filter("userName =",user.nickname()).get()
            if u and u.isDispenser:
                err = self.request.get('error')
                note = self.request.get('note')
                self.response.headers['Content-Type'] = 'text/html'
                template_values = {
                    'logoutURL': users.create_logout_url('/'),
                    'err':err,
                    'note':note,
                    'sensorid':self.request.get("sensorid")
                }
                template = JINJA_ENVIRONMENT.get_template('patient_create.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect(cgi.escape('/?error=Need to be a tag dispenser to do that'))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        user = users.get_current_user()
        if user:
            u = User.all().filter("userName =",user.nickname()).get()
            if u and u.isDispenser:
                name = cgi.escape(self.request.get('patientName'))
                fname = cgi.escape(self.request.get('patientFatherName'))
                loc = cgi.escape(self.request.get('location'))
                gid = cgi.escape(self.request.get('doctorID'))
                sensorid = cgi.escape(self.request.get('sensorID'))
                notes = cgi.escape(self.request.get('notes'))

                if re.match(r'^[a-zA-Z0-9._\- ]+$',name) and re.match(r'^[a-zA-Z0-9._\- ]+$',fname) and re.match(r'^[a-zA-Z0-9._\- ]+$',loc) and re.match(r'^[a-zA-Z0-9._\-]+$',gid) and re.match(r'^[,a-zA-Z0-9._\-]+$',sensorid) and re.match(r'^[a-z A-Z0-9._\-]*$',notes):
                    doc = User.all().filter("userName =",gid).get()
                    if not doc:
                        self.redirect(cgi.escape('/patient/new?error=Doctor not found in the database'))
                        return

                    patient = Patient()
                    patient.patientName = name
                    patient.patientFatherName = fname
                    patient.location = loc
                    patient.doctorId = gid
                    patient.notes = notes
                    patient.sensorId = sensorid
                    patient.put()

                    pid = patient.key().id()

                    for sid in sensorid.split(','):
                        sensortagmap = SensorPatientMap.all().filter("sensorId =",sid).get()
                        if not sensortagmap:
                            newtag = SensorPatientMap()
                            newtag.sensorId = sid
                            newtag.patientId = pid
                            newtag.put()
                        else:
                            sensortagmap.patientId = pid
                            sensortagmap.put()

                    self.redirect(cgi.escape('/?note=Tag mapped to patient successfully'))

                else:
                    self.redirect(cgi.escape('/patient/new?error=Invalid data entered'))
            else:
                self.redirect(cgi.escape('/?error=Need to be a tag dispenser to do that'))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class SensorBulkUpdatePage(webapp2.RequestHandler):
    ''' /sensor/bulkupdate 
        The gateway POSTs multiple readings to this page to upload a bunch of sensor readings at once
    '''
    def post(self):
        sensorid = cgi.escape(self.request.get('sensorid'))
        sensortype = cgi.escape(self.request.get('sensortype'))

        #find patient ID given sensorid
        q = SensorPatientMap.all().filter('sensorId =',sensorid).get()
        if not q:
            self.response.write('01 Sensor not attached to any known patient')
            return
        patientId = q.patientId

        # is the sensortype recognized
        if not re.match(sensor_types,sensortype):
            self.response.write('02 Sensor Type not recognized')
            return

        # prep the list of readings
        try:
            tvpairs = json.loads(cgi.escape(self.request.get('tvpairs')))
            try:
                tvpairs = [(long(t), float(v)) for (t, v) in tvpairs]
            except:
                self.response.write('05 Failed converting (t,v) to type (long,float)')
                return
        except:
            self.response.write('07 JSON parse failed')
            return

        # TODO: decryption if encryption is enabled
        if sensor_data_encryption:
            self.response.write('08 Encrypted bulk transfer not implemented')
            return

        n = len(tvpairs)
        for tv in tvpairs:
            try:
                t = long(tv[0])
                v = float(tv[1])
            except:
                self.response.write('05 Failed converting (t,v) to type (long,float)')
                return
        
        # add the readings
        e = SensorData.all().filter('patientId =',int(patientId)).filter('type =',str(sensortype)).order('-ind').get()
        
        last_ind = -1

        while len(tvpairs) > 0:
            if e:
                if len(e.times) < 1000:
                    m = 1000 - len(e.times)
                else:
                    # create new entity
                    m = 1000
                    last_ind = e.ind
                    e = SensorData()
                    e.patientId = patientId
                    e.type = sensortype
                    e.ind = last_ind + 1
            else:
                # first time !
                e = SensorData()
                m = 1000
                e.patientId = patientId
                e.type = sensortype
                e.ind = 0

            chunk = tvpairs[:m]
            tvpairs = tvpairs[m:]

            e.times += [t for (t, v) in chunk]
            e.vals += [v for (t, v) in chunk]

            e.put()

        self.response.write('00 Done! ')


class SensorUpdatePage(webapp2.RequestHandler):
    ''' /sensor/update
        The gateway POSTs to this page to upload sensor data
    '''
    def post(self):
        sensorid = cgi.escape(self.request.get('sensorid'))
        sensortype = cgi.escape(self.request.get('sensortype'))
        timestamp = cgi.escape(self.request.get('time'))
        if sensor_data_encryption:
            msg = cgi.escape(self.request.get('val'))
            try:
                iv = msg[:2*AES.block_size].decode('hex')
                value_ciphertext = msg[2*AES.block_size:]
                mode = AES.MODE_CBC
                decryptor = AES.new(key, mode,iv)

                value = decryptor.decrypt(value_ciphertext.decode('hex'))

                self.response.headers['Content-Type'] = 'text/plain'

                # check if the signature is correct
                l = len(signature)
                if len(value) < l or value[-1*l:] != signature:
                    self.response.write('03 Signature incorrect')
                    return
                value = value[:-1*l].strip()
            except:
                self.response.write('04 Signature decode error')
                return
        else:
            value = cgi.escape(self.request.get('val'))

        #find patient ID given sensorid
        q = SensorPatientMap.all().filter('sensorId =',sensorid).get()
        if not q:
            self.response.write('01 Sensor not attached to any known patient')
            return
        patientId = q.patientId
        #attach data to the write sensor data table
        if re.match(sensor_types,sensortype):
            try:
                t = long(timestamp)
                v = float(value)
            except:
                self.response.write('05 Failed converting (t,v) to type (long,float)')
                return

            e = SensorData.all().filter('patientId =',int(patientId)).filter('type =',str(sensortype)).order('-ind').get()
            last_ind = -1
            if e:
                if len(e.times) < 1000:
                    # append to the time series in this entity  
                    pass
                else:
                    # create new entity
                    last_ind = e.ind
                    e = SensorData()
                    e.patientId = patientId
                    e.type = sensortype
                    e.ind = last_ind + 1
            else:
                # first time !
                e = SensorData()
                e.patientId = patientId
                e.type = sensortype
                e.ind = 0

            e.times.append(t)
            e.vals.append(v)
            e.put()

        else:
            self.response.write('02 Sensor Type not recognized')
            return

        # all went well
        self.response.write('00 Done! ')


class AnonPatientPage(webapp2.RequestHandler):
    ''' /patient
        This page lists patients only by patient ID and location for anonymous data access
    '''
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_values = {
            'logoutURL': users.create_logout_url('/'),
            'patients': Patient.all()
        }
        template = JINJA_ENVIRONMENT.get_template('anonpatient.html')
        self.response.write(template.render(template_values))

class PatientSensorDataPage(webapp2.RequestHandler):
    ''' /patient/([0-9]+)/'+sensor_types
        This page displays plaintext CSV sensor data for a given patient and sensor type
    '''
    def get(self,patientID,sensor_type):
        self.response.headers['Content-Type'] = 'text/plain'
        for i in getDataSeriesForPatient(patientID,sensor_type):
            self.response.write(str(i[0])+','+str(i[1])+'\n')

class PatientSensorDataGraphPage(webapp2.RequestHandler):
    ''' /patient/([0-9]+)/'+sensor_types+'/graph
        This page visualizes on a graph sensor data from a specific patient and sensor type
    '''
    def get(self,patientID,sensor_type):
        self.response.headers['Content-Type'] = 'text/html'
        bands = plot_bands.get(sensor_type,[])
        r = re.match(r'(.*)/graph/?',self.request.uri)
        template_values = {
            'yName': sensor_type.capitalize(),
            'series': getDataSeriesForPatient(patientID,sensor_type),
            'ebands' : enumerate(bands),
            'nbands' : len(bands),
            'url' : r.group(1)
        }
        template = JINJA_ENVIRONMENT.get_template('sensordataplot.html')
        self.response.write(template.render(template_values))

class DoctorPage(webapp2.RequestHandler):
    ''' /doctor/([0-9]+)/
        This page lists the patients that a doctor is caring for.
    '''
    def get(self,doctorID):
        user = users.get_current_user()
        if user:
            u = User.all().filter("userName =",user.nickname()).get()
            if u and u.isDoctor:
                q = User.all().filter("userName =",user.nickname()).get()
                if q and q.key().id() == int(doctorID):
                    self.response.headers['Content-Type'] = 'text/html'
                    template_values = {
                        'logoutURL': users.create_logout_url('/'),
                        'patients': Patient.all().filter('doctorId =',user.nickname())
                    }
                    template = JINJA_ENVIRONMENT.get_template('patienttable.html')
                    self.response.write(template.render(template_values))
                else:
                    self.redirect('/?error=Access Control Violation')
            else:
                self.redirect('/?error=Need to be a doctor to do that')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class PatientDataPage(webapp2.RequestHandler):
    ''' /patient/([0-9]+)/
        This page lists links to pages that'll display sensor data for different sensor types
    '''
    def get(self,patientID):
        self.response.headers['Content-Type'] = 'text/html'
        template_values = {
            'logoutURL': users.create_logout_url('/'),
            'patientId' : patientID,
            'sensorlist' : sensor_types[1:-1].split('|')
        }
        template = JINJA_ENVIRONMENT.get_template('patientdata.html')
        self.response.write(template.render(template_values))


def getDataSeriesForPatient(patientID,sensortype):
    for entity in SensorData.all().filter('patientId =',int(patientID)).filter('type =',str(sensortype)).order('-ind'):
        for (t,val) in reversed(zip(entity.times,entity.vals)):
            if not math.isnan(val):
                yield (t,val)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/admin/?',AdminPage),
    ('/admin/user/create',UserCreatePage),
    (r'/admin/user/(.*)/delete',UserDeletePage),
    (r'/patient/new/?',PatientCreatePage),
    ('/patient/create',PatientCreatePage),
    ('/sensor/update',SensorUpdatePage),
    ('/sensor/bulkupdate',SensorBulkUpdatePage),
    ('/patient/?',AnonPatientPage),
    (r'/patient/([0-9]+)/'+sensor_types+'/?$',PatientSensorDataPage),
    (r'/patient/([0-9]+)/?',PatientDataPage),
    (r'/doctor/([0-9]+)/?',DoctorPage),
    (r'/patient/([0-9]+)/'+sensor_types+'/graph/?$',PatientSensorDataGraphPage)
], debug=True)
