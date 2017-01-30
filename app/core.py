import threading, time, logging
from app import cache
from app import onewirethermo as owt
from app import zwave


log = logging.getLogger(__name__)

def start():
	log.info("starting")
	coreThread = threading.Thread(target=worker)
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
		time.sleep(1)
		#log.debug("tick...")
		tl = cache.getThermostatList()
		for t in tl:
			typeId = t.hw_id.split("_")
			if typeId[0] =='w1':	#one wire thermometer
				t.measured = round(owt.getValue(typeId[1]), 1)
			elif typeId[0] == 'zw': #zwave thermometer
				t.measured = round(zwave.getValue(typeId[1]), 1)
				log.info("sensor {} : battery level {} %".format(typeId[1], zwave.getBatteryLevel(typeId[1])))
			elif typeId[0] == 'dummy': #dummy value
				t.measured = round(float(typeId[1]), 1)
			else:
				t.measured=15
			if t.enabled: 
				t.active = True if t.measured < t.desired else False
			else:
				t.active = False
		
	
