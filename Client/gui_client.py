import uuid, json, sys, paramiko
from Tkinter import *
from console_client import InstProtocol, InstFactory, host, port
from twisted.internet import reactor

class JsonGenerator(object):
	"""docstring for JsonGenerator"""
	def __init__(self):
		super(JsonGenerator, self).__init__()
		self.json_dict = {}
		self.json_dict['transaction_id'] = str(uuid.uuid4())
		# self.json_dict['end'] = 1
		self.json_dict['servers'] = {}

	def add_server(self,server_id, order_num):
		server_num = 'server_{num}'.format(num = order_num)
		self.json_dict['servers'][server_num] = {}
		self.json_dict['servers'][server_num]['server_id'] = server_id

	def add_patch(self, server_order_num, patch_order_num, patch):
		patch_num = 'patch_{num}'.format(num = patch_order_num)
		self.json_dict['servers'][server_order_num][patch_num] = {}
		self.json_dict['servers'][server_order_num][patch_num]['order_num'] = patch_order_num
		self.json_dict['servers'][server_order_num][patch_num]['patch'] = patch

	def dump_to_file(self):
		with open('install_qeue.json', 'w') as fp:
			json.dump(self.json_dict, fp)
		fp.close()

	def get_server_num(self, server_id):
		for i in xrange(len(self.json_dict['servers'].keys())):
			if self.json_dict['servers']['server_{0}'.format(i)]['server_id'] == server_id:
				return 'server_{0}'.format(i)
		return None

	def get_json(self):
		return self.json_dict

	def get_patch_num(self, server_id):
		curr_num = len([patch for patch in self.json_dict['servers'][server_id].keys() if 'patch' in patch])
		return curr_num

	def get_server_num_exactly(self):
		curr_num = len([server for server in self.json_dict['servers'].keys() if 'server_' in server])
		return curr_num

