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
from .ogf4py3.component import Body, FloorCollision
from .component import TankGraphic, PlayerInput
from .constant import TANK_SPEED, VHEIGHT as G

@toyblock.System
def update_tank_graphic(self, entity):
    body = entity[Body]
    entity[TankGraphic].set_position(body.x, body.y)

@toyblock.System
def update_user_input(self, entity, dt):
    player_input = entity[PlayerInput]
    player_body = entity[Body]
    player_body.vel_x = player_input.move*TANK_SPEED
    if player_input.do_jump and entity[FloorCollision].touch_floor:
        player_body.vel_y = G/2.
        player_input.do_jump = False
    elif player_input.floats and player_input.do_jump and not entity[FloorCollision].touch_floor:
        player_input.time_floating += dt
        player_body.apply_force(dt, y=G*1.5)
        
    aim_pointer = player_input.aim_pointer
    cannon_position = entity[TankGraphic].cannon.position
    angle = atan2(aim_pointer[1] - cannon_position[1], aim_pointer[0] - cannon_position[0])
    player_input.cannon_angle = angle
    entity[TankGraphic].cannon.rotation = -degrees(angle)
    
