from Tkinter import *
from twisted.internet import tksupport, reactor
from gui_client import Application, JsonGenerator

root = Tk()

# Install the Reactor support
tksupport.install(root)
# set rez
root.geometry("1024x860")
# create app obj
app = Application(master=root)
# main loop from 
reactor.run()
root.destroy()
###################

    def send_message(self, event):

        message = self.entry_box.get(1.0, END)
        self.entry_box.delete(1.0, END)   


        point = TCP4ClientEndpoint(reactor, "localhost", 8000)
        d = point.connect(GreeterFactory())
        d.addCallback(lambda p: p.sendMessage(message))

class Greeter(Protocol):
    def sendMessage(self, msg):
        self.transport.write(msg.encode('utf-8'))

class GreeterFactory(Factory):
    def buildProtocol(self, addr):
        return Greeter()


########################

# at this point build Tk app as usual using the root object,
# and start the program with "reactor.run()", and stop it
# with "reactor.stop()".