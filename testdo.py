#! virtual/bin/python

import config, time
config.TEST_MODE = True
config.DO_NBR_OF_BYTES = 2

from app import do

print('start...')
do.init()
do.start()
print('list of pins...')
pins = do.getPinList()
for p in pins:
	print(p)
print('stop...')


#for i in range(0, config.DO_NBR_OF_BYTES * 8):
	#do.setPinActiveLow(i)
	
#do.setPinLowAll()
#print('set all low...')

#for i in range(0, config.DO_NBR_OF_BYTES * 8):
	#do.setPinHigh(i)
	#print('set pin high ; {}'.format(i))
	#time.sleep(0.2)


