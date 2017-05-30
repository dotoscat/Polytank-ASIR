#!/usr/bin/env python

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class Server(DatagramProtocol):
    
    def datagramReceived(self, data, addr):
        print("{} from {}".format(str(data, "utf8"), addr))
        self.transport.write(bytes("Server: Hello client {} :D".format(addr), "utf8"), addr)

if __name__ == "__main__":
    reactor.listenUDP(7777, Server())
    reactor.run()
