import json

class Instance:
	"""Getting all instance params based on instance name
	All necessary information are taken from JSON file"""
	def __init__(self, name):
		with open("config.json", 'r') as json_file:
			self.json_data = json.load(json_file)
		json_file.close()
		self.instance_name = name
		self.instance = self.json_data[self.instance_name]
		self.app_host = self.instance['app_host']
		self.app_port = self.instance['app_port']
		self.ssh_port = self.instance['ssh_port']
		self.db_host = self.instance['db_host']
		self.db_port = self.instance['db_port']
		self.db_sid = self.instance['db_sid']
