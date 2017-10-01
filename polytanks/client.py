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

from math import cos, sin
import logging
import toyblock
import pyglet
from pyglet.sprite import Sprite
from pyglet.window import key
from .ogf4py3 import Scene
from .ogf4py3.component import Body, Collision
from .ogf4py3 import system
from . import assets
from .component import TankGraphic, PlayerInput
from .system import update_tank_graphic, update_user_input
from . import constant
from .constant import VHEIGHT as G
from . import level

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
                raise ValueError("Use a tuple for the point")
            self.x = pair[0]
            self.y = pair[1]
     
        def __getitem__(self, i):
            if not isinstance(i, int):
                raise ValueError("Use an integer for indexing")
            if i == 0: return self.x
            if i == 1: return self.y
     
    def __init__(self):
        super().__init__(4)
        
        self.system_alive_zone = system.AliveZone(0., 0., constant.VWIDTH, constant.VHEIGHT)
        self.system_client_collision = system.CheckCollision()
        self.system_client_collision.table.update({
            (constant.BULLET, constant.PLATFORM): self.bullet_platform
        })
        
        tank_args = (
            Sprite(assets.images["tank-base"], batch=self.batch, group=self.group[2]),
            Sprite(assets.images["tank-cannon"], batch=self.batch, group=self.group[1]),
            (8.5, 12.5)
        )
        
        self.tank_pool = toyblock.Pool(4, constant.TANK_DEF,
            (None, (*(0., 0.), *(constant.SIZE, 0.)), None, tank_args),
            (None, None, {"gravity": True, "max_falling_speed": G/2., "max_ascending_speed": G/2.},),
            systems=(system.physics, update_tank_graphic, update_user_input, system.platform_collision))
        self.tank = self.tank_pool.get()
        self.tank.set(Body, {'x': 200., 'y': 100.})
        self.player_input = self.tank[PlayerInput]
        self.bullet_pool = toyblock.Pool(64, constant.BULLET_DEF,
            (None, None, (assets.images["bullet"],)),
            (
                {"gravity": True},
                {"type_": constant.BULLET, "collides_with": constant.PLATFORM, "offset": (-2., -2.)},
                {"batch": self.batch, "group": self.group[2]}),
            systems=(system.physics, system.collision, system.sprite, self.system_alive_zone, self.system_client_collision)
        )
        self.bullet_pool.init(self.init_entity)
        self.bullet_pool.clean(self.clean_entity)
        
        self.platform_pool = toyblock.Pool(64, constant.PLATFORM_DEF,
            (None, (assets.images["platform"],)),
            ({"type_": constant.PLATFORM}, {"batch": self.batch, "group": self.group[0]},),
            systems=(self.system_client_collision,)
        )
        self.platforms = []
        self.platform_pool.init(self.init_entity)
        
        level.load_level(level.basic, self.platform_pool)
        
        self.cursor_point = Client.Point()
        self.cursor = Sprite(assets.images["eyehole"], batch=self.batch, group=self.group[3])

    def init(self):
        self.director.set_exclusive_mouse(True)
        self.cursor_point.x = constant.VWIDTH/2.
        self.cursor_point.y = constant.VHEIGHT/2.

    def touch_floor(self, entity):
        entity[PlayerInput].reset_time_floating()
        logging.info("Touch floor")

    def clean_entity(self, entity):
        if entity.pool == self.bullet_pool:
            entity[Sprite].visible = False

    def init_entity(self, entity):
        if entity.pool == self.platform_pool:
            self.platforms.append(entity)
        elif entity.pool == self.bullet_pool:
            entity[Sprite].visible = True
        logging.info("init", entity)

    def update(self, dt):
        if self.player_input.accumulate_power and self.player_input.release_power:
            self.player_input.accumulate_power = False
            power = int(self.player_input.time_power)
            self.player_input.time_power = 0.
            self._spawn_bullet()
            print("Bullet of powah", power)
        update_user_input(dt)
        system.collision()
        self.system_alive_zone()
        system.physics(dt, -G)
        system.platform_collision(self.platforms, self.touch_floor)
        self.system_client_collision()
        update_tank_graphic()
        system.sprite()

    def bullet_platform(self, bullet, platform):
        print(bullet, platform)
        if bullet[Body].vel_y < 0.:
            bullet.free()

    def on_key_press(self, symbol, modifier):
        if symbol in (key.A, key.LEFT):
            self.player_input.move_left()
        elif symbol in (key.D, key.RIGHT):
            self.player_input.move_right()
        elif symbol in (key.W, key.UP):
            self.player_input.jump()

    def on_key_release(self, symbol, modifier):
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
        self.player_input.aim_pointer = self.cursor_point
        self.cursor.position = self.cursor_point.point

    def on_mouse_press(self, x, y, button, modifiers):
        self.player_input.accumulate_power = True
        
    def on_mouse_release(self, x, y, button, modifiers):
        if not self.player_input.accumulate_power: return
        self.player_input.accumulate_power = False
        power = int(self.player_input.time_power)
        self.player_input.time_power = 0.
        self._spawn_bullet()

    def _spawn_bullet(self):
        bullet = self.bullet_pool.get()
        angle = self.player_input.cannon_angle
        vel_x = G*cos(angle)
        vel_y = G*sin(angle)
        x, y = self.tank[TankGraphic].cannon.position
        bullet.set(Body, {"vel_x": vel_x, "vel_y": vel_y, "x": x, "y": y})
        bullet.set(Collision, {"width": 4., "height": 4.})
