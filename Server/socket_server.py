"""Network module. Communicate with clients. also It holds ProcessProtocol's child class to subprocess installation"""

from twisted.internet.protocol import Protocol, Factory
from controller import ControllerLayer, GetLogger
import logging, json, os

class InstallationProtocol(Protocol):
	"""Network protocol description. Receiving messages, translate to JSON, building responses"""
	message = ''

	def __init__(self, factory):
		self.factory = factory
		self.controller = ControllerLayer()

	def dataReceived(self, data):
		self.message+=data
		logging.debug(self.message)
		if '#8^)' in self.message:
			logging.debug('message: {msg}'.format(msg = self.message))
			request = json.loads(self.message.replace('#8^)', ''))
			if not self.controller.initialized:
				logging.debug('WTF')
				self.controller.initialize(request)
			self.controller.run_installation()
			response = self.controller.build_responce() + '#8^)'
			self.transport.write(response)
			logging.debug('response: {resp}'.format(resp = repr(response)))
			self.message = ''
		else:
			logging.debug('Message is not full: {msg}'.format(msg = self.message))	


class InstallationFactory(Factory):
	"""Server Factory for InstallationProtocol.
	Build protocol"""

	def buildProtocol(self, addr):
		return InstallationProtocol(self)

	def connectionMade(self):
		logging.info('Connected')


class LogProtocol(Protocol):
	"""docstring for LogProtocol"""
	message = ''
	def __init__(self, factory):
		self.factory = factory
		self.logger = GetLogger()

	def dataReceived(self, data):
		self.message+=data
		logging.debug(self.message)
		if '#8^)' in self.message:
			logging.debug('Loging message: {msg}'.format(msg = self.message))
			request = self.message.replace('#8^)', '').split(';')
			response = self.logger.build_response(request) + '#8^)'
			self.transport.write(response)
			logging.debug('Loging response: {resp}'.format(resp = repr(response)))
			self.message = ''
		else:
			logging.debug('Loging Message is not full: {msg}'.format(msg = self.message))	

class LogFactory(Factory):
	"""Server Factory for InstallationProtocol.
	Build protocol"""

	def buildProtocol(self, addr):
		return LogProtocol(self)

	def connectionMade(self):
		logging.info('Logging Connected')