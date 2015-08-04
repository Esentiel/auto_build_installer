ports = [8007, 8008, 8009]

import os
from twisted.internet import protocol, reactor

class MyPP(protocol.ProcessProtocol):
    def connectionMade(self):
        self.pid = self.transport.pid

    def processExited(self, reason):
        print "processExited, status %s" % (reason.value.exitCode,)



class Test:
    def run(self):
        for port in ports:
            pp = MyPP()
            command = ['C:\Python27\python.exe','main.py', str(port)]
            subprocess = reactor.spawnProcess(pp, command[0], command, env=os.environ)
            print "Process for {port} started..".format(port = port)


Test().run()
reactor.run()