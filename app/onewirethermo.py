#!/usr/bin/python

from os import path
import threading, time
import logging

log = logging.getLogger(__name__)

'''
	Store the themometers in a dictionary.
	Poll the thermoters on a regular interval and store in a cache
	Users read the cache, not from the actual thermometer
'''

class SerialValue:
	def __init__(self, serial, value):
		self.serial = serial
		self.value = value
	

_thermometers = {}

def init():
	log.info("starting...")
	_thermoThread = threading.Thread(target=_worker)
	_thermoThread.start()

def _worker():
	global _thermometers
	while True:
		for k in _thermometers.keys():
			_thermometers[k].value = _getValue(_thermometers[k].serial)
		time.sleep(2)
		

def _getSysDevice(serial):
	return '/sys/bus/w1/devices/' + serial + '/w1_slave'
	
def _getValue(serial):
	try:
		with open(_getSysDevice(serial), 'r') as f: data = f.read()
		return int(data.split('t=')[1])/1000
	except Exception as e:
		print(e)
		return 0
	
	
def getValue(name):
	try:
		return _thermometers[name].value
	except Exception as e:
		print(e)
		return 0
	
def addThermometer(serial, name):
	global _thermometers
	if path.isfile(_getSysDevice(serial)):
		_thermometers[name] = SerialValue(serial, _getValue(serial))
		return "ok"
	else:
		return serial + " : device not found"


