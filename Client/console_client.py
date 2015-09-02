from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout
import json, re, logging

host = 'vm-bee.netcracker.com'
port = 8007

class InstProtocol(Protocol):
	message = ''

	def __init__(self):
		with open('install_qeue.json','r') as jsonfile:
			self.json_data = str(jsonfile.read()).replace('}}}}', '}}},"end": 1}')
			logging.info('Input: {data}'.format(data = self.json_data))
		jsonfile.close()
		self.json_data_status = self.json_data.replace('"end": 1', '"end": 2')

	def connectionMade(self):
		self.transport.write(self.json_data)
		logging.info('Sent data to the server after connectionMade')
		logging.debug('Sent data: {data}'.format(data = self.json_data))

	def dataReceived(self, data):
		self.factory.reactor.callLater(5, self.build_log, data)
		logging.debug('data received: {data}'.format(data = data))

	def build_log(self, data):
		self.message += data
		if '"end"' in self.message:
			the_response = []
			response = json.loads(self.message)
			for server_key in response['servers'].keys():
				for patch_key in response['servers'][server_key].keys():
					if 'patch' in patch_key:
						the_row = {}
						the_row['server_id'] = response['servers'][server_key]['server_id']
						the_row['patch'] = str(re.match('.*/(.*)', response['servers'][server_key][patch_key]['patch']).group(1)).replace('_autoinstaller.zip', '')
						the_row['status'] = response['servers'][server_key][patch_key]['status']
						logging.debug('row with status: {row}'.format(row = the_row))
						the_response.append(the_row)
			self.factory.responce_callback(the_response)
			logging.info('responce_callback initiated')
			logging.debug('the responce: {resp}'.format(resp = the_response))

			self.sendMsg()
			self.message = ''

	def sendMsg(self):
		self.transport.write(self.json_data_status)
		logging.info('Sent data to the server')
		logging.debug('Sent data: {data}'.format(data = self.json_data_status))


class InstFactory(ClientFactory):
	protocol = InstProtocol

	def __init__(self, reactor, responce_callback):
		self.reactor = reactor
		self.responce_callback = responce_callback

	def startedConnecting(self, connector):
		print 'Started to connect.'

	def clientConnectionLost(self, connector, reason):
		print 'Lost connection.  Reason:', reason

	def clientConnectionFailed(self, connector, reason):
		print 'Connection failed. Reason:', reason

