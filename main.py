from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import json, sys
from exceptions import ValueError


port = int(sys.argv[1])

class BuildConfig(Protocol):
	message = ''

	def __init__(self, factory):
		self.factory = factory

	def dataReceived(self, data):
		self.message+=data
		print self.message
		if '"end": 1' in self.message:
			msg = json.loads(self.message)
			with open('test.txt', 'a') as the_file:
				the_file.write(str(port)+': '+repr(msg)+'\n')
			the_file.close()

		# надо тут еще придумать как-то передавать параметры для запуска процессов установки. И отслеживать их статус.

class BCFactory(Factory):
	"""docstring for BCFactory"""

	def buildProtocol(self, addr):
		return BuildConfig(self)


def main():
	endpoint = TCP4ServerEndpoint(reactor, port)
	endpoint.listen(BCFactory())
	reactor.run()



if __name__ == '__main__':
	main()