class Application(Frame):

	@classmethod
	def get_servers_list(cls):
		with open('\\\\vm-bee.netcracker.com\config\list.txt', 'r') as the_config:
			cls.servers_list = the_config.read().replace('instance_id=','').split(',')
		the_config.close()

	@classmethod
	def get_deliverables_list(cls):
		client_ftp = paramiko.SSHClient()
		client_ftp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client_ftp.connect(hostname='ftp.netcracker.com', username='dhl_ro', password = 'XXqiI3nY', port=22)
		sftp_ftp = client_ftp.open_sftp()
		cls.deliverables_list = sftp_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables')
		client_ftp.close()

	def createWidgets(self, order=0):
		var_server = StringVar(self)
		if order == 0:
			var_server.set(self.servers_list[0])
		else:
			var_server.set(self.qeue[order-1]['server_id'].get())
		server = apply(OptionMenu, (self, var_server) + tuple(self.servers_list))
		server.grid(row=order+1, column=1, pady=5, padx = 5)

		var_deliverable = StringVar(self)
		var_deliverable.set(self.deliverables_list[0])
		deliverable = apply(OptionMenu, (self, var_deliverable) + tuple(self.deliverables_list))
		deliverable.grid(row=order+1, column=2, pady=5, padx = 5)

		calc_button = Button(self, text="ci_builds", width=8, command=lambda order = order: self.build_patchs_list(order, light=True))
		calc_button.grid(row=order+1, column=3, pady=5, padx = 5)
		
		var_patch = StringVar(self)
		patch = apply(OptionMenu, (self, var_patch, ()))
		patch.grid(row=order+1, column=4, pady=5, padx = 5)

		calc_button = Button(self, text="more", width=8, command=lambda order = order: self.build_patchs_list(order, light=False))
		calc_button.grid(row=order+1, column=5, pady=5, padx = 5)

		var_status = StringVar()
		label = Label( self, textvariable=var_status, relief=RAISED )
		var_status.set("PLANNED")
		label.grid(row=order+1, column=6, pady=5, padx = 5)

		the_row = {}
		the_row['server_id'] = var_server
		the_row['deliverable'] = var_deliverable
		the_row['var_patch'] = var_patch
		the_row['patch'] = patch
		the_row['status'] = var_status
		self.qeue.append(the_row)

		self.order+=1

	def get_deliverable_selected(self, order=0):
		return self.qeue[order]['deliverable'].get()

	def build_patchs_list(self, order=0, light=False):
		deliverable = self.get_deliverable_selected(order)
		client_ftp = paramiko.SSHClient()
		client_ftp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client_ftp.connect(hostname='ftp.netcracker.com', username='dhl_ro', password = 'XXqiI3nY', port=22)
		sftp_ftp = client_ftp.open_sftp()
		try:
			patches_list = sftp_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci_builds/'.format(deliv = deliverable))
		except:
			patches_list = sftp_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci-builds/'.format(deliv = deliverable))
		client_ftp.close()
		patches_list = [rev.replace('_autoinstaller.zip', '') for rev in list(reversed(patches_list)) if 'autoinstaller.zip' in rev and '.folder' not in rev]

		self._reset_option_menu(patches_list, order, 0, light)

	def _reset_option_menu(self, options, order=0, index=None, light=False):
		menu = self.qeue[order]['patch']["menu"]
		menu.delete(0, "end")
		if not light:
			for string in options:
				menu.add_command(label=string, 
								 command=lambda value=string:
									  self.qeue[order]['var_patch'].set(value))
		else:
			for i in xrange(11):
				menu.add_command(label=options[i], 
								 command=lambda value=options[i]:
									  self.qeue[order]['var_patch'].set(value))
		if index is not None:
			self.qeue[order]['var_patch'].set(options[index])

	def create_new_button(self):
		start_button = Button(self, text="Start", width=12, command=self.generate_json)
		start_button.grid(row=0, column=0, pady=15, padx = 15)
		stop_button = Button(self, text="Stop", width=12, command=self.close_connection)
		stop_button.grid(row=0, column=1, pady=15, padx = 15)
		reset_button = Button(self, text="Reset", width=12, command=lambda: self.reinit(self.reactor, self.master))
		reset_button.grid(row=0, column=2, pady=15, padx = 15)
		new_button = Button(self, text="New Server", width=12, command=lambda: self.createWidgets(self.order))
		new_button.grid(row=1, column=0, pady=5, padx = 30)
	
	def create_client(self):
		self.client = InstFactory(self.reactor, self.update_status)

	def __init__(self, reactor, master=None):
		self.master = master
		Frame.__init__(self, master)
		try:
			sys.remove('install_qeue.json')
		except:
			pass
		self.reactor = reactor
		self.qeue = []
		self.order = 0
		Application.get_servers_list()
		Application.get_deliverables_list()
		self.grid(row=0, column=0)
		self.create_new_button()
		self.createWidgets()
		self.create_client()

	def connect_client(self):
		self.connection = self.reactor.connectTCP(host, port, self.client)

	def close_connection(self):
		self.connection.disconnect()

	def reinit(self, reactor, master=None):
		self.__init__(self.reactor, self.master)


	def generate_json(self):
		client_ftp = paramiko.SSHClient()
		client_ftp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client_ftp.connect(hostname='ftp.netcracker.com', username='dhl_ro', password = 'XXqiI3nY', port=22)
		sftp_ftp = client_ftp.open_sftp()
		json_obj = JsonGenerator()
		for i in xrange(len(self.qeue)):
			server_num = json_obj.get_server_num(self.qeue[i]['server_id'].get())
			if not server_num:
				server_order_num = json_obj.get_server_num_exactly()
				json_obj.add_server(self.qeue[i]['server_id'].get(), server_order_num)
				server_num = json_obj.get_server_num(self.qeue[i]['server_id'].get())
			patch_order_num = json_obj.get_patch_num(server_num)
			try:
				sftp_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci_builds/'.format(deliv = self.qeue[i]['deliverable'].get()))
				patch = 'ftp.netcracker.com/ftp/Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci_builds/{patch}_autoinstaller.zip'.format(deliv = self.qeue[i]['deliverable'].get(), patch = self.qeue[i]['var_patch'].get())
			except:
				patches_list = sftp_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci-builds/'.format(deliv = self.qeue[i]['deliverable'].get()))
				patch = 'ftp.netcracker.com/ftp/Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci-builds/{patch}_autoinstaller.zip'.format(deliv = self.qeue[i]['deliverable'].get(), patch = self.qeue[i]['var_patch'].get())
			json_obj.add_patch(server_num, patch_order_num, patch)
		client_ftp.close()
		json_obj.dump_to_file()

		self.connect_client()


	def update_status(self, response):
		for i in xrange(len(response)):
			for j in xrange(len(self.qeue)):
				if response[i]['server_id'] == self.qeue[j]['server_id'].get() and response[i]['patch'] == self.qeue[j]['var_patch'].get():
					self.qeue[j]['status'].set(response[i]['status'])
