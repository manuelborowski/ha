import threading, time, logging, datetime
import config
from app import cache
#from app import onewirethermo as owt
#from app import zwave
#from app import sendmail
#from app import do


log = logging.getLogger(__name__)


def init():
	log.info("initializing")

def start():
	log.info("starting")
	wrk = threading.Thread(target=worker)
	wrk.setDaemon(True)
	wrk.start()

def worker():
	while True:
		_checkSchedule()
		time.sleep(config.SCHEDULE_DELAY)

			
class HeatingList:
	def __init__(self):
		self.crnt = 0
		self.lst = []
		
	def _time2min(self, time):
		#print('_time2min : {}/{}'.format(time, time.weekday() * 1440 + time.hour * 60 + time.minute))
		return time.weekday() * 1440 + time.hour * 60 + time.minute
		
	def extend(self, lst):
		self.lst.extend(lst)
		
	def init(self):
		minutes  = self._time2min(datetime.datetime.now())
		last = len(self.lst) - 1
		if minutes >= self.lst[last].val:
			#sunday, after the last time entry and before midnight
			self.crnt = last
		else:
			for i in range(len(self.lst)):
				if minutes < self.lst[i].val:
					self.crnt = i - 1
					break;
			if self.crnt < 0: self.crnt = last

	def check(self):
		if (self.crnt == len(self.lst) - 1) and (datetime.datetime.now().weekday() == 6):
			#sunday, after the last time entry : return if the current day is still sunday
			return False
		minutes  = self._time2min(datetime.datetime.now())
		nxt = self.crnt + 1
		if nxt == len(self.lst): nxt = 0 #wrap around
		if minutes >= self.lst[nxt].val: #passed a time entry, shift to next time entry
			self.crnt = nxt
			return True
		else:
			return False
			
	def state(self):
		return (self.crnt % 2) == 0
		
	def __repr__(self):
		return '<crnt/lst : {}/{}>'.format(self.crnt, self.lst)
		
		
_hsVersion = 0
_hsList = HeatingList()

_hsHeatingGoesOn = False
_hsHeatingGoesOff = False

def _checkSchedule():
	global _hsHeatingGoesOn
	global _hsHeatingGoesOff
	if _hsVersion != cache.getHeatingScheduleVersion():
		#There is an update in the heating schedule, check it out
		_updateHeatingList()
		#print('list update : {}'.format(_hsList))
		_hsHeatingGoesOn = _hsList.state()
		_hsHeatingGoesOff = not _hsHeatingGoesOn
		return True
	#print('list check : {}'.format(_hsList))
	if _hsList.check():
		_hsHeatingGoesOn = _hsList.state()
		_hsHeatingGoesOff = not _hsHeatingGoesOn
		return True
	return False

	
def state():
	return _hsList.state()
	
def heatingGoesOn():
	global _hsHeatingGoesOn
	state = _hsHeatingGoesOn
	_hsHeatingGoesOn = False
	return state
	
def heatingGoesOff():
	global _hsHeatingGoesOff
	state = _hsHeatingGoesOff
	_hsHeatingGoesOff = False
	return state
		
def _updateHeatingList():
	global _hsList
	global _hsVersion
	_hsVersion = cache.getHeatingScheduleVersion()
	_hsList = HeatingList()
	_hsList.extend(cache.getHeatingScheduleList())
	#for hs in hsl:
		#for t in hs.timeList:
			#_hsList.append(t)
	_hsList.init()
	log.debug('Heating list update : {}/{}'.format(_hsVersion, _hsList))
	
