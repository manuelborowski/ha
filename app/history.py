#!/usr/bin/python

import threading, time, logging, os, datetime
from app import cache
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


def _getFileHandler(fn):
	if not os.path.isfile(fn):
		#create a new file, write the header and return the handler
		hfh = open(fn, 'a')
		tl = cache.getThermostatList()
		header = 'time;'
		for t in tl:
			header = header + t.hw_id + ';'
		header = header[:-1] + '\n'
		log.debug('new header : %s', header)
		hfh.write(header)
		hfh.close()
	return open(fn, 'a')

def worker():
	while True:
		log.debug('Updating history')
		time.sleep(config.HISTORY_INTERVAL)
		#get current date/time, extract year and month and check if correspondig file exists
		now = datetime.datetime.now()
		hfn = os.path.join(config.HISTORY_DIR, "{}-{}-{}-{}.his".format(now.year, now.month, now.day, now.hour))
		hf = _getFileHandler(hfn)
		tl = cache.getThermostatList()
		line = '{}-{}:{};'.format(now.day, now.hour, now.minute)
		for t in tl:
			line = line + str(t.measured) + ';'
		line = line[:-1] + '\n'
		hf.	write(line)
		hf.close()

