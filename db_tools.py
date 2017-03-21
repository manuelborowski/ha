#!virtual/bin/python
import config
config.DB_TOOLS = True
from app import models, db

class Room:
	def __init__(self, name, scheduled, thermal_mass, thermal_loss, floorheating_mode):
		self.name = name
		self.scheduled = scheduled
		self.thermal_mass = thermal_mass
		self.thermal_loss = thermal_loss
		self.floorheating_mode = floorheating_mode
		
_rooms = [Room('yannick', False, 500, 30, 'NON_PRIORITY'),
			Room('renee', False, 500, 30, 'PRIORITY'),
			Room('badkamer', True, 500, 30, 'FORCE'),
		]

class Thermostat:
	def __init__(self, name, hw_id, min, max, desired, type, room_id):
		self.name = name
		self.hw_id = hw_id
		self.min = min
		self.max = max
		self.desired = desired
		self.type = type
		self.room_id = room_id
		
_thermostats = [Thermostat('yannick', 'zw_yannick', 10, 30, 20, 'RADIATOR', 'yannick'),
				Thermostat('renee', 'zw_renee', 10, 30, 20, 'RADIATOR', 'renee'),
				Thermostat('badkamer_ra', 'w1_28-031685468eff', 10, 30, 20, 'RADIATOR', 'badkamer'),
				Thermostat('badkamer_vv', 'w1_28-0316855a42ff', 10, 30, 20, 'FLOOR', 'badkamer'),
				]

_heatingschedule = [
	#monday
	['06:00',
	'08:00',
	'16:00',
	'22:00'],
	#tuesday
	['06:00',
	'08:00',
	'16:00',
	'22:00'],
	#wednesday
	['06:00',
	'08:00',
	'12:00',
	'22:00'],
	#thursday
	['06:00',
	'08:00',
	'16:00',
	'22:00'],
	#friday
	['06:00',
	'08:00',
	'16:00',
	'22:00'],
	#saturday
	['07:00',
	'08:00',
	'08:00',
	'22:00'],
	#sunday
	['07:00',
	'08:00',
	'08:00',
	'22:00'],
]
print('start db tools')


def newRoom(r):
	try:
		r = models.Room(name=r.name, scheduled=r.scheduled, thermal_mass=r.thermal_mass, \
						thermal_loss=r.thermal_loss, floorheating_mode=r.floorheating_mode)
		db.session.add(r)
		db.session.commit()
		print('added room {}'.format(r.name))
	except Exception as e:
		db.session.rollback()
		#print(str(e))
		print('newRoom : {} bestaat al'.format(r.name))
	
def newThermostat(t):
	try:
		t = models.Thermostat(name=t.name, hw_id=t.hw_id, \
								min=t.min, max=t.max, desired=t.desired, type=t.type)
		db.session.add(t)	
		db.session.commit()
		print('added thermostat {}'.format(t.name))
	except Exception as e:
		db.session.rollback()
		print(str(e))
		print('newThermostat : {} bestaat al'.format(t.name))


def linkRoomToThermostate(t):
	try:
		r = models.Room.query.filter(models.Room.name==t.room_id).first()
		t = models.Thermostat.query.filter(models.Thermostat.name==t.name).first()
		r.thermostats.append(t)
		db.session.commit()
		print('linked thermostat to room {}'.format(t.name))
	except Exception as e:
		print(str(e))
		db.session.rollback()
		print('could not link thermostat to room {}.  Already linked?'.format(t.name))
		
		
def newSchedule(day, time):
	try:
		stime = time.split(':')
		minutes = int(stime[0]) * 60 + int(stime[1])
		h = models.HeatingSchedule(time=day * 1440 + minutes)
		db.session.add(h)	
		db.session.commit()
		print('added day/time {}/{}'.format(day,time))
	except Exception as e:
		db.session.rollback()
		print(str(e))
		print('day/time : {}/{} bestaat al'.format(day, time))
		
#start...

def fillTables():
	for r in _rooms:
		newRoom(r)
		
	for t in _thermostats:
		newThermostat(t)
		
	for t in _thermostats:
		linkRoomToThermostate(t)
		
	for i, d in enumerate(_heatingschedule):
		for t in d:
				newSchedule(i, t)

def dropTables():
	meta = db.metadata
	for table in reversed(meta.sorted_tables):
		print('Clear table %s' % table)	
		db.session.execute(table.delete())
	db.session.commit()


dropTables()
fillTables()

print('stop db tools')
