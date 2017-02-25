import threading, time, logging, datetime
import config
from app import cache
from app import onewirethermo as owt
from app import zwave
from app import sendmail
from app import do


log = logging.getLogger(__name__)

def start():
	log.info("starting")
	coreThread = threading.Thread(target=worker)
	coreThread.setDaemon(True)
	coreThread.start()
	tl = cache.getThermostatList()
	for t in tl:
		typeId = t.hw_id.split("_")
		if typeId[0] =='w1':	#one wire thermometer
			log.info(owt.addThermometer(typeId[1]))
		elif typeId[0] =='zw':	#zwave thermometer
			log.info(zwave.addThermometer(typeId[1]))

	
		
def worker():
	while True:
		time.sleep(config.CORE_WORKER_DELAY)
		try:
			tl = cache.getThermostatList()
			for t in tl:
				typeId = t.hw_id.split("_")
				if typeId[0] =='w1':	#one wire thermometer
					t.measured = round(owt.getValue(typeId[1]), 1)
				elif typeId[0] == 'zw': #zwave thermometer
					t.measured = round(zwave.getValue(typeId[1]), 1)
					t.batLevel = zwave.getBatteryLevel(typeId[1])	
					#log.info("sensor {} : battery level {} %".format(typeId[1], zwave.getBatteryLevel(typeId[1])))
				elif typeId[0] == 'dummy': #dummy value
					t.measured = round(float(typeId[1]), 1)
				else:
					t.measured=15
				if t.enabled: 
					t.active = True if t.measured < t.desired else False
				else:
					t.active = False
		except Exception as e:
			#exceptions at this level are forwarded (email) to the administrator
			sendmail.send('Message from Heating Automation', str(e))
		
_hsVersion = 0
_hsList = []
_hsNextListIndex = -1
_hsNextMoment = 0
_hsPreviousState = False
_hsState = False
_hsHeatingGoesOn = False
_hsHeatingGoesOff = False

def _checkHeatingSchedule():
	if _hsVersion != cache.getHeatingSchedule2Version():
		#There is an update in the heating schedule, check it out
		_updateHeatingData()
		return
		
	now = datetime.datetime.now()
	if (now.dayofweek() * 1440 + now.hour * 60 + now.minute) > _hsNextMoment:
			
		
def _updateHeatingData():
	global _hsList
	global _hsNextListIndex
	global _hsVersion
	global _hsNextMoment
	global _hsState
	global _hsPreviousState
	global _hsHeatingGoesOn
	global _hsHeatingGoesOff
	
	_hsVersion = cache.getHeatingSchedule2Version()
	now = datetime.datetime.now()
	#delta time, in minutes, from monday 00:00
	currentMinutes = now.dayofweek() * 1440 + now.hour * 60 + now.minute
	hsl = cache.getHeatingSchedule2List()
	
	#create a local list.  This is timeconsuming, but happens only when the original
	#schedule list is changed, which does not happen often...
	_hsList = []
	for hs in hsl:
		for t in hs.timeList:
			_hsList.append(t)
	
	found = False
	for i, t in enumerate(_hsList):
		scheduleMinutes = t.time.dayofweek() * 1440 + t.time.hour * 60 + t.time.minute
		if scheduleMinutes > currentMinutes:
			_hsNextListIndex = 
			_hsNextMoment = scheduleMinutes
			_hsState = not t.state
			_hsHeatingGoesOn = _hsState
			_hsHeatingGoesOff = not _hsState
			_hsPreviousState = not _hsState
			found = True
	if not found:
		#corner case : current time is sunday evening, after last entry in timeList
		#Use first entry in timeList of monday
		t = hsl[0].timeList[0]
		_hsNextMoment = t.time.dayofweek() * 1440 + t.time.hour * 60 + t.time.minute
		_hsState = not t.state
		_hsHeatingGoesOn = _hsState
		_hsHeatingGoesOff = not _hsState
		_hsPreviousState = not _hsState
		found = True
			
