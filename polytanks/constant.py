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

from . import assets

TANK = 1
PLATFORM = 1 << 1
BULLET = 1 << 2
EXPLOSION = 1 << 3
TANK_DEF = ("player_input", "floor_collision", "body", "tank_graphic")
PLATFORM_DEF = ("collision", "sprite")
BULLET_DEF = ("body", "collision", "sprite")
EXPLOSION_DEF = ("body", "collision", "timer", "sprite")
VWIDTH = 400
VHEIGHT = 300
TANK_SPEED = 64.
SIZE = 16.
G = VHEIGHT
