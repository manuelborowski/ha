from app import models, db
import sys, datetime, logging
from threading import Timer, Lock
import time

log = logging.getLogger(__name__)

class Room:
	def __init__(self, dbRoom):
		self.id = dbRoom.id
		self.name = dbRoom.name
	
	def __repr__(self):
		return '<id/name %r/%r>' % (self.id, self.name)	
		

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

	def __repr__(self):
		return '<name[%r]/e[%r]/s[%r]/d[%r]/a[%r]/m[%r]>' % \
			(self.name, self.enabled, self.desired, self.dirty, self.active, self.measured)	
			
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
	log.info("starting...")
	_updateCache()
	_flushCache()


def getThermostatList(roomName=None):
	if roomName == None:
		return list(_thermostats.values())
	else:
		_getLock()
		l = []
		for t in _thermostats.values():
			if t.room.name == roomName:
				l.append(t)
		_releaseLock()
		return l

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

def getRoomList():
	return list(_rooms.values())

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
		
def getThermostatParameters(hw_id=None):
	return (_thermostats[hw_id].desired, _thermostats[hw_id].measured, _thermostats[hw_id].active, _thermostats[hw_id].enabled)
		
def _updateCache():
	global _schedule
	_getLock()
	tl = models.Thermostat.query.all()
	for t in tl:
		_thermostats[t.hw_id] = Thermostat(t)
	rl = models.Room.query.all()
	for r in rl:
		_rooms[r.name] = Room(r)
	hl = models.HeatingSchedule.query.order_by(models.HeatingSchedule.index). \
				order_by(models.HeatingSchedule.heattype).all()
	_schedule = []
	for h, i in zip(hl[0::2], hl[1::2]):
		_schedule.append(HeatingSchedule(h, i))
	log.debug("thermostats " + str(_thermostats))
	log.debug("rooms " + str(_rooms))
	log.debug("schedule " + str(_schedule))
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
		for s in _schedule:
			if s.dirty == True:
				l = models.HeatingSchedule.query.filter_by(day=s.day).order_by(models.HeatingSchedule.heattype).all()
				l[0].heaton = s.amHeatingOn
				l[0].heatoff = s.amHeatingOff
				l[1].heaton = s.pmHeatingOn
				l[1].heaton = s.pmHeatingOn
		db.session.commit()
		_releaseLock()
		_updateCache()

	#every xx seconds, scan for dirty (changed) objects and commit them to the database.
	#If no dirty objects then the database is not accessed.
	t = Timer(600, _flushCache)
	t.start()
	log.info('done committing to database')

