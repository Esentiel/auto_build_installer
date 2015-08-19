from Tkinter import *
from twisted.internet import tksupport, reactor
from gui_client import Application, JsonGenerator
import os

root = Tk()

# Install the Reactor support
tksupport.install(root)
# set rez
root.geometry("1280x860")
# create app obj
app = Application(reactor, master=root)
# main loop from
reactor.run()
root.destroy()
reactor.stop()
###################
