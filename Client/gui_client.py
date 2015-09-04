"""Module implements GUI client for the program.
Main goals: generate JSON file, Initiate network communication process, provide user with actual statuses
Also it is possible to stop proces and rerun it in case of need"""
from Tkinter import StringVar, OptionMenu, Button, Label, Frame, RAISED
from socket_client import InstallationProtocol, InstallationFactory, host, port
from PIL import ImageTk, Image
import uuid, json, sys, paramiko, threading, logging

class SSHConnectionSingleton(type):
	"""docstring for SSHConnectionSingleton"""
	def __init__(cls, *args, **kwargs):
		cls.__instance = None
		cls.__lock = threading.Lock()

	def __call__(cls, *args, **kwargs):

		if not cls.__instance:
			with cls.__lock:
				if not cls.__instance:
					cls.__instance = super(SSHConnectionSingleton, cls).__call__(*args, **kwargs)
		return cls.__instance

class SSHClient(object):
	lock = threading.Lock()
	__metaclass__ = SSHConnectionSingleton
	client = paramiko.SSHClient()
	"""docstring for SSHClient"""
	def __init__(self):
		super(SSHClient, self).__init__()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.connect(hostname='ftp.netcracker.com', username='dhl_ro', password = 'XXqiI3nY', port=22)
		self.sftp_ftp = self.client.open_sftp()

	def listdir(self, path):
		with self.lock:
			listdir = self.sftp_ftp.listdir(path)
		return listdir


class JsonGenerator(object):
	"""Class for JSON file generating"""
	def __init__(self):
		super(JsonGenerator, self).__init__()
		self.json_dict = {}
		self.json_dict['transaction_id'] = str(uuid.uuid4())
		self.json_dict['servers'] = {}
		logging.info('generating json. id = {id}'.format(id = self.json_dict['transaction_id']))

	def add_server(self,server_id, order_num):
		server_num = 'server_{num}'.format(num = order_num)
		self.json_dict['servers'][server_num] = {}
		self.json_dict['servers'][server_num]['server_id'] = server_id
		logging.debug('server added: order_num: {ord}, id = {id}'.format(ord = order_num, id = server_id))

	def add_patch(self, server_order_num, patch_order_num, patch):
		patch_num = 'patch_{num}'.format(num = patch_order_num)
		self.json_dict['servers'][server_order_num][patch_num] = {}
		self.json_dict['servers'][server_order_num][patch_num]['order_num'] = patch_order_num
		self.json_dict['servers'][server_order_num][patch_num]['patch'] = patch
		logging.debug('patch added: server = {server_num}, order_num = {ord}, patch = {p}'.format(server_num = server_order_num, ord = patch_order_num, p = patch))

	def dump_to_file(self):
		with open('install_queue.json', 'w') as fp:
			json.dump(self.json_dict, fp)
			logging.info('dump file generated')
			logging.debug('info to file: {jdict}'.format(jdict = self.json_dict))
		fp.close()

	def server_exists(self, server_id):
		for i in xrange(len(self.json_dict['servers'].keys())):
			if self.json_dict['servers']['server_{0}'.format(i)]['server_id'] == server_id:
				logging.debug('server_exists returns {num}'.format(num = i))
				return 'server_{0}'.format(i)
		logging.debug('server_exists returns None')
		return None

	def get_patch_num(self, server_id):
		curr_num = len([patch for patch in self.json_dict['servers'][server_id].keys() if 'patch' in patch])
		logging.debug('get_patch_num returns {num}'.format(num = curr_num))
		return curr_num

	def get_servers_number(self):
		curr_num = len([server for server in self.json_dict['servers'].keys() if 'server_' in server])
		logging.debug('get_servers_number returns {num}'.format(num = curr_num))
		return curr_num

