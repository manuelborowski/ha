import threading, time, logging
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
		time.sleep(1)
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
			do.setPinHigh("test")
		except Exception as e:
			#exceptions at this level are forwarded (email) to the administrator
			sendmail.send('exception received in core.py', str(e))
		
	
