#!/usr/bin/python
import RPi.GPIO as GPIO
import time, sys
from threading import Lock



class SerialGpioOut:
	SHCP_PIN = 16
	DS_PIN = 20
	STCP_PIN = 21
	GPIO_DELAY = 0.001

	def __init__(self, numberOfBytes):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.SHCP_PIN, GPIO.OUT)
		GPIO.setup(self.DS_PIN, GPIO.OUT)
		GPIO.setup(self.STCP_PIN, GPIO.OUT)
		self._numberOfBytes = numberOfBytes
		self._data = bytearray(self._numberOfBytes)
		self._mask = bytearray(self._numberOfBytes)
		self._lock = Lock()
		
	def _getLock(self):
		self._lock.acquire()
		
	def _releaseLock(self):
		self._lock.release()
		
	def _pin2ByteBit(self, pin):
		if pin < 0 or pin >= (self._numberOfBytes * 8): return
		byte = int(pin/8)
		bit = pin-8*byte
		return byte, bit

	def setPinActiveLow(self, pin):
		byte, bit = self._pin2ByteBit(pin)
		self._getLock()
		self._mask[byte] = self._mask[byte] | (1 << bit)
		self._releaseLock()
		print('SPAL', byte, bit, self._mask, self._data)
		
	def setPinActiveHigh(self, pin):
		byte, bit = self._pin2ByteBit(pin)
		self._getLock()
		self._mask[byte] = self._mask[byte] & ((1 << bit) ^ 0xff)
		self._releaseLock()
		print('SPAH', byte, bit, self._mask, self._data)
		
	def setPinHigh(self, pin):
		self.setPinHighSession(pin)
		self.sendData()
		
	def setPinHighSession(self, pin):
		byte, bit = self._pin2ByteBit(pin)
		self._getLock()
		self._data[byte] = self._data[byte] | (1 << bit)
		self._releaseLock()
		print('SPH', byte, bit, self._mask, self._data)
		
	def setPinLowAll(self):
		self._getLock()
		self._data = bytearray(self._numberOfBytes)
		self._releaseLock()
		self.sendData()
		
		
	def setPinLow(self, pin):
		self.setPinLowSession(pin)
		self.sendData()

	def setPinLowSession(self, pin):
		byte, bit = self._pin2ByteBit(pin)
		self._getLock()
		self._data[byte] = self._data[byte] & ((1 << bit) ^ 0xff)
		self._releaseLock()
		print('SPL', byte, bit, self._mask, self._data)

	def flushSession(self):
		self.sendData()

	def sendData(self):
		self._getLock()
		GPIO.output(self.STCP_PIN, GPIO.LOW)
		for d, m in zip(reversed(self._data), reversed(self._mask)):
			mask = 0x80
			print(m, d)
			for i in range(0, 8):
				time.sleep(self.GPIO_DELAY)
				GPIO.output(self.SHCP_PIN, GPIO.LOW)
				level = GPIO.HIGH if (m ^ d) & mask else GPIO.LOW
				GPIO.output(self.DS_PIN, level)
				print ("|  %d %x %x %x" % (1 if level == GPIO.HIGH else 0, d, m, mask))
				time.sleep(self.GPIO_DELAY)
				GPIO.output(self.SHCP_PIN, GPIO.HIGH)
				print (" | %d %x %x %x" % (1 if level == GPIO.HIGH else 0, d, m, mask))
				mask = mask >> 1
		time.sleep(self.GPIO_DELAY)
		GPIO.output(self.STCP_PIN, GPIO.HIGH)
		time.sleep(self.GPIO_DELAY)
		GPIO.output(self.STCP_PIN, GPIO.LOW)
		self._releaseLock()
		

# if not used as a module (standalone), run this test program 
if __name__ == "__main__":
	sdo = SerialGpioOut(2)
	#sdo.sendData(int(sys.argv[1], 0))
	for p in range(0, 16):
		sdo.setPinActiveLow(p)
#	while True:
#		for p in range(0, 8):
#			sdo.setPinHigh(p)
#			time.sleep(0.1)
#		for p in range(0, 8):
#			sdo.setPinLow(p)
#			time.sleep(0.1)
	sdo.setPinLowAll()
	sdo.setPinHigh(0)
	time.sleep(1)
	sdo.setPinLow(0)
	time.sleep(1)	
	for p in range(0, 16):
		sdo.setPinHigh(p)
		time.sleep(0.2)
	for p in range(0, 16):
		sdo.setPinLow(p)
		time.sleep(0.2)
	time.sleep(2)
	sdo.setPinLowAll()

	#sdo.flushSession()	
	
		
