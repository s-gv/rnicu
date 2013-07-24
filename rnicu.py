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

sensor_types = r'(temperature|SpO2)' # example: r'(temp|spo|hr)'
sensor_data_encryption = False
key = 'rnicusecretpaswd'
signature = 'rnicuprojectauthsignature'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

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
	''' Stores Temperature data for all patients '''
	patientId = db.IntegerProperty()
	time = db.StringProperty()
	type = db.StringProperty()
	val = db.StringProperty()

class MainPage(webapp2.RequestHandler):

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
	def get(self):
		self.redirect('/')
	def post(self):
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

class UserDeletePage(webapp2.RequestHandler):
	def post(self,google_id):
		#self.response.write(google_id)
		q = User.all().filter("userName =",google_id).get()
		if q:
			q.delete()
		self.redirect('/admin')

class PatientCreatePage(webapp2.RequestHandler):
	def get(self):
		err = self.request.get('error')
		note = self.request.get('note')
		self.response.headers['Content-Type'] = 'text/html'
		template_values = {
			'logoutURL': users.create_logout_url('/'),
			'err':err,
			'note':note
		}
		template = JINJA_ENVIRONMENT.get_template('patient_create.html')
		self.response.write(template.render(template_values))
		
	def post(self):
		name = cgi.escape(self.request.get('patientName'))
		fname = cgi.escape(self.request.get('patientFatherName'))
		loc = cgi.escape(self.request.get('location'))
		gid = cgi.escape(self.request.get('doctorID'))
		sensorid = cgi.escape(self.request.get('sensorID'))
		notes = cgi.escape(self.request.get('notes'))
		
		if re.match(r'^[a-zA-Z0-9._\- ]+$',name) and re.match(r'^[a-zA-Z0-9._\- ]+$',fname) and re.match(r'^[a-zA-Z0-9._\- ]+$',loc) and re.match(r'^[a-zA-Z0-9._\-]+$',gid) and re.match(r'^[a-zA-Z0-9._\-]+$',sensorid) and re.match(r'^[a-zA-Z0-9._\-]*$',notes):
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
			
			sensortagmap = SensorPatientMap.all().filter("sensorId =",sensorid).get()
			if not sensortagmap:
				newtag = SensorPatientMap()
				newtag.sensorId = sensorid
				newtag.patientId = pid
				newtag.put()
			else:
				sensortagmap.patientId = pid
				sensortagmap.update()
			
			self.redirect(cgi.escape('/?note=Tag mapped to patient successfully'))
	
		else:
			self.redirect(cgi.escape('/patient/new?error=Invalid data entered'))

class SensorUpdatePage(webapp2.RequestHandler):
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
			d = SensorData()
			d.patientId = patientId
			d.time = timestamp
			d.val = value
			d.type = sensortype
			d.put()
			
		else:
			self.response.write('02 Sensor Type not recognized')
			return
		
		# all went well
		self.response.write('00 Done! ')


class AnonPatientPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		template_values = {
			'logoutURL': users.create_logout_url('/'),
			'patients': Patient.all()
		}
		template = JINJA_ENVIRONMENT.get_template('anonpatient.html')
		self.response.write(template.render(template_values))

class PatientSensorDataPage(webapp2.RequestHandler):
	def get(self,patientID,sensor_type):
		self.response.headers['Content-Type'] = 'text/plain'
		for i in getDataSeriesForPatient(patientID,sensor_type):
			self.response.write(str(i.time)+','+str(i.val)+'\n')

class PatientSensorDataGraphPage(webapp2.RequestHandler):
	def get(self,patientID,sensor_type):
		self.response.headers['Content-Type'] = 'text/html'
		
		template_values = {
			'yName': 'Temperature',
			'yUnit': 'Fahrenheit',
			'series': getDataSeriesForPatient(patientID,sensor_type)
		}
		template = JINJA_ENVIRONMENT.get_template('sensordataplot.html')
		self.response.write(template.render(template_values))

class DoctorPage(webapp2.RequestHandler):
	def get(self,doctorID):
		user = users.get_current_user()
		if user:
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
			self.redirect('/')

class PatientDataPage(webapp2.RequestHandler):
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
	return SensorData.all().filter('patientId =',int(patientID)).filter('type =',str(sensortype)).order('-time')

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/admin/?',AdminPage),
	('/admin/user/create',UserCreatePage),
	(r'/admin/user/(.*)/delete',UserDeletePage),
	('/patient/new',PatientCreatePage),
	('/patient/create',PatientCreatePage),
	('/sensor/update',SensorUpdatePage),
	('/patient/?',AnonPatientPage),
	(r'/patient/([0-9]+)/'+sensor_types+'/?$',PatientSensorDataPage),
	(r'/patient/([0-9]+)/?',PatientDataPage),
	(r'/doctor/([0-9]+)/?',DoctorPage),
	(r'/patient/([0-9]+)/'+sensor_types+'/graph/?$',PatientSensorDataGraphPage)
], debug=True)
