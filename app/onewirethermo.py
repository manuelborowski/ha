#!/usr/bin/python

from os import path
import threading, time, datetime
import logging

log = logging.getLogger(__name__)

'''
	Store the themometers in a dictionary.
	Poll the thermoters on a regular interval and store in a cache
	Users read the cache, not from the actual thermometer
'''


_thermometers = {}

def init():
	log.info("starting...")
	_thermoThread = threading.Thread(target=_worker)
	_thermoThread.start()

def _worker():
	while True:
		for k in _thermometers.keys():
			_thermometers[k] = _getValue(k)
		time.sleep(2)
		

def _getSysDevice(serial):
	return '/sys/bus/w1/devices/' + serial + '/w1_slave'
	
def _getValue(serial):
	try:
		#print("start get thermo " + str(datetime.datetime.now()))
		with open(_getSysDevice(serial), 'r') as f: data = f.read()
		#print("stop get thermo " + str(datetime.datetime.now()))
		return int(data.split('t=')[1])/1000
	except Exception as e:
		print(e)
		return 0
	
	
def getValue(serial):
	try:
		return _thermometers[serial]
	except Exception as e:
		print(e)
		return 0
	
def addThermometer(serial):
	if path.isfile(_getSysDevice(serial)):
		log.info("adding onewire thermometer %s", serial)
		_thermometers[serial] = _getValue(serial)
		return "ok"
	else:
		return serial + " : device not found"


