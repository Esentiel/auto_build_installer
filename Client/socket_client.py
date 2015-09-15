"""Module implementing communications with server. Sending requests, receiving responses.
Request is built from JSON file.
Response is handled by responce_callback method from GUI part"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.basic import LineReceiver
from config import host, port, log_port
import json, re, logging

class InstallationProtocol(Protocol):
	"""Protocol implementation. Communication is processingusing JSON messages"""
	message = []

	def __init__(self):
		with open('install_queue.json','r') as jsonfile:
			self.json_data = str(jsonfile.read()) + '#8^)'
			logging.info('Input: {data}'.format(data = self.json_data))
		jsonfile.close()

	def connectionMade(self):
		self.transport.write(self.json_data)
		logging.debug('Sent data: {data}'.format(data = self.json_data))

	def dataReceived(self, data):
		self.factory.reactor.callLater(5, self.response_processing, data)
		logging.debug('data received: {data}'.format(data = data))

	def response_processing(self, data):
		"""Woring on a response and sending another request"""
		self.message.append(data)
		if '#8^)' in data:
			the_response = []
			response = json.loads(unicode(''.join(self.message).strip().replace('#8^)', ''), errors='ignore'))
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
			self.message = []

	def sendMsg(self):
		self.transport.write(self.json_data)
		logging.info('Sent data to the server')
		logging.debug('Sent data: {data}'.format(data = self.json_data))


class InstallationFactory(ClientFactory):
	"""Factorythat implements InstallationProtocol protocol"""
	protocol = InstallationProtocol

	def __init__(self, reactor, responce_callback):
		self.reactor = reactor
		self.responce_callback = responce_callback

	def startedConnecting(self, connector):
		logging.info('Started to connect.')

	def clientConnectionLost(self, connector, reason):
		logging.warn('Lost connection.  Reason: {r}'.format(r =reason))

	def clientConnectionFailed(self, connector, reason):
		logging.error('Connection failed. Reason: {r}'.format(r =reason))


class LogProtocol(LineReceiver):
	"""docstring for LogProtocol"""

	def __init__(self):
		with open('servers_list.csv', 'r') as thelist:
			self.servers = thelist.read()
		thelist.close()

	def connectionMade(self):
		self.transport.write(self.servers+'\r\n')
		logging.debug('LOG Sent data: {data}'.format(data = self.servers))

	def lineReceived(self, data):
		self.factory.reactor.callLater(10, self.response_processing, data)
		logging.debug('log data received: {data}'.format(data = data))

	def response_processing(self, data):
		logging.info('log resp: '+data)
		response = json.loads(data.strip())
		for key in response.keys():
			with open('installer_logs/{server_id}_installer.log'.format(server_id = key), 'w') as logfile:
				logfile.write(response[key])
			logfile.close()
		self.sendMsg()

	def sendMsg(self):
		self.transport.write(self.servers+'\r\n')
		logging.debug('LOG Sent data: {data}'.format(data = self.servers))


class LogFactory(ClientFactory):
	"""Factorythat implements InstallationProtocol protocol"""
	protocol = LogProtocol

	def __init__(self, reactor):
		self.reactor = reactor

	def startedConnecting(self, connector):
		logging.info('Started to connect.')

	def clientConnectionLost(self, connector, reason):
		logging.warn('Lost connection.  Reason: {r}'.format(r =reason))

	def clientConnectionFailed(self, connector, reason):
		logging.error('Connection failed. Reason: {r}'.format(r =reason))


