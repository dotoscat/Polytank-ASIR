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

from collections import deque
from .system import update_tank_graphic, update_user_input
from .ogf4py3 import system
from . import constant
from .constant import G
from .ogf4py3 import magnitude_to_vector, get_angle_from
from . import builder
from .ogf4py3 import toyblock3

system_alive_zone = system.BoundaryTrigger(0., 0.,
    constant.VWIDTH, constant.VHEIGHT)

system_client_collision = system.CheckCollision()
system_platform_collision = system.PlatformCollision()

systems = [system.lifespan, update_user_input, system.collision,
    system_alive_zone, system.physics, system_platform_collision,
    system_client_collision, update_tank_graphic]

class Engine:
    
    def __init__(self, tank_builder=builder.tank, bullet_builder=builder.bullet,
                platform_builder=builder.platform, explosion_builder=builder.explosion,
                powerup_builder=builder.powerup, systems=systems):
                    
        system_client_collision.table.update({
            (constant.BULLET, constant.PLATFORM): self.bullet_platform,
            (constant.BULLET, constant.TANK): self.bullet_tank,
            (constant.EXPLOSION, constant.TANK): self.explosion_tank,
            (constant.POWERUP, constant.TANK): self.powerup_tank})
        self._messages = deque()
        self._add_message = self._messages.append
        self.tank_pool = toyblock3.build_Entity(4, tank_builder,
            *systems)
        self.bullet_pool = toyblock3.build_Entity(64, bullet_builder,
            *systems)
        self.platform_pool = toyblock3.build_Entity(64, platform_builder,
            *systems)
        self.explosion_pool = toyblock3.build_Entity(64, explosion_builder,
            *systems)
        self.powerup_pool = toyblock3.build_Entity(16, powerup_builder,
            *systems)
    
    @property
    def messages(self):
        _messages = self._messages
        while _messages:
            yield _messages.pop()
        
    def update(self, dt):
        system.lifespan(dt)
        update_user_input(dt, self)
        system.physics(dt, -G)
        system.collision()
        system_platform_collision(self.touch_floor)
        system_client_collision()
        system_alive_zone(self._check_limit)
        update_tank_graphic()

    def touch_floor(self, entity):
        entity.input.reset_time_floating()
        entity.tank.hitstun = 0.
        entity.tank.control = True
        self._add_message("touch-floor")

    def shoot(self, entity):
        x, y = entity.tank_graphic.cannon.position
        power = entity.input.time_power
        entity.input.time_power = 0.
        angle = entity.input.cannon_angle
        force = G/2.
        gravity = True
        if power >= 1.:
            force *= power
        bullet = self._spawn_bullet(entity, x, y, force, angle, gravity)
        bullet.set("bullet", owner=entity, power=power)
        self._add_message("shoot")

    def _spawn_bullet(self, entity, x, y, force, angle, gravity):
        bullet = self.bullet_pool.get()
        vel = magnitude_to_vector(force, angle)
        vel_x = vel[0] + entity.body.vel_x
        vel_y = vel[1] + entity.body.vel_y
        bullet.set("body", vel_x=vel_x, vel_y=vel_y, x=x, y=y, gravity=gravity)
        bullet.set("collision", width=4., height=4.)
        return bullet

    def _spawn_explosion(self, x, y, damage, knockback=0):
        explosion = self.explosion_pool.get()
        explosion.set("body", x=x, y=y)
        explosion.set("explosion", damage=damage, knockback=knockback)
        self._add_message("explosion")

    def jump(self, entity):
        entity.body.vel_y = G/2.
        entity.input.do_jump = False
        self._add_message("jump")
        
    def float(self, entity, dt):
        if entity.body.vel_y < 0.:
            entity.body.vel_y = 0.
        entity.input.time_floating += dt
        entity.body.apply_force(dt, y=G*1.5)
        self._add_message("float")

    def bullet_platform(self, bullet, platform):
        if bullet.body.vel_y < 0.:
            x = bullet.body.x
            y = bullet.body.y
            bullet.free()
            self._spawn_explosion(x, y, 1)

    def bullet_tank(self, bullet, tank):
        if bullet.bullet.owner == tank: return
        x = bullet.body.x
        y = bullet.body.y
        bullet.free()
        self._spawn_explosion(x, y, 1)

    def explosion_tank(self, explosion, tank):
        angle = get_angle_from(explosion.body.x, explosion.body.y,
            tank.body.x, tank.body.y)
        force = magnitude_to_vector(G/4.+tank.tank.damage, angle)
        tank.body.max_ascending_speed = 0.
        tank.body.vel_x = force[0]
        tank.body.vel_y = force[1]
        tank.tank.damage += explosion.explosion.damage
        tank.tank.hitstun = 1.
        tank.tank.control = False

    def powerup_tank(self, powerup, tank):
        powerup.powerup.action(tank)
        powerup.free()
        self._add_message("powerup")

    def _spawn_powerup(self, x, y, type_):
        powerup = self.powerup_pool.get()
        powerup.set("body", x=x, y=y)
        if type_ == "heal":
            powerup.powerup.action = self._heal_tank
        else:
            powerup.powerup.action = self._dummy
        return powerup

    def _check_limit(self, entity):
        if isinstance(entity, self.bullet_pool):
            entity.free()
        elif isinstance(entity, self.tank_pool):
            print(entity, "KO!")

    @staticmethod
    def _heal_tank(tank):
        tank.tank.damage -= 30
        if tank.tank.damage < 0:
            tank.tank.damage = 0

    @staticmethod
    def _dummy(tank):
        print("Dummy!")
