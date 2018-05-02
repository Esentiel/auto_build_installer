"""Module implements GUI client for the program.
Main goals: generate JSON file, Initiate network communication process, provide user with actual statuses
Also it is possible to stop proces and rerun it in case of need"""
from Tkinter import StringVar, OptionMenu, Button, Label, Frame, RAISED, Toplevel, Text, END, INSERT, TclError
from socket_client import InstallationProtocol, InstallationFactory, LogFactory
from config import serv_list, cc_list, ftp_root, ftp_root_extnd, delivs, host, port, log_port
from PIL import ImageTk, Image
import uuid, json, sys, paramiko, threading, logging, time, glob, socket, os, re

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
		self.connect()		

	def connect(self):
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.connect(hostname='ftp.netcracker.com', username='dhl_ro', password = 'yourpassword', port=22)
		self.sftp_ftp = self.client.open_sftp()

	def listdir(self, path):
		try:
			with self.lock:
				listdir = self.sftp_ftp.listdir(path)
			return listdir
		except socket.error:
			self.client.close()
			self.connect()
			with self.lock:
				listdir = self.sftp_ftp.listdir(path)
			return listdir
	def stat(self, path):
		try:
			with self.lock:
				self.sftp_ftp.stat(path)
			return True
		except socket.error:
			self.client.close()
			self.connect()
			try:
				with self.lock:
					self.sftp_ftp.stat(path)
			except IOError, e:
				if e[0] == 2:
					return False
		except IOError, e:
			if e[0] == 2:
				return False

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

	def add_patch(self, server_order_num, patch_order_num, patch, cc):
		patch_num = 'patch_{num}'.format(num = patch_order_num)
		self.json_dict['servers'][server_order_num][patch_num] = {}
		self.json_dict['servers'][server_order_num][patch_num]['order_num'] = patch_order_num
		self.json_dict['servers'][server_order_num][patch_num]['patch'] = patch
		self.json_dict['servers'][server_order_num][patch_num]['cc'] = cc
		logging.debug('patch added: server = {server_num}, order_num = {ord}, patch = {p}, cc= {cc}'.format(server_num = server_order_num, ord = patch_order_num, p = patch, cc = cc))

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
		with open(serv_list, 'r') as the_config:
			cls.servers_list = the_config.read().replace('instance_id=','').split(',')
			logging.info('server list was calculated: {slist}'.format(slist = cls.servers_list))
		the_config.close()

	@classmethod
	def get_cc_list(cls):
		"""comment here"""
		with open(cc_list, 'r') as the_config:
			cls.cc_list = re.sub(r':[\d]+', '', the_config.read()).split('\n')
			logging.info('server list was calculated: {slist}'.format(slist = cls.cc_list))
		the_config.close()


	@classmethod
	def get_deliverables_list(cls):
		"""Getting deliverable folders list"""
		client_ftp = SSHClient()
		deliverables_list = client_ftp.listdir(path=ftp_root)
		cls.deliverables_list = []
		for deliverable in deliverables_list:
			for dev in delivs:
				if dev in deliverable:
					cls.deliverables_list.append(deliverable)
		cls.deliverables_list = list(set(cls.deliverables_list))
		cls.deliverables_list.sort()

		logging.info('deliverables list was calculated')
		logging.debug('deliverables list: {dlist}'.format(dlist = cls.deliverables_list))

	def createWidgets(self, order=0):
		"""Drawing mmost part of UI: INstallationn Row: Server dropdown deliverable dropdown, patches dropdown,
		buttons to display patches list, statuses layer"""
		logging.info('Starting createWidgets...')
		widgets_row = []
		the_row = {}

		widgets_row.append(Button(self, text="Delete Row", width=12, command=lambda order=order: self.delete_row(order)))
		widgets_row[0].grid(row=order+1, column=0, pady=5, padx = 15)


		the_row['cc'] = StringVar(self)
		if order == 0:
			the_row['cc'].set(self.cc_list[0])
		else:
			the_row['cc'].set(self.queue[order-1]['cc'].get())
		
		widgets_row.append(apply(OptionMenu, (self, the_row['cc']) + tuple(self.cc_list)))
		widgets_row[1].grid(row=order+1, column=1, pady=5, padx = 5)


		the_row['server_id'] = StringVar(self)
		if order == 0:
			the_row['server_id'].set(self.servers_list[0])
		else:
			the_row['server_id'].set(self.queue[order-1]['server_id'].get())
		widgets_row.append(apply(OptionMenu, (self, the_row['server_id']) + tuple(self.servers_list)))
		widgets_row[2].grid(row=order+1, column=2, pady=5, padx = 5)

		the_row['deliverable'] = StringVar(self)
		the_row['deliverable'].set(self.deliverables_list[0])
		widgets_row.append(apply(OptionMenu, (self, the_row['deliverable']) + tuple(self.deliverables_list)))
		widgets_row[3].grid(row=order+1, column=3, pady=5, padx = 5)

		the_row['trace'] = the_row['deliverable'].trace('w', lambda a,b,c: threading.Thread(target=self.build_patches_list, args=(order, True)).start())

		the_row['var_patch'] = StringVar(self)
		widgets_row.append(apply(OptionMenu, (self, the_row['var_patch'], ())))
		widgets_row[4].grid(row=order+1, column=4, pady=5, padx = 5)
		the_row['patch'] = widgets_row[4]



		widgets_row.append(Button(self, text="more", width=8, command=lambda order = order: self.build_patches_list(order, False)))
		widgets_row[5].grid(row=order+1, column=5, pady=5, padx = 5)

		widgets_row.append(Button(self, text="Show Log", width=8, command=lambda order = order: self.show_log(order)))
		widgets_row[6].grid(row=order+1, column=6, pady=5, padx = 5)

		the_row['status'] = StringVar()
		widgets_row.append(Label( self, textvariable=the_row['status'], width=15))
		the_row['status'].set("PLANNED")
		widgets_row[7].grid(row=order+1, column=7, pady=5, padx = 5)	

		self.widgets.append(widgets_row)

		
		self.queue.append(the_row)
		logging.debug('The row of Widgets[{ord}]: {row}'.format(ord = order, row = the_row))

		# self.order+=1

	def get_deliverable_selected(self, order=0):
		logging.debug('get_deliverable_selected returns {deliv}'.format(deliv = self.queue[order]['deliverable'].get()))
		return self.queue[order]['deliverable'].get()

	def build_patches_list(self, order=0, light=False):
		deliverable = self.get_deliverable_selected(order)
		client_ftp = SSHClient()
		patches_list = []
		prod_patches_list = []
		try:
			prod_patches_list = client_ftp.listdir(path='{root}/{deliv}/_Product.part/'.format(root = ftp_root, deliv = deliverable))
			prod_patches_list = [rev.replace('.zip', '') for rev in list(reversed(prod_patches_list)) if '.PD_' in rev and '.folder' not in rev]
		except:
			pass
		try:
			patches_list = client_ftp.listdir(path='{root}/{deliv}/_ci_builds/'.format(root = ftp_root, deliv = deliverable))
			patches_list = [rev.replace('.zip', '') for rev in list(reversed(patches_list)) if 'autoinstaller.zip' in rev and '.folder' not in rev]
		except:
			pass
		try:
			patches_list = client_ftp.listdir(path='{root}/{deliv}/_ci-builds/'.format(root = ftp_root, deliv = deliverable))
			patches_list = [rev.replace('.zip', '') for rev in list(reversed(patches_list)) if 'autoinstaller.zip' in rev and '.folder' not in rev]
		except:
			pass
		try:
			patches_list = client_ftp.listdir(path='{root}/{deliv}/_manual_builds/'.format(root = ftp_root, deliv = deliverable))
			patches_list = [rev.replace('.zip', '') for rev in list(reversed(patches_list)) if 'autoinstaller.zip' in rev and '.folder' not in rev]
		except:
			pass
		
		patches_list = prod_patches_list+patches_list
		logging.debug('patches_list = {plist}'.format(plist = patches_list))
		self._reset_option_menu(patches_list, order, 0, light)

	def _reset_option_menu(self, options, order=0, index=None, light=False):
		menu = self.queue[order]['patch']["menu"]
		menu.delete(0, "end")
		logging.info('reseting menu options')
		if len(options) == 0:
			log.info('There are no patches under this deliverable')
		else:
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
		new_button = Button(self, text="New Server", width=12, command=lambda: self.createWidgets(len(self.widgets)))
		new_button.grid(row=0, column=0, pady=5, padx = 15)
		start_button = Button(self, text="Start", width=12, command=lambda: threading.Thread(target=self.generate_json).start())
		start_button.grid(row=0, column=1, pady=15, padx = 15)
		stop_button = Button(self, text="Stop", width=12, command=self.close_connection)
		stop_button.grid(row=0, column=2, pady=15, padx = 15)
		reset_button = Button(self, text="Reset", width=12, command=lambda: threading.Thread(target=self.reinit, args=(self.reactor, self.master)).start())
		reset_button.grid(row=0, column=3, pady=15, padx = 15)
		
		
		logging.info('Buttons werecreated')
	
	def create_client(self):
		self.client = InstallationFactory(self.reactor, self.update_status)
		self.log_client = LogFactory(self.reactor)
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
		Application.get_cc_list()
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
		self.log_connection = self.reactor.connectTCP(host, log_port, self.log_client)

	def close_connection(self):
		logging.info('Closing connection...')
		self.connection.disconnect()
		self.log_connection.disconnect()

	def reinit(self, reactor, master=None):
		"""reset all the config"""
		logging.info('Reinit was intiated')
		for i in xrange(len(self.widgets)-1,0,-1):
			for j in range(len(self.widgets[i])):
				self.widgets[i][j].destroy()
				# self.queue[i][j].destroy()
			del self.widgets[i]
			del self.queue[i]
			

	def delete_row(self, order):
		if len(self.widgets) > 1:
			i = order

			while i < len(self.widgets):
				if i == order:
					for j in xrange(len(self.widgets[i])):
						self.widgets[i][j].grid_forget()
						self.widgets[i][j].destroy()
					del self.widgets[i]
					del self.queue[i]
					if i < len(self.widgets):
						self.widgets[i][0].config(command=lambda order=i: self.delete_row(order))
						self.widgets[i][5].config(command=lambda order=i:self.build_patches_list(order, False))
						self.widgets[i][6].config(command=lambda order = i : self.show_log(order))
						self.queue[i]['deliverable'].trace_vdelete('w', self.queue[i]['trace'])
						self.queue[i]['deliverable'].trace('w', lambda a,b,c, order = i: threading.Thread(target=self.build_patches_list, args=(order, True)).start())
						for j in xrange(len(self.widgets[i])):
							self.widgets[i][j].grid(row = i + 1)
				else:
					self.widgets[i][0].config(command=lambda order=i: self.delete_row(order))
					self.widgets[i][5].config(command=lambda order=i:self.build_patches_list(order, False))
					self.widgets[i][6].config(command=lambda order = i : self.show_log(order))
					self.queue[i]['deliverable'].trace_vdelete('w', self.queue[i]['trace'])
					self.queue[i]['deliverable'].trace('w', lambda a,b,c, order = i: threading.Thread(target=self.build_patches_list, args=(order, True)).start())
					for j in xrange(len(self.widgets[i])):
						self.widgets[i][j].grid(row = i + 1)
				i+=1
			self.update_idletasks()

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
			cc = self.queue[i]['cc'].get()
			if client_ftp.stat('{root}/{deliv}/_ci_builds/{patch}.zip'.format(root = ftp_root, deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())):
				patch = '{root}/{deliv}/_ci_builds/{patch}.zip'.format(root = ftp_root_extnd, deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())
			elif client_ftp.stat('{root}/{deliv}/_ci-builds/{patch}.zip'.format(root = ftp_root, deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())):
				patch = '{root}/{deliv}/_ci-builds/{patch}.zip'.format(root = ftp_root_extnd, deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())
			elif client_ftp.stat('{root}/{deliv}/_manual_builds/{patch}.zip'.format(root = ftp_root, deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())):	
				patch = '{root}/{deliv}/_manual_builds/{patch}.zip'.format(root = ftp_root_extnd, deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())
			elif client_ftp.stat('{root}/{deliv}/_Product.part/{patch}.zip'.format(root = ftp_root, deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())):
				patch = '{root}/{deliv}/_Product.part/{patch}.zip'.format(root = ftp_root_extnd, deliv = self.queue[i]['deliverable'].get(), patch = self.queue[i]['var_patch'].get())
			json_obj.add_patch(server_num, patch_order_num, patch, cc)
		
		json_obj.dump_to_file()

		self.dump_server_ids()

		try:
			for name in glob.glob('installer_logs/*_installer.log'):
				os.remove(name)
		except:
			pass

		self.connect_client()

	def dump_server_ids(self):
		the_servers = []
		for i in range(len(self.queue)):
			the_servers.append(self.queue[i]['server_id'].get())
		the_servers = list(set(the_servers))
		with open('servers_list.csv', 'w') as serv_list:
			serv_list.write(';'.join(the_servers))
		serv_list.close()

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

	def close_log(self, win, log):
		log.destroy()
		win.destroy()


	def show_log(self, order):
		server_id = self.queue[order]['server_id'].get()
		logging.info('server_id: {0}'.format(server_id))
		t = Toplevel(self)
		
		logging.info('toplvl: {0}'.format(repr(t)))
		t.wm_title("Log for {serv}".format(serv = server_id))
		log = Text(t)
		t.protocol("WM_DELETE_WINDOW", lambda win=t, log=log: self.close_log(win, log))
		logging.info('log: {0}'.format(repr(log)))
		log.pack(side="top", fill="both", padx=10, pady=10)
		if log.winfo_exists():
			logging.info('log exists_show_log')
			self.refresh_log(log, server_id)
			logging.info('thread started')


	def refresh_log(self, log, server_id):
		if log.winfo_exists():
			try:
				with open('installer_logs/{serv}_installer.log'.format(serv = server_id), 'r') as thelog:
					data = thelog.readlines()
				thelog.close()
				logging.info('log exists_refresh_log')
				log.delete("1.0",END)
				log.insert("1.0", ''.join(data))
				log.update_idletasks()
				log.see(END)
			except IOError:
				logging.warn('installer_logs/{serv}_installer.log'.format(serv = server_id))
			finally:
				if log.winfo_exists():
					self.master.after(10000, lambda: self.refresh_log(log, server_id))
					logging.info('after started..')
