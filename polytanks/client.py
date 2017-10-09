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
import pyglet
from pyglet.sprite import Sprite
from pyglet.window import key
from .ogf4py3 import toyblock3
from .ogf4py3 import Scene
from .ogf4py3.component import Body, Collision, FloorCollision, Timer
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
        
        tank_builder = toyblock3.InstanceBuilder()
        tank_builder.add("player_input", PlayerInput)
        tank_builder.add("floor_collision", FloorCollision, *(0., 0.), *(constant.SIZE, 0.))
        tank_builder.add("body", Body, gravity=True, max_falling_speed=G/2., max_ascending_speed=G/2.)
        tank_builder.add("tank_graphic", TankGraphic,
            Sprite(assets.images["tank-base"], batch=self.batch, group=self.group[2]),
            Sprite(assets.images["tank-cannon"], batch=self.batch, group=self.group[1]),
            (8.5, 12.5),)
        
        self.tank_pool = toyblock3.build_Entity(4, tank_builder,
            system.physics, update_tank_graphic, update_user_input, system.platform_collision)
        self.tank = self.tank_pool.get()
        self.tank.set("body", x=200., y=100.)
        self.player_input = self.tank.player_input
        
        bullet_builder = toyblock3.InstanceBuilder()
        bullet_builder.add("body", Body, gravity=True)
        bullet_builder.add("collision", Collision, type_=constant.BULLET,
            collides_with=constant.PLATFORM, offset=(-2., -2.))
        bullet_builder.add("sprite", Sprite, assets.images["bullet"],
                            batch=self.batch, group=self.group[2])
        
        self.bullet_pool = toyblock3.build_Entity(
            64, bullet_builder,
            system.physics, system.collision, system.sprite,
            self.system_alive_zone, self.system_client_collision)
        
        self.bullet_pool.init(self.init_entity)
        self.bullet_pool.clean(self.clean_entity)
        
        plat_builder = toyblock3.InstanceBuilder()
        plat_builder.add("collision", Collision, type_=constant.PLATFORM)
        plat_builder.add("sprite", Sprite, assets.images["platform"],
            batch=self.batch, group=self.group[0])
        
        self.platform_pool = toyblock3.build_Entity(
            64, plat_builder, self.system_client_collision)
            
        self.platforms = []
        self.platform_pool.init(self.init_entity)
        
        expl_builder = toyblock3.InstanceBuilder()
        expl_builder.add("body", Body)
        expl_builder.add("collision", Collision,
            type_=constant.EXPLOSION, collides_with=constant.EXPLOSION,
            offset=(-4., -4.), width=16., height=16.)
        expl_builder.add("timer", Timer, 0.25)
        expl_builder.add("sprite", Sprite, assets.images["explosion"],
            batch=self.batch, group=self.group[3])
        
        self.explosion_pool = toyblock3.build_Entity(64, expl_builder,
            system.lifespan, system.sprite)
                
        self.explosion_pool.init(self.init_entity)
        self.explosion_pool.clean(self.clean_entity)
        
        level.load_level(level.basic, self.platform_pool)
        
        self.cursor_point = Client.Point()
        self.cursor = Sprite(assets.images["eyehole"], batch=self.batch, group=self.group[3])

    def init(self):
        self.director.set_exclusive_mouse(True)
        self.cursor_point.x = constant.VWIDTH/2.
        self.cursor_point.y = constant.VHEIGHT/2.

    def touch_floor(self, entity):
        entity.player_input.reset_time_floating()
        logging.info("Touch floor")

    def clean_entity(self, entity):
        if (isinstance(entity, self.bullet_pool)
            or isinstance(entity, self.explosion_pool)):
            entity.sprite.visible = False

    def init_entity(self, entity):
        if isinstance(entity, self.platform_pool):
            self.platforms.append(entity)
        elif (isinstance(entity, self.bullet_pool)
            or isinstance(entity, self.explosion_pool)):
            entity.sprite.visible = True
        logging.info("init", entity)

    def update(self, dt):
        system.lifespan(dt)
        if self.player_input.accumulate_power and self.player_input.release_power:
            self.player_input.accumulate_power = False
            self.player_shoots()
        update_user_input(dt)
        system.collision()
        self.system_alive_zone()
        system.physics(dt, -G)
        system.platform_collision(self.platforms, self.touch_floor)
        self.system_client_collision()
        update_tank_graphic()
        system.sprite()

    def bullet_platform(self, bullet, platform):
        if bullet.body.vel_y < 0.:
            x = bullet.body.x
            y = bullet.body.y
            print("destroy", bullet)
            print("on", platform)
            bullet.free()
            self._spawn_explosion(x, y)

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
        self.player_shoots()

    def player_shoots(self):
        x, y = self.tank.tank_graphic.cannon.position
        power = int(self.player_input.time_power)
        self.player_input.time_power = 0.
        angle = self.player_input.cannon_angle
        force = G
        gravity = True
        if power == 0:
            force *= 1.
            gravity = False
        elif power == 1:
            force *= 1.
            gravity = True
        elif power >= 2:
            force *= 1
            gravity = False
        self._spawn_bullet(x, y, force, angle, gravity)

    def _spawn_bullet(self, x, y, force, angle, gravity):
        bullet = self.bullet_pool.get()
        vel_x = force*cos(angle)
        vel_y = force*sin(angle)
        bullet.set("body", vel_x=vel_x, vel_y=vel_y, x=x, y=y, gravity=gravity)
        bullet.set("collision", width=4., height=4.)

    def _spawn_explosion(self, x, y):
        explosion = self.explosion_pool.get()
        explosion.set("body", x=x, y=y)
