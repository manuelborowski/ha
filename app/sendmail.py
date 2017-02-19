import smtplib
import hashlib
import config
import time, queue, threading, logging

log = logging.getLogger(__name__)

#rate limiting : hash a message and put it in a dictionaty (key).  Value is a combination
#of number-of-times-message-is-tried-to-be-sent and a starttime.
#A message is sent once, then blocked for a number of times xx or until a certain time passed

_messages = {}
_messageQueue = queue.Queue()

#base class
class Message:
	pass
	
#class used to transmit message to worker thread
class MessageSend(Message):
	def __init__(self, subject, body):
		self.subject = subject
		self.body = body
	
#class used to transmit flush-command to worker thread
class MessageFlush(Message):
	pass

def start():
	log.info("starting")
	_mainThread = threading.Thread(
		target = mailWorker,
		args = (_messageQueue, ))
	_mainThread.setDaemon(True)
	_mainThread.start()
	
	_flushThread = threading.Thread(target = flushWorker)
	_flushThread.setDaemon(True)
	_flushThread.start()

#flushes the dictionary on regular intervals to avoid a too large dictionary		
def flushWorker():
	while True:
		time.sleep(config.SM_WINDOW + 5)
		flush()
		log.info('flush message cache')

class MessageLimiting:
	def __init__(self):
		self.time = int(time.time())
		self.messageCount = 1
	
def send(subject, body):
	m = MessageSend(subject, body)
	_messageQueue.put(m)
	
def flush():
	m = MessageFlush()
	_messageQueue.put(m)
	
	
def mailWorker(q):
	global _messages
	while True:
		m = q.get()
		if isinstance(m, MessageSend):
			_send(m.subject, m.body)
		elif isinstance(m, MessageFlush):
			_messages = {}
	
def _sendMail(m, mc):
	message = '{}\n\nMessage #{}\n\nGreetings HA'.format(m, mc)
	log.error(message)
	if not config.SM_ENABLE_SEND_MAIL:
		return
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login("automatisatie.borowski@gmail.com", "AuGoo20ToGle16Matisatie")
	server.sendmail("automatisatie.borowski@gmail.com", "emmanuel.borowski@gmail.com", message)
	server.quit()

def _send(subject, body):
	if subject == '': subject = 'heating automation message'
	if body == '' : body = 'heating automation default message'
	 
	msg = 'Subject: {}\n\n{}'.format(subject, body)
	b = bytearray()
	b.extend(msg.encode())
	hmsg = hashlib.sha1(b).hexdigest()
	if hmsg in _messages:
		m = _messages[hmsg]
		if m.messageCount < 3:
			_sendMail(msg, m.messageCount)
		else:
			if (int(time.time()) - int(m.time)) > config.SM_WINDOW:
				_sendMail(msg, m.messageCount)
				m.time = time.time()
		m.messageCount += 1
	else:
		_messages[hmsg] = MessageLimiting()
		m = _messages[hmsg]
		_sendMail(msg, m.messageCount)
		m.messageCount += 1
