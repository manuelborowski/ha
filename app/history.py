#!/usr/bin/python

import threading, time, logging, os
import config

log = logging.getLogger(__name__)
	

def init():
	log.info("intializing...")
	#check if directory exists...
	if not os.path.isdir(config.HISTORY_DIR):
		os.makedirs(config.HISTORY_DIR)

def start():
	log.info("starting...")
	_historyThread = threading.Thread(target=worker)
	_historyThread.start()


def worker():
	while True:
		log.debug('Updating history')
		time.sleep(config.HISTORY_INTERVAL)

