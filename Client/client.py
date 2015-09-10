from Tkinter import *
from twisted.internet import tksupport, reactor
from gui_client import Application, JsonGenerator
from config import title, rez
import logging, glob, os

def on_closing(root, reactor):
	root.destroy()
	reactor.stop()

def main():
	logging.basicConfig(filename='client.log', level=logging.INFO, format='%(asctime)s -  %(name)s - %(thread)d - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
	root = Tk()
	root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, reactor))

	# Install the Reactor support
	tksupport.install(root)
	# set rez
	root.geometry(rez)
	root.wm_title(title)
	# create app obj
	app = Application(reactor, master=root)
	# main loop from
	reactor.run()
	###################

if __name__ == '__main__':
	main()