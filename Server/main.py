from twisted.internet.protocol import Protocol, ProcessProtocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from controller import InstallProc
from logging
import json, sys, os, time

port = 8007

class MyPP(ProcessProtocol):
	def connectionMade(self):
		self.pid = self.transport.pid
		print "connectionMade {pid}".format(pid = self.pid)

	def processExited(self, reason):
		print "processExited {pid}, status {status}".format(pid = self.pid, status = reason)
		logging.info("processExited {pid}, status {status}".format(pid = self.pid, status = reason))


class BuildConfig(Protocol):
	message = ''

	def __init__(self, factory):
		self.factory = factory

	def dataReceived(self, data):
		self.message+=data
		if '"end": 1}' in self.message:
			logging.debug('Resuest type: 1')
			logging.debug('message: {msg}'.format(msg = self.message))
			request = json.loads(self.message)
			self.server_installation = InstallProc(request)
			self.run_processes(self.server_installation)
			response = self.server_installation.build_responce()
			self.transport.write(response)
			logging.info('Response sent for#1 type')
			logging.debug('response ofr #1 type: {resp}'.format(repr(response)))
			self.message = ''
		elif '"end": 2}' in self.message:
			logging.debug('Resuest type: 2')
			logging.debug('message: {msg}'.format(msg = self.message))
			self.run_processes(self.server_installation)
			response = str(self.server_installation.build_responce())
			self.transport.write(response)
			logging.info('Response sent for#2 type')
			logging.debug('response ofr #2 type: {resp}'.format(repr(response)))
			self.message = ''
		else:
			logging.debug('Message is not full: {msg}'.format(msg = self.message))
			

	def run_processes(self, server_installation_obj):
		for i in xrange(len(server_installation_obj.servers)):
			for j in xrange(len(server_installation_obj.servers[i])):
				transaction_id = server_installation_obj.servers[i][j][0]
				server_id = server_installation_obj.servers[i][j][1]
				patch_num = server_installation_obj.servers[i][j][2]-1
				patch = server_installation_obj.servers[i][j][3]
				if server_installation_obj.get_status(transaction_id, server_id, patch_num):
					pp = MyPP()
					command = ['C:\Python27\python.exe','installer.py', transaction_id, server_id, str(patch_num+1), patch]
					subprocess = reactor.spawnProcess(pp, command[0], command, env=os.environ)
					print "Process for {pid} started..".format(pid = pp.pid)
					logging.info("Process for {pid} started with following params: {params}".format(pid = pp.pid, params = repr(server_installation_obj.servers[i][j])))
					del server_installation_obj.servers[i][j]
					time.sleep(5)
					break
					

class BCFactory(Factory):
	"""docstring for BCFactory"""

	def buildProtocol(self, addr):
		return BuildConfig(self)

	def connectionMade(self):
		print 'Connected'

def main():
	logging.basicConfig(filename='logs/main.log', level=logging.INFO)
	endpoint = TCP4ServerEndpoint(reactor, port)
	endpoint.listen(BCFactory())
	reactor.run()

if __name__ == '__main__':
	main()
