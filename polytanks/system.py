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

from math import degrees
from .ogf4py3 import toyblock3, get_angle_from
from .constant import TANK_SPEED, VHEIGHT as G, MAX_ASCENDING_SPEED

@toyblock3.system("input", "body", "platform")
def update_user_input(self, entity, dt, engine):
    """
    :obj:`engine` deberá tener como método :meth:`player_shoots`
    o el método :meth:`_spawn_bullet`.
    """
    player_input = entity.input
    player_body = entity.body
    if entity.tank.hitstun <= 0.:
        if not entity.tank.control and player_input.move:
            entity.tank.control = True
        if entity.tank.control:
            player_body.vel_x = player_input.move*TANK_SPEED
        if player_input.do_jump and entity.platform.touch_floor:
            engine.jump(entity)
        elif player_input.floats and player_input.do_jump and not entity.platform.touch_floor:
            engine.float(entity, dt)
            entity.body.max_ascending_speed = MAX_ASCENDING_SPEED
    else:
        entity.tank.hitstun -= dt
    
    tank = entity.tank
    tank.update(player_body.x, player_body.y)
    
    if player_input.accumulate_power and not player_input.release_power:
        player_input.time_power += dt
        #  print(player_input.time_power)
    
    if (not player_input.shooted and player_input.accumulate_power
        and player_input.release_power):
        player_input.accumulate_power = False
        player_input.shoots = True
        
    if player_input.shoots:
        engine.shoot(entity)
        player_input.shoots = False
        player_input.shooted = True
