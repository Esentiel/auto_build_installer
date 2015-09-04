"""controller module is using as intermediate layer between network(communicating with clients) 
and installatiion(communicating with NC server) levels."""
from twisted.internet import reactor
from twisted.internet.protocol import ProcessProtocol
import os, json, logging

class InstallationProcess(ProcessProtocol):
	"Wrapper for ProcessProtocol. Is using for logging"
	def connectionMade(self):
		self.pid = self.transport.pid
		print "connectionMade {pid}".format(pid = self.pid)

	def processExited(self, reason):
		print "processExited {pid}, status {status}".format(pid = self.pid, status = reason)
		logging.info("processExited {pid}, status {status}".format(pid = self.pid, status = reason))


class ControllerLayer(object):
	"""InstallProc class implements working with messages that are recieved from clients.
	It transform them into a propper way and use them in futher process."""

	initialized = False

	def initialize(self, json_source):
		"""Working with dictionary created from json message recieved by server. Transfor it into a better forat(list).
		Also creating directories and files required for futher processing(by installer.py)."""
		logging.debug('json_source:\n{0}'.format(json_source))
		self.json_source = json_source
		self.servers_num = int(len(self.json_source['servers'].keys()))
		self.transaction_id = self.json_source['transaction_id']
		logging.debug('Creation of InstallProc\'s object:\tServer\'s number = {serv_num}\tTransation_id: {id}'.format(serv_num = self.servers_num, id = self.transaction_id))
		self.servers = []
		for i in xrange(self.servers_num):
			patchs_num = len(self.json_source['servers']['server_{num}'.format(num = i)].keys())-1
			patchs_list = []
			for j in xrange(patchs_num):
				patchs_list.append((self.transaction_id, \
									self.json_source['servers']['server_{0}'.format(i)]['server_id'], \
									self.json_source['servers']['server_{0}'.format(i)]['patch_{num}'.format(num = j)]['order_num'], \
									self.json_source['servers']['server_{0}'.format(i)]['patch_{num}'.format(num = j)]['patch']))
			logging.info('Process config: {patch}'.format(patch = patchs_list))
			self.servers.append(patchs_list)
			if not os.path.exists('servers/{folder}'.format(folder = self.servers[i][0][1])):
				os.makedirs('servers/{folder}'.format(folder = self.servers[i][0][1]))
				logging.debug('Creation of server folder for {serv}'.format(serv = self.servers[i][0][1]))
			if not os.path.exists('servers/{folder}/{id}.lock'.format(folder = self.servers[i][0][1], id = self.servers[i][0][1])):
				with open('servers/{folder}/{id}.lock'.format(folder = self.servers[i][0][1], id = self.servers[i][0][1]), 'w') as lock_file:
					lock_file.write('test,0,test')
				lock_file.close()
				logging.debug('Creation of server lock file for {serv}'.format(serv = self.servers[i][0][1]))
		self.initialized = True


	def check_status(self, transaction_id, server_id, patch_num):
		"""Checking is it possible to initiate installation of the next patch or not.
		Verifying lock file for the last row in it. and checking it's status."""
		with open('servers/{server_id}/{server_id}.lock'.format(server_id = server_id), 'r') as lock_file:
			arr = lock_file.readlines()
		lock_file.close()
		server_info = tuple(str([item for item in arr if item != '\n'][-1]).strip(' \t\n\r').split(','))
		logging.info('Checking status for {info}'.format(info = server_info))
		if (server_info[2] == 'SUCCESSFUL' and int(server_info[1]) == patch_num and server_info[0] == transaction_id) or patch_num == -1:
			logging.debug('Status for {id}, {serv}, {patch}=True'.format(id = transaction_id, serv = server_id, patch = patch_num))
			return True
		else:
			logging.debug('Status for {id}, {serv}, {patch}=False'.format(id = transaction_id, serv = server_id, patch = patch_num))
			return False
		

	@staticmethod
	def get_status(transaction_id, server_id, order_num):
		"""Getting status for the patch installation. lock file holds status.
		Or status may ne pending in case there is no any processing for current patch in te lock file."""
		with open('servers/{server_id}/{server_id}.lock'.format(server_id = server_id), 'r') as lock_file:
			arr = lock_file.readlines()
		lock_file.close()
		arr = [item.split(',') for item in arr]
		for i in xrange(len(arr)-1, -1, -1):
			if transaction_id == arr[i][0] and order_num == int(arr[i][1]):
				logging.debug('Status for {id}, {serv}, {ord}={status}'.format(id = transaction_id, serv = server_id, ord = order_num, status = arr[i][2]))
				return arr[i][2]
				break
		logging.debug('Status for {id}, {serv}, {ord}=PENDING'.format(id = transaction_id, serv = server_id, ord = order_num))
		return 'PENDING'

	def build_responce(self):
		"""Generating json response with statusesfor each patch installation process."""
		for server_key in self.json_source['servers'].keys():
			for patch_key in self.json_source['servers'][server_key].keys():
				if 'patch' in patch_key:
					curr_status = self.__class__.get_status(self.transaction_id, self.json_source['servers'][server_key]['server_id'], self.json_source['servers'][server_key][patch_key]['order_num'])
					self.json_source['servers'][server_key][patch_key]['status'] = curr_status
					logging.debug('Server: {serv}, patch_key: {patch}, status={status}'.format(serv= server_key, patch = patch_key, status = curr_status))
		return str(self.json_source).replace('\'','"').replace('u"', '"')


	def run_installation(self):
		"""Initiate installation process as a distinct subproces"""
		for i in xrange(len(self.servers)):
			for j in xrange(len(self.servers[i])):
				transaction_id = self.servers[i][j][0]
				server_id = self.servers[i][j][1]
				patch_num = self.servers[i][j][2]-1
				patch = self.servers[i][j][3]
				if self.check_status(transaction_id, server_id, patch_num):
					pp = InstallationProcess()
					command = ['C:\Python27\python.exe','installer.py', transaction_id, server_id, str(patch_num+1), patch]
					subprocess = reactor.spawnProcess(pp, command[0], command, env=os.environ)
					print "Process for {pid} started..".format(pid = pp.pid)
					logging.info("Process for {pid} started with following params: {params}".format(pid = pp.pid, params = repr(self.servers[i][j])))
					del self.servers[i][j]
					logging.debug(self.servers)
					break