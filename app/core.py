import threading, time, logging
from app import cache


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
ch = logging.FileHandler("test.log", 'a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

log.debug("starting")


def init():
	print("starting core")
	coreThread = threading.Thread(target=worker)
	coreThread.start()
	
	
def worker():
	while True:
		time.sleep(1)
		log.debug("inside worker")
		print("i'm the worker")
		tl = cache.getThermostatList()
		for t in tl:
			if t.hw_id=='th_yannick':
				with open(t.hw_id) as f:t.measured=int(f.read())
			else:
				t.measured=15
			if t.enabled: 
				t.active = True if t.measured < t.desired else False
			else:
				t.active = False
		
	
