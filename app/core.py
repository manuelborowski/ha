import threading, time, logging, datetime
import config
from app import cache
from app import onewirethermo as owt
from app import zwave
from app import sendmail
from app import do
from app import schedule


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
	#subscribe a number of rooms on a heating schedule state change
	schedule.subscribeStateChange('eetkamer', stateChangeCb, 1)
	schedule.subscribeStateChange('badkamer', stateChangeCb, 2)


def stateChangeCb(room, dtime):
	log.debug('State change for room/dtime : {}/{}'.format(room, dtime))

	
		
def worker():
	#try:
		while True:
			time.sleep(config.CORE_WORKER_DELAY)
			tl = cache.getThermostatList()
			# check the heating schedule.
			if schedule.heatingGoesOn():
				log.info('heating goes ON')
				#for t in tl:
					#if t.scheduled: t.enabled = True
			if schedule.heatingGoesOff():
				log.info('heating goes OFF')
				#for t in tl:
					#t.enabled = False
			# update the thermometer readings
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
					
				#depending on the measured temperature, the desired temperature and the state
				#of the thermometer (enabled or not), activate the heating.
				#if t.enabled: 
					#t.active = True if t.measured < t.desired else False
				#else:
					#t.active = False
	#except Exception as e:
		#exceptions at this level are forwarded (email) to the administrator
	#	sendmail.send('Message from Heating Automation', str(e))
	
			
