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

def init():
	global _numberOfBytes
	global _mask
	global _data
	global _lock
	log.info("intializing...")
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(SHCP_PIN, GPIO.OUT)
	GPIO.setup(DS_PIN, GPIO.OUT)
	GPIO.setup(STCP_PIN, GPIO.OUT)
	_numberOfBytes = config.DO_NBR_OF_BYTES
	_data = bytearray(_numberOfBytes)
	_mask = bytearray(_numberOfBytes)
	_lock = Lock()
	
def start():
	log.info("starting...")
	#the 16-relais module uses negative logic : input low -> releais active
	for p in range(0, _numberOfBytes * 8):
		setPinActiveLow(p)
	setPinLowAll()
	time.sleep(1)
	for p in range(0, _numberOfBytes * 8):
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
	
def _pin2ByteBit(pin):
	if pin < 0 or pin >= (_numberOfBytes * 8): return
	byte = int(pin/8)
	bit = pin-8*byte
	return byte, bit

def setPinActiveLow(pin):
	global _mask
	byte, bit = _pin2ByteBit(pin)
	_getLock()
	_mask[byte] = _mask[byte] | (1 << bit)
	_releaseLock()
	log.info('SetPinActiveLow {} {} {} {}'.format(byte, bit, _mask, _data))
	
def setPinActiveHigh(pin):
	global _mask
	byte, bit = _pin2ByteBit(pin)
	_getLock()
	_mask[byte] = _mask[byte] & ((1 << bit) ^ 0xff)
	_releaseLock()
	log.info('SetPinActiveHigh {} {} {} {}'.format(byte, bit, _mask, _data))
	
def setPinHigh(pin):
	pin = _name2int(pin)
	setPinHighSession(pin)
	_sendData()
	
def setPinHighSession(pin):
	global _data
	byte, bit = _pin2ByteBit(pin)
	_getLock()
	_data[byte] = _data[byte] | (1 << bit)
	_releaseLock()
	#print('SPH', byte, bit, _mask, _data)
	
def setPinLowAll():
	global _data
	_getLock()
	_data = bytearray(_numberOfBytes)
	_releaseLock()
	_sendData()
	
def setPinLow(pin):
	setPinLowSession(pin)
	_sendData()

def setPinLowSession(pin):
	global _data
	byte, bit = _pin2ByteBit(pin)
	_getLock()
	_data[byte] = _data[byte] & ((1 << bit) ^ 0xff)
	_releaseLock()
	#print('SPL', byte, bit, _mask, _data)

def flushSession(self):
	self._sendData()

def _sendData():
	_getLock()
	GPIO.output(STCP_PIN, GPIO.LOW)
	for d, m in zip(reversed(_data), reversed(_mask)):
		mask = 0x80
		#print(m, d)
		for i in range(0, 8):
			time.sleep(GPIO_DELAY)
			GPIO.output(SHCP_PIN, GPIO.LOW)
			level = GPIO.HIGH if (m ^ d) & mask else GPIO.LOW
			GPIO.output(DS_PIN, level)
			#print ("|  %d %x %x %x" % (1 if level == GPIO.HIGH else 0, d, m, mask))
			time.sleep(GPIO_DELAY)
			GPIO.output(SHCP_PIN, GPIO.HIGH)
			#print (" | %d %x %x %x" % (1 if level == GPIO.HIGH else 0, d, m, mask))
			mask = mask >> 1
	time.sleep(GPIO_DELAY)
	GPIO.output(STCP_PIN, GPIO.HIGH)
	time.sleep(GPIO_DELAY)
	GPIO.output(STCP_PIN, GPIO.LOW)
	_releaseLock()
		

## if not used as a module (standalone), run this test program 
#if __name__ == "__main__":
	#config.DO_NBR_OF_BYTES=2
	#init()
	##sdo._sendData(int(sys.argv[1], 0))
	#for p in range(0, 16):
		#setPinActiveLow(p)
##	while True:
##		for p in range(0, 8):
##			sdo.setPinHigh(p)
##			time.sleep(0.1)
##		for p in range(0, 8):
##			sdo.setPinLow(p)
##			time.sleep(0.1)
	#setPinLowAll()
	#setPinHigh(0)
	#time.sleep(1)
	#setPinLow(0)
	#time.sleep(1)	
	#for p in range(0, 16):
		#setPinHigh(p)
		#time.sleep(0.2)
	#for p in range(0, 16):
		#setPinLow(p)
		#time.sleep(0.2)
	#time.sleep(2)
	#setPinLowAll()

	##sdo.flushSession()	
	
		
