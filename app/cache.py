from app import models, db
import sys, datetime, logging
from threading import Timer, Lock
import time
import config

log = logging.getLogger(__name__)

#------------------common----------------------

_digitalOutputs = []
_thermostats = {}
_rooms = {}
_schedule = []
_lock = Lock()
_dirty = False


def _getLock():
	_lock.acquire()

def _releaseLock():
	_lock.release()
	
def init():
	log.info("initializing...")
	_updateCache()
	_flushCache()
	_initDigitalOutput


def _updateCache():
	global _schedule
	_getLock()
	tl = models.Thermostat.query.all()
	for t in tl:
		_thermostats[t.hw_id] = Thermostat(t)
	rl = models.Room.query.all()
	for r in rl:
		_rooms[r.name] = Room(r)
	_updateHeatingSchedule2Cache()
	_releaseLock()

def _flushCache():
	global _dirty
	if _dirty:
		_getLock()
		_dirty = False
		for t in _thermostats.values():
			if t.dirty == True:
				models.Thermostat.query.filter_by(hw_id=t.hw_id).first().desired = t.desired
				models.Thermostat.query.filter_by(hw_id=t.hw_id).first().enabled = t.enabled
		_flushHeatingSchedule2Cache()
		db.session.commit()
		_releaseLock()
		_updateCache()

	#every xx seconds, scan for dirty (changed) objects and commit them to the database.
	#If no dirty objects then the database is not accessed.
	t = Timer(config.CACHE_UPDATE_DB_DELAY, _flushCache)
	t.start()
	log.info('done committing to database')


#------------------rooms----------------------

class Room:
	def __init__(self, dbRoom):
		self.id = dbRoom.id
		self.name = dbRoom.name
	
	def __repr__(self):
		return '<id/name %r/%r>' % (self.id, self.name)	
		


def getRoomList():
	return sorted(list(_rooms.values()), key=lambda room: room.name)
	
#------------------heating schedule----------------------


class HeatingSchedule:
	def __init__(self, dbHeatingScheduleAm, dbHeatingSchedulePm):
		self.day = dbHeatingScheduleAm.day
		self.index = dbHeatingScheduleAm.index
		self.amHeatingOn = dbHeatingScheduleAm.heaton
		self.amHeatingOff = dbHeatingScheduleAm.heatoff
		self.pmHeatingOn = dbHeatingSchedulePm.heaton
		self.pmHeatingOff = dbHeatingSchedulePm.heatoff
		self.dirty = False
		
	def __repr__(self):
		return '<day[%r]/on[%r]/off[%r]/on[%r]/off[%r]>' % \
			(self.day, self.amHeatingOn, self.amHeatingOff, self.pmHeatingOn, type(self.pmHeatingOff))
	
def getHeatingScheduleList():
	return _schedule

def setHeatingSchedule(day, period, enabled, val):
	global _dirty
	_getLock()
	for h in _schedule:
		if h.day == day:
			if period == 'am':
				if enabled == 'on':
					h.amHeatingOn = datetime.datetime.strptime(val, '%H:%M')
				else:
					h.amHeatingOff = datetime.datetime.strptime(val, '%H:%M')
			else:
				if enabled == 'on':
					h.pmHeatingOn = datetime.datetime.strptime(val, '%H:%M')
				else:
					h.pmHeatingOff = datetime.datetime.strptime(val, '%H:%M')
			h.dirty = True
	_dirty = True
	_releaseLock()
	
#------------------heating schedule 2----------------------

_schedule2 = []
_DAY_OF_WEEK = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']

#Warning : MUST be executed inside _lock() ... _unlock()
def _updateHeatingSchedule2Cache():
	global _schedule2
	_schedule2 = []
	for i,d in enumerate(_DAY_OF_WEEK):
		tl = models.HeatingSchedule2.query.filter(models.HeatingSchedule2.day==i).\
								order_by(models.HeatingSchedule2.index).all()
		l = []
		for t in tl: 
			l.append(t.time)
		_schedule2.append(HeatingSchedule2(i, d, l))
		log.info(_schedule2[i])
			
			
#Warning : MUST be executed inside _lock() ... _unlock()
def _flushHeatingSchedule2Cache():
	for i, s in enumerate(_schedule2):
		if s.dirty:
			tl = models.HeatingSchedule2.query.filter(models.HeatingSchedule2.day==i).\
											order_by(models.HeatingSchedule2.index).all()
			for i, t in enumerate(tl):
				t.time = s.timeList[i]


class HeatingSchedule2:
	def __init__(self, index, day, timeList):
		self.index = index
		self.day = day
		self.timeList = timeList
		self.dirty = False
		
	def __repr__(self):
		return '<day/dirty/times : {}/{}/{}>'.format(self.day, self.dirty, self.timeList)
	
def getHeatingSchedule2List():
	return _schedule2

#day : 0..6 (monday = 0)
#index : 0..3
def setHeatingSchedule2(day, index, val):
	log.info('setHeatingSchedule : day/index/val : {}/{}/{}'.format(day, index, val))
	global _dirty
	_getLock()
	_schedule2[day].timeList[index] = datetime.datetime.strptime(val, '%H:%M')
	_schedule2[day].dirty = True
	_dirty = True
	_releaseLock()
#------------------thermostats----------------------

class Thermostat:
	def __init__(self, dbThermostat):
		self.id = dbThermostat.id
		self.name = dbThermostat.name
		self.enabled = dbThermostat.enabled
		self.min = dbThermostat.min
		self.max = dbThermostat.max
		self.desired = dbThermostat.desired
		self.hw_id = dbThermostat.hw_id
		self.room = dbThermostat.room
		self.dirty = False
		self.active = False
		self.measured = self.desired
		self.follow_schedule = dbThermostat.follow_schedule
		self.batLevel = -100

	def __repr__(self):
		return '<name[%r]/e[%r]/s[%r]/d[%r]/a[%r]/m[%r]>' % \
			(self.name, self.enabled, self.desired, self.dirty, self.active, self.measured)	
			

def getThermostatList(roomName=None):
	if roomName == None:
		return sorted(list(_thermostats.values()), key=lambda thermostat: thermostat.hw_id)
	else:
		_getLock()
		l = []
		for t in _thermostats.values():
			if t.room.name == roomName:
				l.append(t)
		_releaseLock()
		return l


def setThermostatEnabled(hw_id=None, enabled=False):
	_getLock()
	global _dirty
	_thermostats[hw_id].enabled = enabled
	_thermostats[hw_id].dirty = True
	_dirty = True
	_releaseLock()

def setThermostatValue(hw_id=None, desired=0):
	_getLock()
	global _dirty
	_thermostats[hw_id].desired = int(desired)
	_thermostats[hw_id].dirty = True
	_dirty = True
	_releaseLock()
		
def getThermostat(hw_id=None):
	if hw_id:
		return _thermostats[hw_id]
	else:
		return None
		
def getThermostatParameters(hw_id=None):
	return (_thermostats[hw_id].desired, _thermostats[hw_id].measured, _thermostats[hw_id].active, _thermostats[hw_id].enabled)
		
#------------------digital outputs----------------------

class DigitalOut:
	def __init__(self, pin, name):
		self.pin = pin
		self.name = name
		

def _initDigitalOutput():
	global _digitalOutputs
	log.info("set up digital outputs...")
	for n, p in config.DO_OUTPUTS:
		_digitalOutputs.append(DigitalOut(p, n))
	



