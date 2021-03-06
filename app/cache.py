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
	_getLock()
	_updateThermostatCache()
	_updateRoomCache()
	_updateHeatingScheduleCache()
	_releaseLock()

def _flushCache():
	global _dirty
	if _dirty:
		_getLock()
		_dirty = False
		_flushThermostatCache()
		_flushHeatingScheduleCache()
		db.session.commit()
		_releaseLock()
		#_updateCache()

	#every xx seconds, scan for dirty (changed) objects and commit them to the database.
	#If no dirty objects then the database is not accessed.
	t = Timer(config.CACHE_UPDATE_DB_DELAY, _flushCache)
	t.start()
	log.info('done committing to database')

#------------------rooms----------------------

#non-priority : when the desired room temperature is reached, then the heating is switched off, 
# even if the floorheating did not reach its desired value
#priority : first the floorheating is enabled until the desired temperature is reached.  Then the
# radiators are enabled until the desired room temperature is reached
#force : the radiators and floorheating is reached.  The radiators are switched off when the 
# desired room temperature is reached.  The floorheating is swithced off only when the desired
# floorheating temperature is reached.
class FHmode:
	NON_PRIORITY	= 'NON_PRIORITY'
	PRIORITY		= 'PRIORITY'
	FORCE			= 'FORCE'

#off : the heating is off
#priming : the room is heated so that it can reach the desired temperature(s).  See also here above
#on : the room has reached its desired temperature and the temperature is sustained.
class HeatingState:
	OFF				= 'OFF'
	PRIMING			= 'PRIMING'
	ON				= 'ON' 
	
class ThermostatType:
	RADIATOR		= 'RADIATOR'
	FLOOR			= 'FLOOR'
	
class Room:
	def __init__(self, dbRoom):
		self.id = dbRoom.id
		self.name = dbRoom.name
		self.enabled = False
		self.scheduled = dbRoom.scheduled
		self.thermal_mass = dbRoom.thermal_mass
		self.thermal_loss = dbRoom.thermal_loss
		self.floorheating_mode = dbRoom.floorheating_mode
		self.state = HeatingState.OFF
		self.floorThermostat = []
		for t in dbRoom.thermostats:
			if t.type == ThermostatType.RADIATOR:
				self.radiatorThermostat = getThermostat(t.hw_id)
			else:
				self.floorThermostat.append(getThermostat(t.hw_id))
	
	def __repr__(self):
		line = '<room : n/e/s/tm/tl/fm/st : {}/{}/{}/{}/{}/{}/{}>'.format(self.name, \
			self.enabled, self.scheduled, self.thermal_mass, self.thermal_loss, \
			self.floorheating_mode, self.state)
		line += '\nradiator thermostat : {}'.format(self.radiatorThermostat)
		for t in self.floorThermostat:
			line += '\nfloor thermostat : {}'.format(t)
		return line

def _updateRoomCache():
	rl = models.Room.query.all()
	for r in rl:
		_rooms[r.name] = Room(r)
		log.debug(_rooms[r.name])
		
def getRoomList():
	return sorted(list(_rooms.values()), key=lambda room: room.name)
	
def setRoomStatus(name=None, enabled=False):
	_getLock()
	log.info('changed state of room {} to {}'.format(name, enabled))
	_rooms[name].enabled = enabled
	_releaseLock()
	
def getRoomStatus(name=None):
	return _rooms[name].enabled

#------------------heating schedule ----------------------

class IdValDirty:
	def __init__(self, id, val):
		self.id = id
		self.val = val
		self.dirty = False
		
	def __repr__(self):
		return '<id/val/dirty : {}/{}/{}>'.format(self.id, self.val, self.dirty)

_schedule = []
_version = 1

#Warning : MUST be executed inside _lock() ... _unlock()
def _updateHeatingScheduleCache():
	global _schedule
	_schedule=[]
	if config.SCHEDULE_TEST:
		for i in range(0, 60*24*7, 10): #every 10 minutes
			_schedule.append(IdValDirty(i, i))
	else:
		sl = models.HeatingSchedule.query.order_by(models.HeatingSchedule.time).all()
		for s in sl: _schedule.append(IdValDirty(s.id, s.time))
			
#Warning : MUST be executed inside _lock() ... _unlock()
def _flushHeatingScheduleCache():
	global _version
	if config.SCHEDULE_TEST: return
	for s in _schedule:
		if s.dirty:
			t = models.HeatingSchedule.query.filter(models.HeatingSchedule.id==s.id).first()
			t.time = s.val
			s.dirty = False
	_version += 1

def getHeatingScheduleList():
	_getLock()
	_releaseLock()
	return _schedule

def getHeatingScheduleForViewing():	
	if config.SCHEDULE_TEST:
		return {}
	else:
		day = 0
		threshold = 1440
		tl = []
		dct = {}
		for t in _schedule:
			if t.val > threshold:
				dct[config.DAY_OF_WEEK_LIST[day]] = tl
				day += 1
				threshold += 1440
				tl = []
			minInDay = t.val + 1440 - threshold
			shour = int(minInDay / 60)
			smin = minInDay - 60 * shour
			tl.append(IdValDirty(t.id, '%02d:%02d' % (shour, smin)))
		#add sunday...
		dct[config.DAY_OF_WEEK_LIST[day]] = tl
		log.debug('Schedule list for viewing : {}'.format(dct))
		return dct

def getHeatingScheduleVersion():
	return _version

#id : database index
#val : 06:30
def setHeatingSchedule(id, val):
	global _dirty
	global _schedule
	global _version
	log.info('setHeatingSchedule : id/val/version : {}/{}/{}'.format(id, val, _version))
	_getLock()
	for s in _schedule:
		if s.id == id:
			day = int(s.val / 1440)  #calculate the day
			hm = val.split(':')
			s.val = day * 1440 + int(hm[0]) * 60 + int(hm[1])
			s.dirty = True
			break
	#make sure the list is sorted!
	_schedule.sort(key=lambda x: x.val)
	_dirty = True
	_version += 1
	_releaseLock()
			
#------------------thermostats----------------------

class Thermostat:
	def __init__(self, dbThermostat):
		self.id = dbThermostat.id
		self.name = dbThermostat.name
		self.min = dbThermostat.min
		self.max = dbThermostat.max
		self.desired = dbThermostat.desired
		self.hw_id = dbThermostat.hw_id
		self.room = dbThermostat.room
		self.dirty = False
		self.active = False
		self.measured = self.desired
		self.batLevel = -100

	def __repr__(self):
		return '<name[%r]/d[%r]/ds[%r]/a[%r]/m[%r]>' % \
			(self.name, self.desired, self.dirty, self.active, self.measured)	

def _updateThermostatCache():			
	tl = models.Thermostat.query.all()
	for t in tl:
		_thermostats[t.hw_id] = Thermostat(t)

def _flushThermostatCache():
	for t in _thermostats.values():
		if t.dirty == True:
			models.Thermostat.query.filter_by(hw_id=t.hw_id).first().desired = t.desired
			t.dirty = False

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
	



