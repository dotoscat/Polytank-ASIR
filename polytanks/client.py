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
from pyglet.window import key
from .ogf4py3 import Scene

from . import assets

print(assets)

class Client(Scene):
    def __init__(self):
        super().__init__(1)
        self.sprite = pyglet.sprite.Sprite(assets.images["tank-base"], batch=self.batch, group=self.group[0])

    def on_key_press(self, symbol, modifier):
        print(symbol, modifier)

    def on_key_release(self, symbol, modifier):
        print(symbol, modifier)
