#! virtual/bin/python

import config, time
config.TEST_MODE = True

from app import sendmail

sendmail.start()
print('sending messages...')

while True:
	sendmail.send('subject of message', 'body of message')
	time.sleep(1)
