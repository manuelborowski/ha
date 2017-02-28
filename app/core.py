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
	#try:
		heatingCheckCtr = 0
		while True:
			time.sleep(config.CORE_WORKER_DELAY)
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
			heatingCheckCtr += 1
			if heatingCheckCtr > 10:
				heatingCheckCtr = 0
				#if hsCheckSchedule():
					#log.debug("at {} : heating state is : {}".format(datetime.datetime.now(), hsState()))
					#log.debug("goes on/off : {}/{}".format(hsHeatingGoesOn(), hsHeatingGoesOff()))
	#except Exception as e:
		#exceptions at this level are forwarded (email) to the administrator
	#	sendmail.send('Message from Heating Automation', str(e))
			
#class HeatingList:
	#def __init__(self):
		#self.crnt = 0
		#self.lst = []
		
	#def _time2min(self, time):
		##print('_time2min : {}/{}'.format(time, time.weekday() * 1440 + time.hour * 60 + time.minute))
		#return time.weekday() * 1440 + time.hour * 60 + time.minute
		
	#def append(self, item):
		#self.lst.append(item)
		
	#def init(self):
		#minutes  = self._time2min(datetime.datetime.now())
		#last = len(self.lst) - 1
		#if (minutes >= self._time2min(self.lst[last].time)):
			##sunday, after the last time entry and before midnight
			#self.crnt = last
		#else:
			#for i in range(len(self.lst)):
				#if minutes < self._time2min(self.lst[i].time):
					#self.crnt = i - 1
					#break;
			#if self.crnt < 0: self.crnt = last

	#def check(self):
		#if (self.crnt == len(self.lst) - 1) and (datetime.datetime.now().weekday() == 6):
			##sunday, after the last time entry : return if the current day is still sunday
			#return False
		#minutes  = self._time2min(datetime.datetime.now())
		#nxt = self.crnt + 1
		#if nxt == len(self.lst): nxt = 0 #wrap around
		#if minutes > self._time2min(self.lst[nxt].time): #passed a time entry, shift to next time entry
			#self.crnt = nxt
			#return True
		#else:
			#return False
			
	#def state(self):
		#return self.lst[self.crnt].state
		
	#def __repr__(self):
		#return '<crnt/lst : {}/{}>'.format(self.crnt, self.lst)
		
		
#_hsVersion = 0
#_hsList = HeatingList()

#_hsHeatingGoesOn = False
#_hsHeatingGoesOff = False

#def hsCheckSchedule():
	#global _hsHeatingGoesOn
	#global _hsHeatingGoesOff
	#if _hsVersion != cache.getHeatingScheduleVersion():
		##There is an update in the heating schedule, check it out
		#_updateHeatingList()
		##print('list update : {}'.format(_hsList))
		#return True
	##print('list check : {}'.format(_hsList))
	#if _hsList.check():
		#_hsHeatingGoesOn = _hsList.state()
		#_hsHeatingGoesOff = not _hsHeatingGoesOn
		#return True
	#return False

	
#def hsState():
	#return _hsList.state()
	
#def hsHeatingGoesOn():
	#global _hsHeatingGoesOn
	#state = _hsHeatingGoesOn
	#_hsHeatingGoesOn = False
	#return state
	
#def hsHeatingGoesOff():
	#global _hsHeatingGoesOff
	#state = _hsHeatingGoesOff
	#_hsHeatingGoesOff = False
	#return state
		
#def _updateHeatingList():
	#global _hsList
	#global _hsVersion
	#global _hsHeatingGoesOn
	#global _hsHeatingGoesOff
	#_hsVersion = cache.getHeatingScheduleVersion()
	##create a local list.  This is timeconsuming, but happens only when the original
	##schedule list is changed, which does not happen often...
	#hsl = cache.getHeatingScheduleList()
	#_hsList = HeatingList()
	#for hs in hsl:
		#for t in hs.timeList:
			#_hsList.append(t)
	#_hsList.init()
	#_hsHeatingGoesOn = _hsList.state()
	#_hsHeatingGoesOff = not _hsHeatingGoesOn
	
