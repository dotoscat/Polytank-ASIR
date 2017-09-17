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
import polytanks.assets
from polytanks.client import Client

if __name__ == "__main__":
    WIDTH = 800
    HEIGHT = 600
    director = ogf4py3.Director(
        caption="Polytanks client",
        width=WIDTH,
        height=HEIGHT,
        vwidth=WIDTH/2.,
        vheight=HEIGHT/2.
        )
        
    director.scene = Client()
        
    pyglet.app.run()
