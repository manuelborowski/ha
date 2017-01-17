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

def init():
	log.info("initializing...")
	global options
	#Define some manager options
	options = ZWaveOption(config.ZWAVE_DEVICE, config_path="zwconfig", user_path=".", cmd_line="")
	options.set_log_file(config.OPENZWAVE_LOG_FILE)
	options.set_append_log_file(False)
	options.set_console_output(False)
	options.set_save_log_level(config.OPENZWAVE_LOG_LEVEL)
	#options.set_save_log_level('Info')
	options.set_logging(False)
	options.lock()

def start():
	log.info("starting...")

	#print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))

	#Create a network object
	network = ZWaveNetwork(options)

	time_started = 0
	log.info("Waiting for network awaked")
	for i in range(0,300):
		if network.state>=network.STATE_AWAKED:
			log.info("Network is awaked.")
			#print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))
			break
		else:
			#sys.stdout.write(".")
			#sys.stdout.flush()
			#time_started += 1
			time.sleep(1.0)
	if network.state<network.STATE_AWAKED:
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
	log.info("Waiting for network ready")
	#print("------------------------------------------------------------")
	for i in range(0,300):
		if network.state>=network.STATE_READY:
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


	#print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))
	if not network.is_ready:
	#	print(".")
		log.info("Network is not ready but continue anyway")

	#print("------------------------------------------------------------")
	#print("Controller capabilities : {}".format(network.controller.capabilities))
	#print("Controller node capabilities : {}".format(network.controller.node.capabilities))
	#print("Nodes in network : {}".format(network.nodes_count))
	#print("Driver statistics : {}".format(network.controller.stats))
	#print("------------------------------------------------------------")
	#for node in network.nodes:

		#print("------------------------------------------------------------")
		#print("{} - Name : {}".format(network.nodes[node].node_id,network.nodes[node].name))
		#print("{} - Manufacturer name / id : {} / {}".format(network.nodes[node].node_id,network.nodes[node].manufacturer_name, network.nodes[node].manufacturer_id))
		#print("{} - Product name / id / type : {} / {} / {}".format(network.nodes[node].node_id,network.nodes[node].product_name, network.nodes[node].product_id, network.nodes[node].product_type))
		#print("{} - Version : {}".format(network.nodes[node].node_id, network.nodes[node].version))
		#print("{} - Command classes : {}".format(network.nodes[node].node_id,network.nodes[node].command_classes_as_string))
		#print("{} - Capabilities : {}".format(network.nodes[node].node_id,network.nodes[node].capabilities))
		#print("{} - Neigbors : {}".format(network.nodes[node].node_id,network.nodes[node].neighbors))
		#print("{} - Can sleep : {}".format(network.nodes[node].node_id,network.nodes[node].can_wake_up()))
		#groups = {}
		#for grp in network.nodes[node].groups :
			#groups[network.nodes[node].groups[grp].index] = {'label':network.nodes[node].groups[grp].label, 'associations':network.nodes[node].groups[grp].associations}
		#print("{} - Groups : {}".format (network.nodes[node].node_id, groups))
		#values = {}
		#for val in network.nodes[node].values :
			#values[network.nodes[node].values[val].object_id] = {
				#'label':network.nodes[node].values[val].label,
				#'help':network.nodes[node].values[val].help,
				#'command_class':network.nodes[node].values[val].command_class,
				#'max':network.nodes[node].values[val].max,
				#'min':network.nodes[node].values[val].min,
				#'units':network.nodes[node].values[val].units,
				#'data':network.nodes[node].values[val].data_as_string,
				#'ispolled':network.nodes[node].values[val].is_polled
				#}
		##print("{} - Values : {}".format(network.nodes[node].node_id, values))
		##print("------------------------------------------------------------")
		#for cmd in network.nodes[node].command_classes:
			#print("   ---------   ")
			##print("cmd = {}".format(cmd))
			#values = {}
			#for val in network.nodes[node].get_values_for_command_class(cmd) :
				#values[network.nodes[node].values[val].object_id] = {
					#'label':network.nodes[node].values[val].label,
					#'help':network.nodes[node].values[val].help,
					#'max':network.nodes[node].values[val].max,
					#'min':network.nodes[node].values[val].min,
					#'units':network.nodes[node].values[val].units,
					#'data':network.nodes[node].values[val].data,
					#'data_str':network.nodes[node].values[val].data_as_string,
					#'genre':network.nodes[node].values[val].genre,
					#'type':network.nodes[node].values[val].type,
					#'ispolled':network.nodes[node].values[val].is_polled,
					#'readonly':network.nodes[node].values[val].is_read_only,
					#'writeonly':network.nodes[node].values[val].is_write_only,
					#}
			#print("{} - Values for command class : {} : {}".format(network.nodes[node].node_id,
										#network.nodes[node].get_command_class_as_string(cmd),
										#values))
		#print("------------------------------------------------------------")

	#print("------------------------------------------------------------")
	#print("Driver statistics : {}".format(network.controller.stats))
	#print("------------------------------------------------------------")

	#print("------------------------------------------------------------")
	#print("Try to autodetect nodes on the network")
	#print("------------------------------------------------------------")
	#print("Nodes in network : {}".format(network.nodes_count))
	#print("------------------------------------------------------------")
	#print("Retrieve switches on the network")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_switches() :
			#print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
			#print("  state: {}".format(network.nodes[node].get_switch_state(val)))
	#print("------------------------------------------------------------")
	#print("Retrieve dimmers on the network")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_dimmers() :
			#print("node/name/index/instance : {}/{}/{}/{}".format (node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format (network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : {}".format (network.nodes[node].values[val].id_on_network))
			#print("  level: {}".format (network.nodes[node].get_dimmer_level(val)))
	#print("------------------------------------------------------------")
	#print("Retrieve RGB Bulbs on the network")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_rgbbulbs() :
			#print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
			#print("  level: {}".format(network.nodes[node].get_dimmer_level(val)))
	#print("------------------------------------------------------------")
	#print("Retrieve sensors on the network")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_sensors() :
			#print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
			#print("  value: {} {}".format(network.nodes[node].get_sensor_value(val), network.nodes[node].values[val].units))
	#print("------------------------------------------------------------")
	#print("Retrieve thermostats on the network")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_thermostats() :
			#print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
			#print("  value: {} {}".format(network.nodes[node].get_thermostat_value(val), network.nodes[node].values[val].units))
	#print("------------------------------------------------------------")
	#print("Retrieve switches all compatibles devices on the network    ")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_switches_all() :
			#print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
			#print("  value / items:  / {}".format(network.nodes[node].get_switch_all_item(val), network.nodes[node].get_switch_all_items(val)))
			#print("  state: {}".format(network.nodes[node].get_switch_all_state(val)))
	#print("------------------------------------------------------------")
	#print("------------------------------------------------------------")
	#print("Retrieve protection compatibles devices on the network    ")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_protections() :
			#print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : ".format(network.nodes[node].values[val].id_on_network))
			#print("  value / items: {} / {}".format(network.nodes[node].get_protection_item(val), network.nodes[node].get_protection_items(val)))
	#print("------------------------------------------------------------")

	#print("------------------------------------------------------------")
	#print("Retrieve battery compatibles devices on the network         ")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_battery_levels() :
			#print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
			#print("  value : {}".format(network.nodes[node].get_battery_level(val)))
	#print("------------------------------------------------------------")

	#print("------------------------------------------------------------")
	#print("Retrieve power level compatibles devices on the network         ")
	#print("------------------------------------------------------------")
	#values = {}
	#for node in network.nodes:
		#for val in network.nodes[node].get_power_levels() :
			#print("node/name/index/instance : {}/{}/{}/{}".format(node,network.nodes[node].name,network.nodes[node].values[val].index,network.nodes[node].values[val].instance))
			#print("  label/help : {}/{}".format(network.nodes[node].values[val].label,network.nodes[node].values[val].help))
			#print("  id on the network : {}".format(network.nodes[node].values[val].id_on_network))
			#print("  value : {}".format(network.nodes[node].get_power_level(val)))
	#print("------------------------------------------------------------")
	##print
	##print("------------------------------------------------------------")
	##print("Activate the switches on the network")
	##print("Nodes in network : {}").format network.nodes_count
	##print("------------------------------------------------------------")
	##for node in network.nodes:
	##    for val in network.nodes[node].get_switches() :
	##        print("Activate switch {} on node {}".format \
	##                (network.nodes[node].values[val].label,node))
	##        network.nodes[node].set_switch(val,True)
	##        print("Sleep 10 seconds")
	##        time.sleep(10.0)
	##        print("Dectivate switch {} on node {}".format \
	##                (network.nodes[node].values[val].label,node))
	##        network.nodes[node].set_switch(val,False)
	##print("Done"))
	##print("------------------------------------------------------------")

	#print("------------------------------------------------------------")
	#print("Driver statistics : {}".format(network.controller.stats))
	#print("Driver label : {}".format(network.controller.get_stats_label('retries')))
	#print("------------------------------------------------------------")


	#print("------------------------------------------------------------")
	#print("Get the temperature")
	#print("------------------------------------------------------------")
	#values = {}
	for node in network.nodes:
		for val in network.nodes[node].get_sensors() :
			if network.nodes[node].name == "yannick" and network.nodes[node].values[val].label == "Temperature":
				t_node = node
				t_sensor = val
				break
			if network.nodes[node].name == "yannick" and network.nodes[node].values[val].label == "Luminance":
				t_node = node
				l_sensor = val

	print("Temp : Node/sensor : {}/{}".format(t_node, t_sensor))      
	print("Lum : Node/sensor : {}/{}".format(t_node, l_sensor))      

	for i in range(0,300):
		time.sleep(1.0)
		print("Temperatuur is {} {}".format(network.nodes[t_node].get_sensor_value(t_sensor), network.nodes[t_node].values[t_sensor].units))
		print("Luminancie is {} {}".format(network.nodes[t_node].get_sensor_value(l_sensor), network.nodes[t_node].values[l_sensor].units))
		  

	print("------------------------------------------------------------")
	print("Stop network")
	print("------------------------------------------------------------")
	network.stop()
	print("Memory use : {} Mo".format( (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)))
