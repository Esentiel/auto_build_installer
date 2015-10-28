"""Network module. Communicate with clients. also It holds ProcessProtocol's child class to subprocess installation"""

from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
from controller import ControllerLayer, GetLogger
import logging, json, os

class InstallationProtocol(Protocol):
	"""Network protocol description. Receiving messages, translate to JSON, building responses"""
	message = ''

	def __init__(self, factory):
		self.factory = factory
		self.controller = ControllerLayer()

	def lineReceived(self, data):
		logging.debug(self.message)
		logging.debug('message: {msg}'.format(msg = self.message))
		request = json.loads(self.message.strip())
		if not self.controller.initialized:
			logging.debug('WTF')
			self.controller.initialize(request)
		self.controller.run_installation()
		response = self.controller.build_responce() 
		self.transport.write(response + '\r\n')
		logging.debug('response: {resp}'.format(resp = repr(response)))
		self.message = ''

class InstallationFactory(Factory):
	"""Server Factory for InstallationProtocol.
	Build protocol"""

	def buildProtocol(self, addr):
		return InstallationProtocol(self)

	def connectionMade(self):
		logging.info('Connected')


class LogProtocol(LineReceiver):
	"""docstring for LogProtocol"""
	def __init__(self, factory):
		self.factory = factory
		self.logger = GetLogger()

	def lineReceived(self, data):
		logging.debug('log req rec: ' + data)
		request = data.split(';')
		response = self.logger.build_response(request)
		self.transport.write(response+'\r\n')
		logging.debug('Loging response: {resp}'.format(resp = repr(response)))
	

class LogFactory(Factory):
	"""Server Factory for InstallationProtocol.
	Build protocol"""

	def buildProtocol(self, addr):
		return LogProtocol(self)

	def connectionMade(self):
		logging.info('Logging Connected')