"""The server's heart. Looping all around trying to do something useful."""

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from socket_server import InstallationFactory, LogFactory
import logging

#chose any port you want. But it should be the same for a Client
port = 8008
log_port = 8007

def main():
	logging.basicConfig(filename='logs/main.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
	endpoint = TCP4ServerEndpoint(reactor, port)
	log_endpoint = TCP4ServerEndpoint(reactor, log_port)
	endpoint.listen(InstallationFactory())
	log_endpoint.listen(LogFactory())
	print 'Server is running...'
	reactor.run()

if __name__ == '__main__':
	main()
