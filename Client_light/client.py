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
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import task
from sys import stdout
from twisted.internet import reactor
import time, json, re

host = 'localhost'
port = 8007

class InstProtocol(Protocol):
	message = ''

	def __init__(self):
		with open('install_qeue.json','r') as jsonfile:
			self.json_data = jsonfile.read()
		jsonfile.close()
		self.json_data_status = self.json_data.replace('"end": 1', '"end": 2')

	def connectionMade(self):
		self.transport.write(self.json_data)

	def dataReceived(self, data):
		self.message += data
		if '"end"' in self.message:
			response = json.loads(self.message)
			stdout.write('\n\n\n')
			for server_key in response['servers'].keys():
				for patch_key in response['servers'][server_key].keys():
					if 'patch' in patch_key:
						server_string =  'Server: {server_id}\tPatch: {patch_name}\t Status: {status}\n'.format(server_id = response['servers'][server_key]['server_id'],\
																									patch_name = re.match('.*/(.*)', response['servers'][server_key][patch_key]['patch']).group(1),\
																									status = response['servers'][server_key][patch_key]['status'])

						stdout.write(server_string)
			if 'PENDING' not in self.message:
				self.transport.loseConnection()
			else:
				time.sleep(30)
				self.sendMsg()
			self.message = ''

	def sendMsg(self):
		self.transport.write(self.json_data_status)

class InstFactory(ClientFactory):
	protocol = InstProtocol

	def startedConnecting(self, connector):
		print 'Started to connect.'

	def clientConnectionLost(self, connector, reason):
		print 'Lost connection.  Reason:', reason

	def clientConnectionFailed(self, connector, reason):
		print 'Connection failed. Reason:', reason

reactor.connectTCP(host, port, InstFactory())
reactor.run()