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
import polytanks.protocol as protocol

class View(pyglet.window.Window):
    """
    Esta clase sería la 'vista', de lo que pasa en el servidor.
    Al contrario que el servidor aquí se le da control a pyglet para controlar
    la ventana. La funcionalidad de twisted es llamada periódicamente desde
    pyglet para atender las conexiones de red.
    
    Cada evento de la ventana es pasado al cliente.
    """
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
        if symbol in (key.LEFT, key.A):
            self.client.send(protocol.move_tank(1, 1.))
        elif symbol in (key.RIGHT, key.D):
            self.client.send(protocol.move_tank(1, -1.))
    
    def on_key_release(self, symbol, modifiers):
        from pyglet.window import key
        if symbol in (key.LEFT, key.A, key.RIGHT, key.D):
            self.client.send(protocol.move_tank(1, 0.))
    
class Client(DatagramProtocol):
    """
    Esta clase se encarga de gestionar la red entre el servidor y el cliente.
    """
    def startProtocol(self):
        host = "127.0.0.1"
        port = 7777
        
        self.transport.connect(host, port)
        self.transport.write(protocol.connect())
        
    def datagramReceived(self, data, addr):
        """
        Con la ayuda del módulo protocol el cliente puede saber qué
        es lo que pasa en el servidor.
        """
        server_command = protocol.get_command(data)
        if server_command == protocol.RECREATE_TANK:
            command, id_, x, y = protocol.get_recreate_tank(data)
            print("(Re)created tank with id {} at {}, {}".format(id_, x, y))
        
    def connectionRefused(self):
        print("With hope some server will be listening")
        pyglet.app.exit()
    
    def send(self, data):
        self.transport.write(data)
    
if __name__ == "__main__":
    pyglet.resource.path = ["graphics"]
    pyglet.resource.reindex()
    view = View(640, 480)
    pyglet.app.run()
        
