#!/usr/bin/env  python
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

import selectors
import socket
import pyglet
import polytanks.ogf4py3 as ogf4py3
from polytanks.client import Client
from polytanks import constant

def run_client():
    director = ogf4py3.Director(
        caption="Polytanks client", fullscreen=False,
        width=constant.WIDTH, height=constant.HEIGHT,
        vwidth=constant.VWIDTH, vheight=constant.VHEIGHT)
    director.set_background_color(0., 0., 0.)
    director.scene = Client()
    pyglet.app.run()

ADDRESS = ("127.0.0.1", 7777)

def listen(data, socket):
    print(data.decode())
    socket.send("close".encode())

class Connection:
    def __init__(self, address, listener):
        self._address = address
        self._socket = socket.socket(type=socket.SOCK_DGRAM)
        self._socket.connect(address)
        self._socket.setblocking(False)
        self._selector = selectors.DefaultSelector()
        self._selector.register(self._socket, selectors.EVENT_READ,
            listener)
        self._selector_select = self._selector.select
    
    @property
    def socket(self):
        return self._socket
    
    def tick(self):
        events = self._selector_select(0)
        for key, mask in events:
            try:
                socket = key.fileobj
                data = socket.recv(1024)
                key.data(data, socket)
            except ConnectionResetError:
                print("No se ha podido conectar con el servidor")
    
    def __del__(self):
        self._socket.close()
        self._selector.close()

if __name__ == "__main__":
    #print(my_socket.send(b"Hello world"))
    conn = Connection(ADDRESS, listen)
    conn.socket.send(b"hi")
    try:
        while True:
            conn.tick()
    except KeyboardInterrupt:
        pass
