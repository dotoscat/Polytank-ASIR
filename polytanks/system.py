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
from .ogf4py3 import toyblock3, get_angle_from
from .constant import TANK_SPEED, VHEIGHT as G

@toyblock3.system("body", "tank_graphic")
def update_tank_graphic(self, entity):
    body = entity.body
    entity.tank_graphic.set_position(body.x, body.y)

@toyblock3.system("player_input", "body", "floor_collision")
def update_user_input(self, entity, dt, engine):
    """
    :obj:`engine` deberá tener como método :meth:`player_shoots`
    o el método :meth:`_spawn_bullet`.
    """
    player_input = entity.player_input
    player_body = entity.body
    player_body.vel_x = player_input.move*TANK_SPEED
    if player_input.do_jump and entity.floor_collision.touch_floor:
        player_body.vel_y = G/2.
        player_input.do_jump = False
    elif player_input.floats and player_input.do_jump and not entity.floor_collision.touch_floor:
        player_input.time_floating += dt
        player_body.apply_force(dt, y=G*1.5)
    
    if player_input.accumulate_power and not player_input.release_power:
        player_input.time_power += dt
        #  print(player_input.time_power)
    
    if player_input.accumulate_power and player_input.release_power:
        player_input.accumulate_power = False
        player_input.shoots = True
    
    aim_pointer = player_input.aim_pointer
    cannon_position = entity.tank_graphic.cannon.position
    angle = get_angle_from(*cannon_position, *aim_pointer)
    #  angle = atan2(aim_pointer[1] - cannon_position[1], aim_pointer[0] - cannon_position[0])
    player_input.cannon_angle = angle
    entity.tank_graphic.cannon.rotation = -degrees(angle)
    
    if player_input.shoots:
        engine.player_shoots()
        player_input.shoots = False
    
