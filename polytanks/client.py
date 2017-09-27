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

import logging
import toyblock
import pyglet
from pyglet.sprite import Sprite
from pyglet.window import key
from .ogf4py3 import Scene
from .ogf4py3.component import Body
from .ogf4py3 import system
from . import assets
from .component import TankGraphic, PlayerInput
from .system import update_tank_graphic, update_user_input
from . import constant
from . import level

class Client(Scene):    
    def __init__(self):
        super().__init__(3)
                            
        tank_args = (
            Sprite(assets.images["tank-base"], batch=self.batch, group=self.group[2]),
            Sprite(assets.images["tank-cannon"], batch=self.batch, group=self.group[1]),
            (8.5, 12.5)
        )
        
        self.tank_pool = toyblock.Pool(4, constant.TANK_DEF,
            (None, (*(0., 0.), *(constant.SIZE, 0.)), None, tank_args),
            (None, None, {"gravity": True},),
            systems=(system.physics, update_tank_graphic, update_user_input, system.platform_collision))
        self.tank = self.tank_pool.get()
        self.tank.set(Body, {'x': 200., 'y': 100.})
        self.player_input = self.tank[PlayerInput]
        
        self.platform_pool = toyblock.Pool(64, constant.PLATFORM_DEF,
            (None, (assets.images["platform"],),),
            (None, {"batch": self.batch, "group": self.group[0]},),
        )
        self.platforms = []
        self.platform_pool.init(self.init_entity)
        
        level.load_level(level.basic, self.platform_pool)

    def touch_floor(self):
        print("touch")
        logging.info("Touch floor")

    def init_entity(self, entity):
        if entity.pool == self.platform_pool:
            self.platforms.append(entity)
        logging.info("init", entity)

    def update(self, dt):
        update_user_input()
        system.physics(dt, -32.)
        system.platform_collision(self.platforms, self.touch_floor)
        update_tank_graphic()
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
                
