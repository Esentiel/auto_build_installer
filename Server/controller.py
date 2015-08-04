
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

		# 1. create folders for each server_id
		# 2. create lock file(empty). mask is [order_number],[status]

	def get_status(self, server_id):
		pass
		# parse file and return last row as ([order_num], [status]) or None in case file is empty