class Application(Frame):
	"""Implements main GUI front-end. All the buttons, lists and so on.
	Also it implements communication with socket client."""
	@classmethod
	def get_servers_list(cls):
		"""Getting servers list"""
		with open('\\\\vm-bee.netcracker.com\config\list.txt', 'r') as the_config:
			cls.servers_list = the_config.read().replace('instance_id=','').split(',')
			logging.info('server list was calculated: {slist}'.format(slist = cls.servers_list))
		the_config.close()

	@classmethod
	def get_deliverables_list(cls):
		"""Getting deliverable folders list"""
		client_ftp = SSHClient()
		deliverables_list = client_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables')
		cls.deliverables_list = [deliverable for deliverable in deliverables_list if 'Migration.Core.1' in  deliverable or 'PPS.1' in deliverable or 'PH1.Migration.SmokeTest' in deliverable or 'PPS.9' in deliverable or 'RefData' in deliverable or 'data-duplicator' in deliverable]
		
		logging.info('deliverables list was calculated')
		logging.debug('deliverables list: {dlist}'.format(dlist = cls.deliverables_list))

	def createWidgets(self, order=0):
		"""Drawing mmost part of UI: INstallationn Row: Server dropdown deliverable dropdown, patches dropdown,
		buttons to display patches list, statuses layer"""
		logging.info('Starting createWidgets...')
		widgets_row = []
		var_server = StringVar(self)
		if order == 0:
			var_server.set(self.servers_list[0])
		else:
			var_server.set(self.queue[order-1]['server_id'].get())
		server = apply(OptionMenu, (self, var_server) + tuple(self.servers_list))
		server.grid(row=order+1, column=1, pady=5, padx = 5)

		widgets_row.append(server)

		var_deliverable = StringVar(self)
		var_deliverable.set(self.deliverables_list[0])
		deliverable = apply(OptionMenu, (self, var_deliverable) + tuple(self.deliverables_list))
		deliverable.grid(row=order+1, column=2, pady=5, padx = 5)
		widgets_row.append(deliverable)

		calc_button_light = Button(self, text="ci_builds", width=8, command=lambda: threading.Thread(target=self.build_patches_list, args=(order, True)).start())
		calc_button_light.grid(row=order+1, column=3, pady=5, padx = 5)

		widgets_row.append(calc_button_light)
		
		var_patch = StringVar(self)
		patch = apply(OptionMenu, (self, var_patch, ()))
		patch.grid(row=order+1, column=4, pady=5, padx = 5)

		widgets_row.append(patch)

		calc_button = Button(self, text="more", width=8, command=lambda: threading.Thread(target=self.build_patches_list, args=(order, False)).start())
		calc_button.grid(row=order+1, column=5, pady=5, padx = 5)

		widgets_row.append(calc_button)

		var_status = StringVar()
		label = Label( self, textvariable=var_status, relief=RAISED )
		var_status.set("PLANNED")
		label.grid(row=order+1, column=6, pady=5, padx = 5)

		widgets_row.append(label)

		self.widgets.append(widgets_row)

		the_row = {}
		the_row['server_id'] = var_server
		the_row['deliverable'] = var_deliverable
		the_row['var_patch'] = var_patch
		the_row['patch'] = patch
		the_row['status'] = var_status
		self.queue.append(the_row)
		logging.debug('The row of Widgets[{ord}]: {row}'.format(ord = order, row = the_row))

		self.order+=1

	def get_deliverable_selected(self, order=0):
		logging.debug('get_deliverable_selected returns {deliv}'.format(deliv = self.queue[order]['deliverable'].get()))
		return self.queue[order]['deliverable'].get()

	def build_patches_list(self, order=0, light=False):
		deliverable = self.get_deliverable_selected(order)
		client_ftp = SSHClient()
		try:
			patches_list = client_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci_builds/'.format(deliv = deliverable))
		except:
			try:
				patches_list = client_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci-builds/'.format(deliv = deliverable))
			except:
				patches_list = client_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_manual_builds/'.format(deliv = deliverable))
		patches_list = [rev.replace('_autoinstaller.zip', '') for rev in list(reversed(patches_list)) if 'autoinstaller.zip' in rev and '.folder' not in rev]
		logging.debug('patches_list = {plist}'.format(plist = patches_list))
		self._reset_option_menu(patches_list, order, 0, light)

	def _reset_option_menu(self, options, order=0, index=None, light=False):
		menu = self.queue[order]['patch']["menu"]
		menu.delete(0, "end")
		logging.info('reseting menu options')
		if not light:
			for string in options:
				menu.add_command(label=string, 
								 command=lambda value=string:
									  self.queue[order]['var_patch'].set(value))
		else:
			if len(options)< 11:
				the_len = len(options)
			else:
				the_len = 11
			for i in xrange(the_len):
				menu.add_command(label=options[i], 
								 command=lambda value=options[i]:
									  self.queue[order]['var_patch'].set(value))
		if index is not None:
			self.queue[order]['var_patch'].set(options[index])

	def create_buttons(self):
		logging.info('Creating buttons...')
		start_button = Button(self, text="Start", width=12, command=lambda: threading.Thread(target=self.generate_json).start())
		start_button.grid(row=0, column=0, pady=15, padx = 15)
		stop_button = Button(self, text="Stop", width=12, command=self.close_connection)
		stop_button.grid(row=0, column=1, pady=15, padx = 15)
		reset_button = Button(self, text="Delete Last", width=12, command=lambda: threading.Thread(target=self.delete_last_row).start())
		reset_button.grid(row=0, column=2, pady=15, padx = 15)
		reset_button = Button(self, text="Reset", width=12, command=lambda: threading.Thread(target=self.reinit, args=(self.reactor, self.master)).start())
		reset_button.grid(row=0, column=3, pady=15, padx = 15)
		
		new_button = Button(self, text="New Server", width=12, command=lambda: self.createWidgets(self.order))
		new_button.grid(row=1, column=0, pady=5, padx = 30)
		logging.info('Buttons werecreated')
	
	def create_client(self):
		self.client = InstallationFactory(self.reactor, self.update_status)
		logging.info('Establishing Network Client...')

	def __init__(self, reactor, master=None):
		self.master = master
		Frame.__init__(self, master)
		try:
			sys.remove('install_queue.json')
		except:
			pass
		self.reactor = reactor
		self.queue = []
		self.widgets = []
		self.order = 0
		Application.get_servers_list()
		Application.get_deliverables_list()
		self.grid(row=0, column=0)
		self.create_buttons()
		self.create_client()
		self.createWidgets()
		self.put_girl_on()
		

	def connect_client(self):
		logging.info('Connection to the Server...')
		self.connection = self.reactor.connectTCP(host, port, self.client)

	def close_connection(self):
		logging.info('Closing connection...')
		self.connection.disconnect()

	def reinit(self, reactor, master=None):
		"""reset all the config"""
		logging.info('Reinit was intiated')
		for i in xrange(len(self.widgets)-1,0,-1):
			for j in range(len(self.widgets[i])):
				self.widgets[i][j].destroy()
				# self.queue[i][j].destroy()
			del self.widgets[i]
			del self.queue[i]
		logging.debug(self.order)
		self.order = 1

	def delete_last_row(self):
		logging.debug('Last rows deletion')
		if len(self.widgets) > 1:
			for j in xrange(len(self.widgets[-1])):
				self.widgets[-1][j].destroy()
			del self.widgets[-1]
			del self.queue[-1]
			logging.debug(self.order)
			self.order-=1


	def generate_json(self):
		client_ftp = SSHClient()
		json_obj = JsonGenerator()
		for i in xrange(len(self.queue)):
			server_num = json_obj.server_exists(self.queue[i]['server_id'].get())
			if not server_num:
				server_order_num = json_obj.get_servers_number()
				json_obj.add_server(self.queue[i]['server_id'].get(), server_order_num)
				server_num = json_obj.server_exists(self.queue[i]['server_id'].get())
			patch_order_num = json_obj.get_patch_num(server_num)
			try:
				client_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci_builds/'.format(deliv = self.queue[i]['deliverable'].get()))
				patch = 'ftp.netcracker.com/ftp/Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci_builds/{patch}_autoinstaller.zip'.format(deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())
			except:
				try:
					patches_list = client_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci-builds/'.format(deliv = self.queue[i]['deliverable'].get()))
					patch = 'ftp.netcracker.com/ftp/Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_ci-builds/{patch}_autoinstaller.zip'.format(deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())
				except:
					patches_list = client_ftp.listdir(path='./Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_manual_builds/'.format(deliv = self.queue[i]['deliverable'].get()))
					patch = 'ftp.netcracker.com/ftp/Projects/DHL/IM.GRE_CP/_Internal_Deliverables/{deliv}/_manual_builds/{patch}_autoinstaller.zip'.format(deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())
			json_obj.add_patch(server_num, patch_order_num, patch)
		
		json_obj.dump_to_file()

		self.connect_client()

	def put_girl_on(self):
		logging.info('Sexy lady')
		img_frame = Frame(self.master)
		img_frame.grid(row=4, column=0)
		try:
			img = ImageTk.PhotoImage(Image.open("girl.jpg"))
		except:
			logging.error('girl.jpg is absent in client folder')
			raise
		panel = Label(img_frame, image = img)
		panel.image = img
		panel.grid(row=0, column=0)


	def update_status(self, response):
		logging.info('Updating statuses')
		for i in xrange(len(response)):
			for j in xrange(len(self.queue)):
				if response[i]['server_id'] == self.queue[j]['server_id'].get() and response[i]['patch'] == self.queue[j]['var_patch'].get():
					self.queue[j]['status'].set(response[i]['status'])
		logging.debug('new queue after updating statuses: {q}'.format(q = self.queue))
