# -*- coding: utf-8 -*-
"""

This file is part of **python-openzwave** project https://github.com/OpenZWave/python-openzwave.
    :platform: Unix, Windows, MacOS X
    :sinopsis: openzwave wrapper

.. moduleauthor:: bibi21000 aka Sébastien GALLET <bibi21000@gmail.com>

License : GPL(v3)

**python-openzwave** is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

**python-openzwave** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with python-openzwave. If not, see http://www.gnu.org/licenses.

"""

import logging
import sys, os
import resource
import time, threading
from threading import Lock

log = logging.getLogger(__name__)

import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import config

class NodeFunction:
	def __init__(self):
		self.node = 0
		self.tempVal = 0
		self.batVal = 0
		self.ready = False

_thermometers = {}
_lock = Lock()

def _getLock():
	_lock.acquire()

def _releaseLock():
	_lock.release()

def init():
	log.info("initializing...")
	global _network
	#Define some manager options
	options = ZWaveOption(config.ZWAVE_DEVICE, config_path=config.OPENZWAVE_CONFIG_FILE, user_path=".", cmd_line="")
	options.set_log_file(config.OPENZWAVE_LOG_FILE)
	options.set_append_log_file(False)
	options.set_console_output(False)
	options.set_save_log_level(config.OPENZWAVE_LOG_LEVEL)
	#options.set_save_log_level('Info')
	options.set_logging(True)
	options.lock()
	#Create a network object
	_network = ZWaveNetwork(options)

def start():
	global _network
	log.info("starting...")
	_thermoThread = threading.Thread(target=_worker)
	_thermoThread.start()


def _worker():
	global _network
	log.info("start worker...")

	time_started = 0
	for i in range(0,3):
		log.info("Waiting for network awaked (%d seconds)", i*10)
		for t in range(0, 9):
			if _network.state >= _network.STATE_AWAKED:
				log.info("Network is awaked.")
				break
			else:
				time.sleep(1.0)
		if _network.state >= _network.STATE_AWAKED:
				break
	if _network.state < _network.STATE_AWAKED:
		log.info("Network is not awake but continue anyway")
	#for i in range(0,3):
		#log.info("Waiting for network ready (%d seconds)", i*10)
		#for t in range(0, 9):
			#if _network.state >= _network.STATE_READY:
				#log.info("Network is ready")
				#break
			#else:
				#time.sleep(1.0)
		#if _network.state >= _network.STATE_READY:
			#break

	while True:
		#network is ready, check if Thermometers are added...
		if _thermometers:
			_getLock()
			for t in _thermometers:
				_findNodeFunction(t)
			_releaseLock()
		time.sleep(10 * 60)

def _findNodeFunction(name):
	global _thermometers
	if _thermometers[name].ready: return
	log.info("Find a node/function for : %s", name)
	for n in _network.nodes:
		for f in _network.nodes[n].get_sensors():
			if _network.nodes[n].name == name and _network.nodes[n].values[f].label == "Temperature":
				_thermometers[name].node = n
				_thermometers[name].tempVal = f
				_thermometers[name].ready = True
				if _network.nodes[n].get_battery_levels():
					for k in _network.nodes[n].get_battery_levels().keys():
						_thermometers[name].batVal = k
				return
	log.error("cannot find node with name %s", name)
	

def addThermometer(name):
	global _thermometers
	log.info("Adding thermometer : %s ", name)
	_getLock()
	_thermometers[name] = NodeFunction()
	_findNodeFunction(name)
	_releaseLock()
	
def getValue(name):
	try:
		if _thermometers[name].ready:
			return _network.nodes[_thermometers[name].node].get_sensor_value(_thermometers[name].tempVal)
		else:
			return config.INVALID_TEMP
	except Exception as e:
		log.error("getValue : " + str(e))
		return config.INVALID_TEMP

def getBatteryLevel(name):
	try:
		if _thermometers[name].ready:
			return _network.nodes[_thermometers[name].node].get_battery_level(_thermometers[name].batVal)
		else:
			return config.INVALID_BATTERY_LEVEL
	except Exception as e:
		log.error("getBatteryLevel : " + str(e))
		return config.INVALID_BATTERY_LEVEL
