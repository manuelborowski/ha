import threading, time
from app import cache


def init():
	print("starting core")
	coreThread = threading.Thread(target=worker)
	coreThread.start()
	
	
def worker():
	while False:
		time.sleep(1)
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
		
	
