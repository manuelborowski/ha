#!/usr/bin/python

from os import path
import threading, time, datetime
from threading import Lock
import logging
import config

log = logging.getLogger(__name__)

'''
	Store the themometers in a dictionary.
	Pol the thermoters on a regular interval and store in a cache
	Users read the cache, not from the actual thermometer
'''


_thermometers = {}
_addThermometers = {}
_lock = Lock()

def _getLock():
	_lock.acquire()

def _releaseLock():
	_lock.release()
	

def start():
	log.info("starting...")
	_thermoThread = threading.Thread(target=_worker)
	_thermoThread.start()

def _worker():
	global _addThermometers
	global _thermometers
	log.info("start worker...")
	while True:
		for k in _thermometers.keys():
			_thermometers[k] = _getValue(k)
		if _addThermometers:
			_getLock()
			_thermometers.update(_addThermometers)
			_addThermometers = {}
			_releaseLock()
		#time.sleep(2)
	
		

def _getSysDevice(serial):
	return '/sys/bus/w1/devices/' + serial + '/w1_slave'
	
def _getValue(serial):
	try:
		with open(_getSysDevice(serial), 'r') as f: data = f.read()
		return int(data.split('t=')[1])/1000
	except Exception as e:
		print(e)
		return 0
	
	
def getValue(serial):
	try:
		return _thermometers[serial]
	except Exception as e:
		#print("getValue " + str(e))
		return config.INVALID_TEMP
	
def addThermometer(serial):
	global _addThermometers
	if path.isfile(_getSysDevice(serial)):
		log.info("adding onewire thermometer %s", serial)
		_getLock()
		_addThermometers[serial] = _getValue(serial)
		_releaseLock()
		return "ok"
	else:
		return serial + " : device not found"


