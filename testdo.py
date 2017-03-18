#! virtual/bin/python

import config, time
config.MODULE_TEST = True
config.DO_NBR_OF_BYTES = 2

from app import do

print('start...')
do.init()
do.start()
print('list of pins...')
pins = do.getPinList()
for n, p in enumerate(pins):
	print('{}/{}'.format(n, p))
print('stop...')


#for i in range(0, config.DO_NBR_OF_BYTES * 8):
	#do.setPinActiveLow(i)
	
#do.setPinLowAll()
#print('set all low...')

#for i in range(0, config.DO_NBR_OF_BYTES * 8):
	#do.setPinHigh(i)
	#print('set pin high ; {}'.format(i))
	#time.sleep(0.2)


