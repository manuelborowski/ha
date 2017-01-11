#!/usr/bin/python

from os import path
import threading, time
import logging, logging.handlers

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
ch = logging.FileHandler("../test.log", 'a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
ch2 = logging.handlers.SMTPHandler("smtp.gmail.com", "emmanuel.borowski@gmail.com", 
							"manuel.borowski@campussintursula.be", 
							"logging van het verwarmingstoestel", 
							("emmanuel.borowski@gmail.com", "ManGoo28UGle8El69"))
ch2.setLevel(logging.CRITICAL)
log.addHandler(ch)
log.addHandler(ch2)

log.debug("starting")
log.critical("eens proberen een mailtje te sturen")

class OneWireThermo:
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
	
	def __init__(self):
		print("starting onewirethermo")
		_thermoThread = threading.Thread(target=self._worker)
		_thermoThread.start()
	
	def _worker(self):
		while True:
			log.debug("inside worker")
			for k in self._thermometers.keys():
				self._thermometers[k].value = self._getValue(self._thermometers[k].serial)
			time.sleep(2)
			
	
	def _getSysDevice(self, serial):
		return '/sys/bus/w1/devices/' + serial + '/w1_slave'
		
	def _getValue(self, serial):
		try:
			with open(self._getSysDevice(serial), 'r') as f: data = f.read()
			return int(data.split('t=')[1])/1000
		except Exception as e:
			print(e)
			return 0
		
		
	def getValue(self, name):
		try:
			return self._thermometers[name].value
		except Exception as e:
			print(e)
			return 0
		
	def addThermometer(self, serial, name):
		
		if path.isfile(self._getSysDevice(serial)):
			self._thermometers[name] = self.SerialValue(serial, self._getValue(serial))
			return "ok"
		else:
			return serial + " : device not found"


# if not used as a module (standalone), run this test program 
if __name__ == "__main__":
	owt = OneWireThermo()
	
	print(owt.addThermometer('28-03168553fbff', 'th_yannick'))
	print(owt.addThermometer('28-0516866ca3ff', 'th_renee'))
	print(owt._getValue('28-03168553fbff'))
	while True:
		print('%s : %f ' % ('th_yannick', owt.getValue('th_yannick')))
		print('%s : %f ' % ('th_renee', owt.getValue('th_renee')))
		time.sleep(1)
