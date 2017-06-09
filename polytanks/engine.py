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
import toyblock

class Body:
    ID = 1
    __slots__ = ("x", "y", "id")
    
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.id = Body.ID
        Body.ID += 1

_tank_def = (Body, pyglet.sprite.Sprite)
_tanks = toyblock.Pool(4, _tank_def)

class Engine(object):
    def __init__(self):
        self.entities = []
        
