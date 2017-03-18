#! virtual/bin/python

import config, time
config.MODULE_TEST = True

from app import sendmail

sendmail.start()
print('sending messages...')

while True:
	sendmail.send('subject of message', 'body of message')
	time.sleep(1)
