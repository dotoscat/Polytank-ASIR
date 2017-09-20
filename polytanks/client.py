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

from math import atan2, degrees, hypot
import toyblock
import pyglet
from pyglet.sprite import Sprite
from pyglet.window import key
from .ogf4py3 import Scene
from .ogf4py3.component import Body
from .ogf4py3 import system
from . import assets
from .component import TankGraphic, PlayerInput

TANK = (PlayerInput, Body, TankGraphic)

class Client(Scene):
    TANK_SPEED = 64.
    
    def __init__(self):
        super().__init__(2)
        
        @toyblock.System
        def update_tank_graphic(self, entity):
            body = entity[Body]
            entity[TankGraphic].set_position(body.x, body.y)
        
        @toyblock.System
        def update_user_input(self, entity):
            player_input = entity[PlayerInput]
            player_body = entity[Body]
            player_body.vel_x = player_input.move*Client.TANK_SPEED
            aim_pointer = player_input.aim_pointer
            cannon_position = entity[TankGraphic].cannon.position
            angle = atan2(aim_pointer[1] - cannon_position[1], aim_pointer[0] - cannon_position[0])
            entity[TankGraphic].cannon.rotation = -degrees(angle)
            
        self.update_user_input = update_user_input
        self.update_tank_graphic = update_tank_graphic
        
        tank_args = (
            Sprite(assets.images["tank-base"], batch=self.batch, group=self.group[1]),
            Sprite(assets.images["tank-cannon"], batch=self.batch, group=self.group[0]),
            (8.5, 12.5)
        )
        
        self.tank_pool = toyblock.Pool(4, TANK,
            (None, None, tank_args),
            (None, {"gravity": True},),
            systems=(system.physics, update_tank_graphic, update_user_input))
        self.tank = self.tank_pool.get()
        self.tank.set(Body, {'x': 200., 'y': 200.})
        self.player_input = self.tank[PlayerInput]

    def update(self, dt):
        self.update_user_input()
        system.physics(dt, 0.)
        self.update_tank_graphic()
        system.sprite()

    def on_key_press(self, symbol, modifier):
        if symbol == key.LEFT:
            self.player_input.move_left()
        elif symbol == key.RIGHT:
            self.player_input.move_right()

    def on_key_release(self, symbol, modifier):
        if symbol in (key.LEFT, key.RIGHT) and self.player_input.moves():
            self.player_input.stop_moving()

    def on_mouse_motion(self, x, y, dx, dy):
        aim_pointer = self.director.get_virtual_xy(x, y)
        self.player_input.aim_pointer = aim_pointer
        
