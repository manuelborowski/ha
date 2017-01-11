import threading, time, logging
from app import cache
from app import onewirethermo as owt


log = logging.getLogger(__name__)

def init():
	log.info("starting")
	coreThread = threading.Thread(target=worker)
	coreThread.start()
	log.info(owt.addThermometer('28-03168553fbff', 'th_yannick'))
	log.info(owt.addThermometer('28-0516866ca3ff', 'th_renee'))

	
		
def worker():
	while True:
		time.sleep(1)
		log.debug("tick...")
		tl = cache.getThermostatList()
		for t in tl:
			if t.hw_id=='th_yannick':
				t.measured = owt.getValue('th_yannick')
				#with open(t.hw_id) as f:t.measured=int(f.read())
			elif t.hw_id =='th_renee' :
				t.measured = owt.getValue('th_renee')
				
			else:
				t.measured=15
			if t.enabled: 
				t.active = True if t.measured < t.desired else False
			else:
				t.active = False
		
	
