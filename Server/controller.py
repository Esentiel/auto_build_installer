
class InstallProc(object):
	"""docstring for InstallProc"""
	def __init__(self, json_source):
		self.json_source = json_source
		self.servers_num = int(len(self.json_source.keys()))
		for i in xrange(self.servers_num):
			patchs_num = len(self.json_source['servers']['server_{num}'.format(num = i)].keys())-1
			patchs_list = []
			for j in xrange(patchs_num):
				patchs_list.append((self.json_source['servers']['server_{0}'.format(i)]['server_id'], \
									self.json_source['servers']['server_{0}'.format(i)]['patch_{num}'.format(num = j)]['order_num'], \
									self.json_source['servers']['server_{0}'.format(i)]['patch_{num}'.format(num = j)]['patch']))
			self.__dict__['server_{0}'.format(i)] = patchs_list
			if not os.path.exists('servers/{folder}'.format(self.__dict__['server_{0}'.format(i)][1])):
    			os.makedirs('servers/{folder}'.format(self.__dict__['server_{0}'.format(i)][1]))
    		if not os.path.exists('servers/{folder}/{id}'.format(self.__dict__['server_{0}'.format(i)][1], self.__dict__['server_{0}'.format(i)][0])):
    			with open('servers/{folder}/{id}.lock'.format(self.__dict__['server_{0}'.format(i)][1], self.__dict__['server_{0}'.format(i)][0]), 'w') as lock_file:
    				lock_file.write('start')
    			lock_file.close()
		# created lock file(empty). mask is [order_number],[status]

	def get_status(self, server_id, patch_num):
		if not os.path.exists('servers/{server_id}.lock'.format(server_id = server_id)):
			return True
		else:
			with open('servers/{server_id}.lock'.format(server_id = server_id), 'r') as lock_file:
   				arr = lock_file.readlines()
			lock_file.close()
			server_info = tuple(str([item for item in arr if item != '\n'][-1]).strip(' \t\n\r').split(', '))
			if server_info[1] == 'PASSED' and (int(server_info[0]) == patch_num or patch_num = -1):
				return True
			else:
				return False
		# parse file and return last row as ([order_num], [status]) or None in case file is empty