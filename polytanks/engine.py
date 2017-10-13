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

from .system import update_tank_graphic, update_user_input
from .ogf4py3 import system
from . import constant
from .constant import G

system_alive_zone = system.AliveZone(0., 0.,
    constant.VWIDTH, constant.VHEIGHT)

system_client_collision = system.CheckCollision()

systems = [system.lifespan, update_user_input, system.collision,
    system_alive_zone, system.physics, system.platform_collision,
    system_client_collision, update_tank_graphic]

class Engine:
    def __init__(self):
        self.platforms = []

    def update(self, dt):
        system.lifespan(dt)
        update_user_input(dt, self)
        system.collision()
        system_alive_zone()
        system.physics(dt, -G)
        system.platform_collision(self.platforms, self.touch_floor)
        system_client_collision()
        update_tank_graphic()

    def touch_floor(self, entity):
        entity.player_input.reset_time_floating()
