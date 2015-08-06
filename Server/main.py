from twisted.internet.protocol import Protocol, ProcessProtocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from controller import InstallProc
import json, sys, os, time

port = 8007

class MyPP(ProcessProtocol):
	def connectionMade(self):
		self.pid = self.transport.pid
		print "connectionMade {pid}".format(pid = self.pid)

	def processExited(self, reason):
		print "processExited {pid}, status {status}".format(pid = self.pid, status = reason)


class BuildConfig(Protocol):
	message = ''

	def __init__(self, factory):
		self.factory = factory

	def dataReceived(self, data):
		self.message+=data
		if '"end": 1}' in self.message:
			request = json.loads(self.message)
			server_installation = InstallProc(request)
			self.run_processes(server_installation)
			response = server_installation.build_responce()
			self.transport.write(str(response))
		elif '"end": 2}' in self.message:
			self.run_processes(server_installation)
			response = server_installation.build_responce()
			self.transport.write(str(response))
			

	def run_processes(self, server_installation_obj):
		for i in xrange(server_installation_obj.servers_num):
			for j in xrange(len(server_installation_obj.__dict__['server_{0}'.format(i)])):
				transaction_id = server_installation_obj.__dict__['server_{0}'.format(i)][j][0]
				server_id = server_installation_obj.__dict__['server_{0}'.format(i)][j][1]
				patch_num = server_installation_obj.__dict__['server_{0}'.format(i)][j][2]-1
				patch = server_installation_obj.__dict__['server_{0}'.format(i)][j][3]
				if server_installation_obj.get_status(server_id, patch_num):
					pp = MyPP()
					command = ['C:\Python27\python.exe','installer.py', transaction_id, server_id, str(patch_num+1), patch]
					subprocess = reactor.spawnProcess(pp, command[0], command, env=os.environ)
					print "Process for {pid} started..".format(pid = pp.pid)
					del server_installation_obj.__dict__['server_{0}'.format(i)][j]
					time.sleep(5)
					

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
