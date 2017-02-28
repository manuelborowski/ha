#!virtual/bin/python
from app import models, db

_rooms = ['yannick', 'renee']

class Thermostat:
	def __init__(self, name, hw_id, enabled, min, max, desired, scheduled, room_id):
		self.name = name
		self.hw_id = hw_id
		self.enabled = enabled
		self.min = min
		self.max = max
		self.desired = desired
		self.scheduled = scheduled
		self.room_id = room_id
		
_thermostats = [Thermostat('yannick', 'zw_yannick', True, 10, 30, 20, False, 'yannick'),
				Thermostat('renee', 'zw_renee', True, 10, 30, 20, False, 'renee')
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


def newRoom(name):
	try:
		r = models.Room(name=name)
		db.session.add(r)
		db.session.commit()
		print('added room {}'.format(name))
	except Exception as e:
		db.session.rollback()
		#print(str(e))
		print('newRoom : {} bestaat al'.format(name))
	
def newThermostat(t):
	try:
		t = models.Thermostat(name=t.name, hw_id=t.hw_id, enabled=t.enabled, \
								min=t.min, max=t.max, desired=t.desired, scheduled=t.scheduled)
		db.session.add(t)	
		db.session.commit()
		print('added thermostat {}'.format(t.name))
	except Exception as e:
		db.session.rollback()
		#print(str(e))
		print('newThermostat : {} bestaat al'.format(t.name))


def linkRoomToThermostate(name):
	try:
		r = models.Room.query.filter(models.Room.name==name).first()
		t = models.Thermostat.query.filter(models.Thermostat.name==name).first()
		r.thermostats.append(t)
		db.session.commit()
		print('linked thermostat to room {}'.format(name))
	except Exception as e:
		db.session.rollback()
		print('could not link thermostat to room {}.  Already linked?'.format(name))
		
		
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
		linkRoomToThermostate(t.room_id)
		
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
