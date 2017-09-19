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

import toyblock
import pyglet
from pyglet.sprite import Sprite
from pyglet.window import key
from .ogf4py3 import Scene
from .ogf4py3.component import Body
from .ogf4py3 import system
from . import assets
from .component import TankGraphic

TANK = (Body, TankGraphic)

class Client(Scene):
    def __init__(self):
        super().__init__(2)
        
        @toyblock.System
        def update_tank_graphic(self, entity):
            body = entity[Body]
            entity[TankGraphic].set_position(body.x, body.y)
        
        self.update_tank_graphic = update_tank_graphic
        
        tank_sprites = (
            Sprite(assets.images["tank-base"], batch=self.batch, group=self.group[1]),
            Sprite(assets.images["tank-cannon"], batch=self.batch, group=self.group[0])
        )
        
        self.tank_pool = toyblock.Pool(4, TANK,
            (None, tank_sprites),
            ({"gravity": True},),
            systems=(system.physics, update_tank_graphic))
        self.tank = self.tank_pool.get()

    def update(self, dt):
        system.physics(dt, 0.)
        self.update_tank_graphic()
        system.sprite()

    def on_key_press(self, symbol, modifier):
        print(symbol, modifier)

    def on_key_release(self, symbol, modifier):
        print(symbol, modifier)
