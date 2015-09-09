from Tkinter import *
from twisted.internet import tksupport, reactor
from gui_client import Application, JsonGenerator
import logging, glob, os

def on_closing(root, reactor):
	root.destroy()
	reactor.stop()

def main():
	logging.basicConfig(filename='client.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
	root = Tk()
	root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, reactor))

	# Install the Reactor support
	tksupport.install(root)
	# set rez
	root.geometry("1280x860")
	root.wm_title("Anime Auto bulk installer tool for DHL project and friends")
	# create app obj
	app = Application(reactor, master=root)
	# main loop from
	reactor.run()
	###################

if __name__ == '__main__':
	main()