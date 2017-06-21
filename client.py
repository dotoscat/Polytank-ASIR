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
from polytanks.engine import Engine, Body
import toyblock

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
        self._engine = Engine()
        self._client = Client(self._engine, self)
        self._images = {}
        self._sprites = {}
        self._draw_sprites = []
        self._graphics_system = toyblock.System(self._update_entities)
        
        def iterate_reactor(dt):
            reactor.runUntilCurrent()
            reactor.doSelect(0)
        
        def iterate_graphics_system(dt):
            self._graphics_system.run()
        
        pyglet.clock.schedule(iterate_reactor)
        pyglet.clock.schedule(iterate_graphics_system)
        reactor.listenUDP(0, self._client)
        self._load_images()
    
    def _load_images(self):
        self._images["tank"] = pyglet.resource.image("tank.png")
    
    def on_draw(self):
        self.clear()
        for sprite in self._draw_sprites:
            sprite.draw()

    def on_key_press(self, symbol, modifiers):
        from pyglet.window import key
        if symbol in (key.LEFT, key.A):
            self._client.send(protocol.move(1, -1.))
        elif symbol in (key.RIGHT, key.D):
            self._client.send(protocol.move(1, 1.))
        elif symbol == key.C:
            print("C")
            if self._client.is_connected():
                self._client.disconnect()
            else:
                self._client.connect()
    
    def on_key_release(self, symbol, modifiers):
        from pyglet.window import key
        if symbol in (key.LEFT, key.A, key.RIGHT, key.D):
            self._client.send(protocol.move(1, 0.))
    
    def add_to_draw(self, entity, id_, image_name):
        image = self._images[image_name]
        self._sprites[id_] = pyglet.sprite.Sprite(image)
        self._graphics_system.add_entity(entity)

    def _update_entities(self, system, entity):
        body = entity.get_component(Body)
        sprite = self._sprites[body.id]
        sprite.x = body.x
        sprite.y = body.y
        self._draw_sprites.append(sprite)

class Client(DatagramProtocol):
    """
    Esta clase se encarga de gestionar la red entre el servidor y el cliente.
    """
    def __init__(self, engine, view):
        super(Client, self).__init__()
        self._engine = engine
        self._view = view
        self._connected = False
            
    def datagramReceived(self, data, addr):
        """
        Con la ayuda del módulo protocol el cliente puede saber qué
        es lo que pasa en el servidor.
        """
        server_command = protocol.get_command(data)
        if server_command == protocol.SNAPSHOT:
            print("Snapshot from server!", data)
            protocol.set_engine_from_snapshot(self._engine, data)
            #command, id_, x, y = protocol.get_recreate_tank(data)
            #entity, body = self._engine.create_tank(id_, x, y)
            #self._view.add_to_draw(entity, id_, "tank")
            #print("(Re)created tank with id {} at {}, {}".format(id_, x, y))
        
    def connectionRefused(self):
        print("With hope some server will be listening")
    
    def send(self, data):
        self.transport.write(data)
    
    def is_connected(self):
        return self._connected
    
    def connect(self, host="127.0.0.1", port=7777):
        if self._connected: return False
        self.transport.connect(host, port)
        self.transport.write(protocol.connect())
        self._connected = True
        return True
    
    def disconnect(self):
        if not self._connected: return False
        deferred = self.transport.stopListening()
        
        def _set_disconnected():
            print("Disconnected")
            self._connected = False
        
        deferred.addCallback(_set_disconnected)
        
        return True
    
if __name__ == "__main__":
    pyglet.resource.path = ["graphics"]
    pyglet.resource.reindex()
    view = View(640, 480)
    pyglet.app.run()
        
