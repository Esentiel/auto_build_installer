from Tkinter import *
from twisted.internet import tksupport, reactor
from gui_client import Application, JsonGenerator
from console_client import InstProtocol, InstFactory, host, port
import os

root = Tk()

# Install the Reactor support
tksupport.install(root)
# set rez
root.geometry("1024x860")
# create app obj
app = Application(master=root)
# connect to factory
reactor.connectTCP(host, port, InstFactory())
# main loop from
reactor.run()
os.remove('install_qeue.json')
root.destroy()
reactor.stop()
###################

# import struct

# from twisted.internet.protocol import Protocol, ClientFactory
# from twisted.protocols.basic import IntNStringReceiver


# class SocketClientProtocol(IntNStringReceiver):
#     """ The protocol is based on twisted.protocols.basic
#         IntNStringReceiver, with little-endian 32-bit
#         length prefix.
#     """
#     structFormat = "<L"
#     prefixLength = struct.calcsize(structFormat)

#     def stringReceived(self, s):
#         self.factory.got_msg(s)

#     def connectionMade(self):
#         self.factory.clientReady(self)


# class SocketClientFactory(ClientFactory):
#     """ Created with callbacks for connection and receiving.
#         send_msg can be used to send messages when connected.
#     """
#     protocol = SocketClientProtocol

#     def __init__(
#             self,
#             connect_success_callback,
#             connect_fail_callback,
#             recv_callback):
#         self.connect_success_callback = connect_success_callback
#         self.connect_fail_callback = connect_fail_callback
#         self.recv_callback = recv_callback
#         self.client = None

#     def clientConnectionFailed(self, connector, reason):
#         self.connect_fail_callback(reason)

#     def clientReady(self, client):
#         self.client = client
#         self.connect_success_callback()

#     def got_msg(self, msg):
#         self.recv_callback(msg)

#     def send_msg(self, msg):
#         if self.client:
#             self.client.sendString(msg)
# ######################
# #       GUI PART
# ####################

# class SampleGUIClientWindow(QMainWindow):
#     def __init__(self, reactor, parent=None):
#         super(SampleGUIClientWindow, self).__init__(parent)
#         self.reactor = reactor

#         self.create_main_frame()
#         self.create_client()
#         self.create_timer()

#     def create_main_frame(self):
#         self.circle_widget = CircleWidget()
#         self.doit_button = QPushButton('Do it!')
#         self.doit_button.clicked.connect(self.on_doit)
#         self.log_widget = LogWidget()

#         hbox = QHBoxLayout()
#         hbox.addWidget(self.circle_widget)
#         hbox.addWidget(self.doit_button)
#         hbox.addWidget(self.log_widget)

#         main_frame = QWidget()
#         main_frame.setLayout(hbox)

#         self.setCentralWidget(main_frame)

#     def create_timer(self):
#         self.circle_timer = QTimer(self)
#         self.circle_timer.timeout.connect(self.circle_widget.next)
#         self.circle_timer.start(25)

#     def create_client(self):
#         self.client = SocketClientFactory(
#                         self.on_client_connect_success,
#                         self.on_client_connect_fail,
#                         self.on_client_receive)

#     def on_doit(self):
#         self.log('Connecting...')
#         # When the connection is made, self.client calls the on_client_connect
#         # callback.
#         #
#         self.connection = self.reactor.connectTCP(SERVER_HOST, SERVER_PORT, self.client)

#     def on_client_connect_success(self):
#         self.log('Connected to server. Sending...')
#         self.client.send_msg('hello')

#     def on_client_connect_fail(self, reason):
#         # reason is a twisted.python.failure.Failure  object
#         self.log('Connection failed: %s' % reason.getErrorMessage())

#     def on_client_receive(self, msg):
#         self.log('Client reply: %s' % msg)
#         self.log('Disconnecting...')
#         self.connection.disconnect()

#     def log(self, msg):
#         timestamp = '[%010.3f]' % time.clock()
#         self.log_widget.append(timestamp + ' ' + str(msg))

#     def closeEvent(self, e):
#         self.reactor.stop()


# #-------------------------------------------------------------------------------
# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     try:
#         import qt4reactor
#     except ImportError:
#         # Maybe qt4reactor is placed inside twisted.internet in site-packages?
#         from twisted.internet import qt4reactor
#     qt4reactor.install()

#     from twisted.internet import reactor
#     mainwindow = SampleGUIClientWindow(reactor)
#     mainwindow.show()

#     reactor.run()

########################