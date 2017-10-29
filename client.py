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

import pyglet
import polytanks.ogf4py3 as ogf4py3
from polytanks.client import Client
from polytanks import constant, protocol

ADDRESS = ("127.0.0.1", 7777)

def listen(data, socket):
    print(data.decode())

if __name__ == "__main__":
    #conn = ogf4py3.Connection(ADDRESS, listen)
    #conn.socket.send(b"join")
    try:
        director = ogf4py3.Director(
            caption="Polytanks client", fullscreen=False,
            width=constant.WIDTH, height=constant.HEIGHT,
            vwidth=constant.VWIDTH, vheight=constant.VHEIGHT)
        director.set_background_color(0., 0., 0.)
        client = Client(ADDRESS)
        director.scene = client
        pyglet.app.run()
    except KeyboardInterrupt:
        pass
    client.logout()
