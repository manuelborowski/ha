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

log = logging.getLogger(__name__)

import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import time
import config

class NodeFunction:
	def __init__(self):
		self.node = 0
		self.function = 0
		self.value = config.INVALID_TEMP

_thermometers = {}


def init():
	log.info("initializing...")
	global options
	#Define some manager options
	options = ZWaveOption(config.ZWAVE_DEVICE, config_path=config.OPENZWAVE_CONFIG_FILE, user_path=".", cmd_line="")
	options.set_log_file(config.OPENZWAVE_LOG_FILE)
	options.set_append_log_file(False)
	options.set_console_output(False)
	options.set_save_log_level(config.OPENZWAVE_LOG_LEVEL)
	#options.set_save_log_level('Info')
	options.set_logging(False)
	options.lock()

def start():
	global _network
	log.info("starting...")

	#print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))

	#Create a network object
	_network = ZWaveNetwork(options)

	time_started = 0
	#log.info("Waiting for network awaked")
	for i in range(0,30):
		log.info("Waiting for network awaked (%d seconds)", i*10)
		for t in range(0, 9):
			if _network.state>=network.STATE_AWAKED:
				log.info("Network is awaked.")
				#print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))
				break
			else:
				#sys.stdout.write(".")
				#sys.stdout.flush()
				#time_started += 1
				time.sleep(1.0)
		if _network.state>=network.STATE_AWAKED:
				break
	if _network.state<network.STATE_AWAKED:
		#print(".")
		log.info("Network is not awake but continue anyway")
	#print("------------------------------------------------------------")
	#print("Use openzwave library : {}".format(network.controller.ozw_library_version))
	#print("Use python library : {}".format(network.controller.python_library_version))
	#print("Use ZWave library : {}".format(network.controller.library_description))
	#print("Network home id : {}".format(network.home_id_str))
	#print("Controller node id : {}".format(network.controller.node.node_id))
	#print("Controller node version : {}".format(network.controller.node.version))
	#print("Nodes in network : {}".format(network.nodes_count))
	#print("------------------------------------------------------------")
	#log.info("Waiting for network ready")
	#print("------------------------------------------------------------")
	for i in range(0,30):
		log.info("Waiting for network ready (%d seconds)", i*10)
		for t in range(0, 9):
			if _network.state>=network.STATE_READY:
				#print(" done in {} seconds".format(time_started))
				log.info("Network is ready")
				break
			else:
				#sys.stdout.write(".")
				#time_started += 1
				#sys.stdout.write(network.state_str)
				#sys.stdout.write("(")
				#sys.stdout.write(str(network.nodes_count))
				#sys.stdout.write(")")
				#sys.stdout.write(".")
				#sys.stdout.flush()
				time.sleep(1.0)
		if _network.state>=network.STATE_READY:
			break


	#print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))
	if not _network.is_ready:
	#	print(".")
		log.info("Network is not ready but continue anyway")

	for node in _network.nodes:
		for val in _network.nodes[node].get_sensors() :
			if _network.nodes[node].name == "yannick" and _network.nodes[node].values[val].label == "Temperature":
				t_node = node
				t_sensor = val
				break
			if _network.nodes[node].name == "yannick" and _network.nodes[node].values[val].label == "Luminance":
				t_node = node
				l_sensor = val

	print("Temp : Node/sensor : {}/{}".format(t_node, t_sensor))      
	print("Lum : Node/sensor : {}/{}".format(t_node, l_sensor))      

	for i in range(0,300):
		time.sleep(1.0)
		print("Temperatuur is {} {}".format(_network.nodes[t_node].get_sensor_value(t_sensor), _network.nodes[t_node].values[t_sensor].units))
		print("Luminancie is {} {}".format(_network.nodes[t_node].get_sensor_value(l_sensor), _network.nodes[t_node].values[l_sensor].units))
		  

	print("------------------------------------------------------------")
	print("Stop network")
	print("------------------------------------------------------------")
	_network.stop()
	print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))


def _findNodefunction(name):
	if not _network.is_ready:
		log.error("network is not ready, cannot add %s", name)
		return
	for n in _network.nodes:
		for f in _network.nodes[n].get_sensors():
			if _network.nodes[n].name==name and _network.nodes[n].values[f].label=="Temperature":
				_thermometers[name].node = n
				_thermometers[name].function = f
				_thermometers[name].value = _network.nodes[n].get_sensor_value(f)
				return
	log.error("cannot find node with name %s", name)
	

def addThermometer(name):
	_thermometers[name] = NodeFunction()
	if _network.is_ready:
		self._findNodeFunction(name)
	
