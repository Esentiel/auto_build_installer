
import os, json

class InstallProc(object):
	"""docstring for InstallProc"""
	def __init__(self, json_source):
		self.json_source = json_source
		self.servers_num = int(len(self.json_source['servers'].keys()))
		self.transaction_id = self.json_source['transaction_id']
		self.servers = []
		for i in xrange(self.servers_num):
			patchs_num = len(self.json_source['servers']['server_{num}'.format(num = i)].keys())-1
			patchs_list = []
			for j in xrange(patchs_num):
				patchs_list.append((self.transaction_id, \
									self.json_source['servers']['server_{0}'.format(i)]['server_id'], \
									self.json_source['servers']['server_{0}'.format(i)]['patch_{num}'.format(num = j)]['order_num'], \
									self.json_source['servers']['server_{0}'.format(i)]['patch_{num}'.format(num = j)]['patch']))
			self.servers.append(patchs_list)
			if not os.path.exists('servers/{folder}'.format(folder = self.servers[i][0][1])):
				os.makedirs('servers/{folder}'.format(folder = self.servers[i][0][1]))
			if not os.path.exists('servers/{folder}/{id}.lock'.format(folder = self.servers[i][0][1], id = self.servers[i][0][1])):
				with open('servers/{folder}/{id}.lock'.format(folder = self.servers[i][0][1], id = self.servers[i][0][1]), 'w') as lock_file:
					lock_file.write('start')
				lock_file.close()


	def get_status(self, transaction_id, server_id, patch_num):
		with open('servers/{server_id}/{server_id}.lock'.format(server_id = server_id), 'r') as lock_file:
			arr = lock_file.readlines()
		lock_file.close()
		server_info = tuple(str([item for item in arr if item != '\n'][-1]).strip(' \t\n\r').split(','))
		if (server_info[2] == 'SUCCESSFUL' and int(server_info[1]) == patch_num and server_info[0] == transaction_id) or patch_num == -1:
			return True
		else:
			return False
		# parse file and return last row as ([transaction_id], [order_num], [status]) or None in case file is empty

	@staticmethod
	def get_progress(transaction_id, server_id, order_num):
		if not os.path.exists('servers/{server_id}.lock'.format(server_id = server_id)):
			return 'PENDING'
		else:
			with open('servers/{server_id}.lock'.format(server_id = server_id), 'r') as lock_file:
				arr = lock_file.readlines()
			lock_file.close()
			for i in xrange(len(arr), -1, -1):
				if transaction_id == arr[i][0] and order_num == arr[i][1]:
					return arr[i][2]
					break
			return 'PENDING'

	def build_responce(self):
		for server_key in self.json_source['servers'].keys():
			for patch_key in self.json_source['servers'][server_key].keys():
				if 'patch' in patch_key:
					curr_status = self.__class__.get_progress(self.transaction_id, server_key, self.json_source['servers'][server_key][patch_key]['order_num'])
					self.json_source['servers'][server_key][patch_key]['status'] = curr_status

		return str(self.json_source).replace('\'','"').replace('u"', '"')