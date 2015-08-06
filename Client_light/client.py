# import socket, json, time, sys

# HOST = 'localhost'    # The remote host
# PORT = 8007              # The same port as used by the server
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # s.setblocking(0)
# s.connect((HOST, PORT))


# with open('install_qeue.json', 'r') as json_file:
# 	# json_data = json.load(json_file)
# 	json_data = json_file.read()
# json_file.close()
# s.sendall(str(json_data))
# # while True:
# # 	s.sendall(str(json_data))
# # 	response = ''
# # 	while True:
# # 		try:
# # 			response += s.recv(1024)
# # 			if '"end": 1}' in response:
# # 				print response
# # 				break
# # 		except socket.timeout, e:
# # 			if err == 'timed out':
# # 				time.sleep(1)
# # 				print 'recv timed out, retry later'
# # 				continue
# # 			else:
# # 				print e
# # 				sys.exit(1)
# # 		except socket.error, e:
# # 			# Something else happened, handle error, exit, etc.
# # 			print e
# # 			sys.exit(1)
# # 		else:
# # 			if len(response) == 0:
# # 				print 'orderly shutdown on server end'
# # 				sys.exit(0)

# # 	if 'PENDING' not in response:
# # 		print "Everythis was done!"
# # 		break
# # 	else:
# # 		time.sleep(5)
# time.sleep(30)


# json_data = json_data.replace('"end": 1', '"end": 2')

# s.sendall(str(json_data))
###############################

host = 'localhost'
port = 8007

from twisted.internet import reactor, task
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

class InstallProtocol(Protocol):
	def sendMessage(self, msg):
		self.transport.write(msg)

def gotProtocol(p):
	with open('install_qeue.json', 'r') as json_file:
		json_data = json_file.read()
	json_file.close()

	p.sendMessage(json_data)
	l = task.LoopingCall(p.sendMessage, json_data.replace('"end": 1', '"end": 2'))
	l.start(1.0)

point = TCP4ClientEndpoint(reactor, host, port)
d = connectProtocol(point, InstallProtocol())
d.addCallback(gotProtocol)
reactor.run()