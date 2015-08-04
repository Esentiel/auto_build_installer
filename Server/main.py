from twisted.internet.protocol import Protocol, ProcessProtocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from controller import InstallProc
import json, sys

port = int(sys.argv[1])

class BuildConfig(Protocol):
	message = ''

	def __init__(self, factory):
		self.factory = factory

	def dataReceived(self, data):
		self.message+=data
		if '"end": 1}' in self.message:
			request = json.loads(self.message)
			server_installation = InstallProc(request)
			# for i in xrange(server_installation.servers_num):
			# test ProcessProtocol
			# 1. make loop to start processes 
			# if ... pasre lockfile..
			# or just use processExited to start another one in case there are more patches..
	def connectionLost(self):
		print 1

		

class BCFactory(Factory):
	"""docstring for BCFactory"""

	def buildProtocol(self, addr):
		return BuildConfig(self)


def main():
	endpoint = TCP4ServerEndpoint(reactor, port)
	endpoint.listen(BCFactory())
	reactor.run()


# https://twistedmatrix.com/documents/8.1.0/api/twisted.internet.protocol.ProcessProtocol.html
if __name__ == '__main__':
	main()
