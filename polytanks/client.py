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
from random import choice
import pyglet

from pyglet.sprite import Sprite
from pyglet.window import key
from .ogf4py3 import gui
from .ogf4py3 import magnitude_to_vector, get_angle_from, Connection
from .ogf4py3 import toyblock3
from .ogf4py3 import Scene
from .ogf4py3 import system
from . import assets
from .system import update_tank_graphic, update_user_input
from . import constant
from .constant import G
from . import level
from . import builder
from . import engine
from .component import TankGraphic
from . import protocol

systems = engine.systems
systems.append(system.sprite)

class Client(Scene):
    
    class Point:
        def __init__(self, x=0., y=0.):
            self.x = x
            self.y = y
            
        @property
        def point(self):
            return (self.x, self.y)
            
        @point.setter
        def point(self, pair):
            if not isinstance(pair, tuple):
                raise TypeError("Use a tuple for the point")
            self.x = pair[0]
            self.y = pair[1]
        
        def __iter__(self):
            return iter((self.x, self.y))
        
        def __getitem__(self, i):
            if not isinstance(i, int):
                raise TypeError("Use an integer for indexing")
            if i == 0: return self.x
            if i == 1: return self.y
     
    def __init__(self, address):
        super().__init__(5)
        
        self.conn = Connection(address, self.listen)
        self._joined = False
        
        builder.tank.add("tank_graphic", TankGraphic,
            Sprite(assets.images["tank-base"], batch=self.batch, group=self.group[2]),
            Sprite(assets.images["tank-cannon"], batch=self.batch, group=self.group[1]),
            (0., 4.),)
        builder.bullet.add("sprite", Sprite, assets.images["bullet"],
            batch=self.batch, group=self.group[2])
        builder.platform.add("sprite", Sprite, assets.images["platform"],
            batch=self.batch, group=self.group[0])
        builder.explosion.add("sprite", Sprite, assets.images["explosion"],
            batch=self.batch, group=self.group[3])
        builder.powerup.add("sprite", Sprite, assets.images["heal"],
            batch=self.batch, group=self.group[3])
        
        self.engine = engine.Engine()
        level.load_level(level.basic, self.engine.platform_pool)

        self.engine.bullet_pool.init(self.init_entity)
        self.engine.bullet_pool.clean(self.clean_entity)
        self.engine.platform_pool.init(self.init_entity)
        self.engine.explosion_pool.init(self.init_entity)
        self.engine.explosion_pool.clean(self.clean_entity)
        self.engine.powerup_pool.init(self.init_entity)
        self.engine.powerup_pool.clean(self.clean_entity)
        
        self.cursor_point = Client.Point()
        self.cursor = Sprite(assets.images["eyehole"], batch=self.batch, group=self.group[3])
        
        self.damage = gui.NumberLabel("%", batch=self.batch, group=self.group[4])
        self.damage.value = 0
        self.damage.x = 32.
        self.damage.y = 8.

        self.dt = 0.

    def init(self):
        self.director.set_exclusive_mouse(True)
        self.cursor_point.x = constant.VWIDTH/2.
        self.cursor_point.y = constant.VHEIGHT/2.

    def clean_entity(self, entity):
        if (isinstance(entity, self.engine.bullet_pool)
            or isinstance(entity, self.engine.explosion_pool)
            or isinstance(entity, self.engine.powerup_pool)):
            entity.sprite.visible = False

    def init_entity(self, entity):
        if (isinstance(entity, self.engine.bullet_pool)
            or isinstance(entity, self.engine.explosion_pool)
            or isinstance(entity, self.engine.powerup_pool)):
            entity.sprite.visible = True
        logging.info("init", entity)

    def update(self, dt):
        self.dt += dt
        if self.dt > 3.:
            self.dt = 0.
            if choice((True, False)):
                powerup = self.engine._spawn_powerup(128., 128., "heal")
                powerup.sprite.image = assets.images["heal"]
        self.conn.tick()
        self.engine.update(dt)
        if self._joined:
            self.damage.value = self.tank.tank.damage
        system.sprite()
        for message in self.engine.messages:
            if message in assets.player:
                assets.player.play(message)

    def on_key_press(self, symbol, modifier):
        if not self._joined and symbol == key.J:
            self.conn.socket.send(protocol.mono.pack(protocol.JOIN))
        elif not self._joined:
            return
        elif self._joined and symbol == key.L:
            self.conn.socket.send(protocol.mono.pack(protocol.LOGOUT))
        if symbol in (key.A, key.LEFT):
            self.player_input.move_left()
        elif symbol in (key.D, key.RIGHT):
            self.player_input.move_right()
        elif symbol in (key.W, key.UP):
            self.player_input.jump()

    def on_key_release(self, symbol, modifier):
        if not self._joined: return
        if symbol in (key.A, key.D, key.LEFT, key.RIGHT) and self.player_input.moves():
            self.player_input.stop_moving()
        if symbol in (key.UP, key.W) and self.player_input.do_jump:
            self.player_input.not_jump()

    def on_mouse_motion(self, x, y, dx, dy):
        #  print("mouse motion", x, y, dx, dy)
        self._update_mouse(dx, dy)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        #  print("mouse drag", x, y, dx, dy)
        self._update_mouse(dx, dy)

    def _update_mouse(self, dx, dy):
        vdx, vdy = self.director.get_virtual_xy(dx, dy)
        self.cursor_point.x += vdx
        self.cursor_point.y += vdy
        if self.cursor_point.x < 0.:
            self.cursor_point.x = 0.
        elif self.cursor_point.x > constant.VWIDTH:
            self.cursor_point.x = constant.VWIDTH
        if self.cursor_point.y < 0.:
            self.cursor_point.y = 0.
        elif self.cursor_point.y > constant.VHEIGHT:
            self.cursor_point.y = constant.VHEIGHT
        if not self._joined: return 
        self.player_input.aim_pointer = self.cursor_point
        self.cursor.position = self.cursor_point.point

    def on_mouse_press(self, x, y, button, modifiers):
        if not self._joined: return
        self.player_input.accumulate_power = True
        
    def on_mouse_release(self, x, y, button, modifiers):
        if not self._joined: return
        if not self.player_input.accumulate_power: return
        self.player_input.accumulate_power = False
        self.player_input.shoots = True

    def listen(self, data, socket):
        print(self, data.decode())

    def joined(self, id_, x, y):
        print("Joined with id", id_, x, y)
        self.tank = self.engine.tank_pool.get()
        self.tank.id = id_
        self.tank.set("body", x=x, y=x)
        self.player_input = self.tank.input
        self._joined = True
        
