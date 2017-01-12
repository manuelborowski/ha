import threading, time, logging
from app import cache
from app import onewirethermo as owt


log = logging.getLogger(__name__)

def init():
	log.info("starting")
	coreThread = threading.Thread(target=worker)
	coreThread.start()
	tl = cache.getThermostatList()
	for t in tl:
		typeId = t.hw_id.split(":")
		if typeId[0] =='w1':	#one wire thermometer
			log.info(owt.addThermometer(typeId[1]))

	
		
def worker():
	while True:
		time.sleep(1)
		#log.debug("tick...")
		tl = cache.getThermostatList()
		for t in tl:
			typeId = t.hw_id.split(":")
			if typeId[0] =='w1':	#one wire thermometer
				t.measured = owt.getValue(typeId[1])
			else:
				t.measured=15
			if t.enabled: 
				t.active = True if t.measured < t.desired else False
			else:
				t.active = False
		
	
