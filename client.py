#!/usr/bin/env python

#Copyright (C) 2017  Oscar Triano 'dotoscat' <dotoscat (at) gmail (dot) com>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as
#published by the Free Software Foundation, either version 3 of the
#License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import pyglet
import protocol

class View(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(View, self).__init__(*args, **kwargs)
        client = Client()
        self.client = client
        
        def iterate_reactor(dt):
            reactor.runUntilCurrent()
            reactor.doSelect(0)
        
        pyglet.clock.schedule(iterate_reactor)
        reactor.listenUDP(0, client)
        
    def on_draw(self):
        self.clear()

    def on_key_press(self, symbol, modifiers):
        from pyglet.window import key
        print(symbol, modifiers)

class Client(DatagramProtocol):
        
    def startProtocol(self):
        host = "127.0.0.1"
        port = 7777
        
        self.transport.connect(host, port)
        self.transport.write(protocol.client.connect())
        
    def datagramReceived(self, data, addr):
        print(data)
        
    def connectionRefused(self):
        print("With hope some server will be listening")
        pyglet.app.exit()
        
if __name__ == "__main__":
    view = View(640, 480)
    pyglet.app.run()
        
