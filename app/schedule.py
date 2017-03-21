import threading, time, logging, datetime
import config
from app import cache

log = logging.getLogger(__name__)

class HeatingList:
	class StateChangeCB:
		def __init__(self, id, cb, dtime, level):
			self.id = id
			self.cb = cb
			self.dtime = dtime
			self.level = level
			self.active = True
			
		def __repr__(self):
			return '<i/dt/s/a : {}/{}/{}/{}>'.format(self.id, self.dtime, self.level, self.active)

	def __init__(self):
		self.crnt = 0
		self.lst = []
		self.cbDict = {}
		
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
		minutes  = self._time2min(datetime.datetime.now())
		if (self.crnt == len(self.lst) - 1) and (datetime.datetime.now().weekday() == 6):
			#check the callbacks.  Adjust the 'next' time because of the wrap around...
			self._checkCb(minutes, self.lst[0].val + 1440 * 7)
			#sunday, after the last time entry : return if the current day is still sunday
			return False
		nxt = self.crnt + 1
		if nxt == len(self.lst): nxt = 0 #wrap around
		self._checkCb(minutes, self.lst[nxt].val)
		if minutes >= self.lst[nxt].val: #passed a time entry, shift to next time entry
			self.crnt = nxt
			self._resetCb()
			return True
		else:
			return False
			
	def state(self):
		return (self.crnt % 2) == 0
		
	def _checkCb(self, now, nxt):
		#log.debug('check callback : now/nxt : {}/{}'.format(now, nxt))
		for cb in self.cbDict.values():
			if cb.active and now >= (nxt - cb.dtime) and self.state() != cb.level:
				cb.active = False
				cb.cb(cb.id, cb.dtime, cb.level)
	def _resetCb(self):
		log.debug('reset callback')
		for cb in self.cbDict.values():
			if not cb.active and self.state() != cb.level:
				cb.active = True
		
	def addStateChangeCb(self, id, cb, dtime, level):
		self.cbDict[id] = self.StateChangeCB(id, cb, dtime, level)
		log.info('added statechange callback : {}'.format(self.cbDict[id]))
		
	def __repr__(self):
		return '<crnt/lst : {}/{}>'.format(self.crnt, self.lst)
		


_hsVersion = 0
_hsList = HeatingList()

def init():
	log.info("initializing")
	_updateHeatingList()

def start():
	log.info("starting")
	wrk = threading.Thread(target=worker)
	wrk.setDaemon(True)
	wrk.start()

def worker():
	time.sleep(62 - datetime.datetime.now().second)
	while True:
		_checkSchedule()
		time.sleep(config.SCHEDULE_DELAY)


def subscribeHeatingChange(id, cb, dtime, level):
	_hsList.addStateChangeCb(id, cb, dtime, level)
			
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
	
