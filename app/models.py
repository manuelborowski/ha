from app import db
 
  
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	
	def __repr__(self):
		return '<User %r>' % (self.nickname)


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Post %r>' % (self.body)

class Room(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40), unique=True)
	thermostats = db.relationship('Thermostat', backref='room', lazy='dynamic')
	
	def __repr__(self):
		return '<name %r>' % (self.name)
	
class Thermostat(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40))
	enabled = db.Column(db.Boolean)
	min = db.Column(db.Integer)
	max = db.Column(db.Integer)
	desired = db.Column(db.Integer)
	hw_id = db.Column(db.String(40))
	room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

	def __repr__(self):
		return '<hw_id %r>' % (self.hw_id)	

class HeatingSchedule(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	day = db.Column(db.String(20), unique=True)
	heaton = db.Column(db.DateTime)
	heatoff = db.Column(db.DateTime)
	heattype = db.Column(db.String(20))
	index = db.Column(db.Integer)
	
	def __repr__(self):
		return '<day/on/off %r/%r/%r>' % (self.day, self.heaton, self.heatoff)
