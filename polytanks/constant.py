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

from pyglet.sprite import Sprite
from .ogf4py3.component import Body, Collision, FloorCollision
from .component import TankGraphic, PlayerInput

TANK = 1
PLATFORM = 2
BULLET = 3
TANK_DEF = (PlayerInput, FloorCollision, Body, TankGraphic)
PLATFORM_DEF = (Collision, Sprite)
BULLET_DEF = (Body, Sprite)
VWIDTH = 400
VHEIGHT = 300
TANK_SPEED = 64.
SIZE = 16.
