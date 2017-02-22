#!/usr/bin/python
import RPi.GPIO as GPIO
import time, sys
from threading import Lock

import threading, time, datetime
import logging, sys
import config

log = logging.getLogger(__name__)

SHCP_PIN = 16
DS_PIN = 20
STCP_PIN = 21
GPIO_DELAY = 0.0001

class Pin:
	def __init__(self):
		self.value = False
		self.inverse = False
		self.name = ""
		
	def __repr__(self):
		return('{}/{}/{}'.format(self.name, self.value, self.inverse))

def init():
	global _numberOfPins
	global _pins
	global _lock
	log.info("intializing...")
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(SHCP_PIN, GPIO.OUT)
	GPIO.setup(DS_PIN, GPIO.OUT)
	GPIO.setup(STCP_PIN, GPIO.OUT)
	_numberOfPins = config.DO_NBR_OF_BYTES * 8
	_pins = [Pin() for _ in range(_numberOfPins)]
	#if a name exists for the pin, add it...
	try:
		for k,v in config.DO_OUTPUTS.items():
			_pins[v].name = k
	except IndexError:
		log.error('{} : index of pin is out of range : {}/{}'.format(__file__, v, k))
		
	_lock = Lock()
	
def start():
	log.info("starting...")
	#the 16-relais module uses negative logic : input low -> releais active
	for p in range(0, _numberOfPins):
		setPinActiveLow(p)
	setPinLowAll()
	time.sleep(1)
	for p in range(0, _numberOfPins):
		setPinHigh(p)
		time.sleep(0.1)
	time.sleep(1)
	setPinLowAll()
	
def _getLock():
	_lock.acquire()
	
def _releaseLock():
	_lock.release()
	
def _name2int(nameOrPin):
	#if the parameter is a pin, return the pin, else use lookup table to translate name
	#to pin
	if isinstance(nameOrPin, int): return nameOrPin
	try:
		pin = config.DO_OUTPUTS[nameOrPin]
		return pin
	except Exception as e:
		raise ValueError('{}: {} : "{}" is not a valid output pin name'.format(__file__, sys._getframe().f_code.co_name, nameOrPin))
	
def setPinActiveLow(pin):
	_name2int(pin)
	_getLock()
	_pins[pin].inverse = True
	_releaseLock()
	log.info('SetPinActiveLow {}'.format(pin))
	
def setPinActiveHigh(pin):
	_name2int(pin)
	_getLock()
	_pins[pin].inverse = False
	_releaseLock()
	log.info('SetPinActiveHigh {}'.format(pin))
	
def setPinHigh(pin):
	setPinHighSession(pin)
	_sendData()
	
def setPinHighSession(pin):
	pin = _name2int(pin)
	_getLock()
	_pins[pin].value = True
	_releaseLock()
	#print('SPH', byte, bit, _mask, _pins)
	
def setPinLowAll():
	_getLock()
	for p in _pins:
		p.value = False
	_releaseLock()
	_sendData()
	
def setPinLow(pin):
	setPinLowSession(pin)
	_sendData()

def setPinLowSession(pin):
	pin = _name2int(pin)
	_getLock()
	_pins[pin].value = False
	_releaseLock()
	#print('SPL', byte, bit, _mask, _pins)
	
def getPinValue(pin):
	pin = _name2int(pin)
	return _pins[pin].value
	
def getPinList():
	return _pins

def flushSession(self):
	self._sendData()

def _sendData():
	_getLock()
	GPIO.output(STCP_PIN, GPIO.LOW)	#store clock low
	for p in _pins[::-1]:	#reverse list
		time.sleep(GPIO_DELAY)
		GPIO.output(SHCP_PIN, GPIO.LOW)	#shift clock low
		level = p.value != p.inverse
		GPIO.output(DS_PIN, level)	#data strobe
		#print ("|  %d %x %x %x" % (1 if level == GPIO.HIGH else 0, d, m, mask))
		time.sleep(GPIO_DELAY)
		GPIO.output(SHCP_PIN, GPIO.HIGH)	#shift clock high : sample data strobe
		#print (" | %d %x %x %x" % (1 if level == GPIO.HIGH else 0, d, m, mask))
	time.sleep(GPIO_DELAY)
	GPIO.output(STCP_PIN, GPIO.HIGH)	#store clock high : data to pins
	time.sleep(GPIO_DELAY)
	GPIO.output(STCP_PIN, GPIO.LOW)	#store clock low
	_releaseLock()
		
