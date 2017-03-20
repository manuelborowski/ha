from app import db
 
  
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	
	def __repr__(self):
		return '<User %r>' % (self.nickname)


class FHState:
	NON_PRIORITY	= 'NON_PRIORITY'
	PRIORITY		= 'PRIORITY'
	FORCE			= 'FORCE'

class Room(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40), unique=True)
	scheduled = db.Column(db.Boolean)
	thermal_mass = db.Column(db.Integer)	# x 100
	thermal_loss = db.Column(db.Integer)	# x 100
	floorheating_state = db.Column(db.String(40))
	thermostats = db.relationship('Thermostat', backref='room', lazy='dynamic')
	
	def __repr__(self):
		return '<name %r>' % (self.name)
	
class Thermostat(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40), unique=True)
	hw_id = db.Column(db.String(40))
	min = db.Column(db.Integer)
	max = db.Column(db.Integer)
	desired = db.Column(db.Integer)
	room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

	def __repr__(self):
		return '<hw_id %r>' % (self.hw_id)	


#content of table
#time : time, in minutes, starting from sunday midnight.
# ...
class HeatingSchedule(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.Integer)
	
	def __repr__(self):
		return '<day/index/time : {}>'.format(self.time)
