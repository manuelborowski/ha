#!/usr/bin/python
from os import path

class OneWireThermo:
	
	def addThermometer(self, serial, name):
		
		if path.isfile('/sys/bus/w1/devices/' + serial + '/w1_slave'):
			print ("serial number is ok")
		else:
			print("bad serial number")


# if not used as a module (standalone), run this test program 
if __name__ == "__main__":
	owt = OneWireThermo()
	
	owt.addThermometer('28-03168553fbff', 'th_yannick')
