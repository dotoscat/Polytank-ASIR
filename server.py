#!/usr/bin/env python

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

print("Hola mundo")
class Server(DatagramProtocol):
    
    def datagramReceived(self, data, addr):
        print("{} from {}".format(data, addr))

if __name__ == "__main__":
    reactor.listenUDP(7777, Server())
    reactor.run()
