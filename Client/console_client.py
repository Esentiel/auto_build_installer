from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import task
from sys import stdout
from twisted.internet import reactor
import time, json, re, uuid

host = 'vm-bee.netcracker.com'
port = 8007

class InstProtocol(Protocol):
	message = ''

	def __init__(self):
		with open('install_qeue.json','r') as jsonfile:
			self.json_data = str(jsonfile.read()).replace('}}}}', '}}},"end": 1}')
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