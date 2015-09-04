"""The server's heart. Looping all around trying to do something useful."""

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from socket_server import InstallationFactory
import logging

#chose any port you want. But it should be the same for a Client
port = 8008

def main():
	logging.basicConfig(filename='logs/main.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
	endpoint = TCP4ServerEndpoint(reactor, port)
	endpoint.listen(InstallationFactory())
	reactor.run()

if __name__ == '__main__':
	main()
