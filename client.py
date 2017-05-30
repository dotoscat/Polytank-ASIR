#!/usr/bin/env python

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class Client(DatagramProtocol):
    
    def startProtocol(self):
        host = "127.0.0.1"
        port = 7777
        
        self.transport.connect(host, port)
        self.transport.write(b'hello server! :D')
        
    def datagramReceived(self, data, addr):
        print(data)
        
    def connectionRefused(self):
        print("With hope some server will be listening")
        reactor.stop()
        
if __name__ == "__main__":
    reactor.listenUDP(0, Client())
    reactor.run()
        
