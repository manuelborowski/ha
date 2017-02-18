import smtplib
import hashlib
import config
import time, queue, threading


#rate limiting : hash a message and put it in a dictionaty (key).  Value is a combination
#of number-of-times-message-is-tried-to-be-sent and a starttime.
#A message is sent once, then blocked for a number of times xx or until a certain time passed

_messages = {}
_messageQueue = queue.Queue()

class Message:
	pass
	
class MessageSend(Message):
	pass
	
class MessageFlush(Message):
	pass

def start():
	_mainThread = threading.Thread(

class MessageLimiting:
	def __init__(self):
		self.time = int(time.time())
		self.messageCount = 1
	
def _sendMail(message):
	print(message)
	return
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login("automatisatie.borowski@gmail.com", "AuGoo20ToGle16Matisatie")
	server.sendmail("automatisatie.borowski@gmail.com", "emmanuel.borowski@gmail.com", message)
	server.quit()

def send(subject, body):
	if subject == '': subject = 'heating automation message'
	if body == '' : body = 'heating automation default message'
	 
	msg = 'Subject: {}\n\n{}'.format(subject, body)
	b = bytearray()
	b.extend(msg.encode())
	hmsg = hashlib.sha1(b).hexdigest()
	if hmsg in _messages:
		m = _messages[hmsg]
		if m.messageCount < 3:
			_sendMail('{}\n\nMessage #{}'.format(msg, m.messageCount))
		else:
			if (int(time.time()) - int(m.time)) > config.SM_WINDOW:
				_sendMail('{}\n\nMessage #{}'.format(msg, m.messageCount))
				m.time = time.time()
		m.messageCount += 1
	else:
		_messages[hmsg] = MessageLimiting()
		m = _messages[hmsg]
		_sendMail('{}\n\nMessage #{}'.format(msg, m.messageCount))
		m.messageCount += 1
	print(hmsg)
