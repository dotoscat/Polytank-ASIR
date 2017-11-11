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

import struct

JOIN = 1
LOGOUT = 2

JOINED = 3
DONE = 4

CLIENT_INPUT = 5

MOVE_LEFT = 6
MOVE_RIGHT = 7
STOP = 8
JUMP = 9
NO_JUMP = 10

MOVE = 5
AIM = 6
JUMP = 7
SHOOT = 8
SHOOTED = 9

SNAPSHOT = 10
START_GAME = 11

mono = struct.Struct("!i")
di = struct.Struct("!if")
di_i = struct.Struct("!ii")
tri = struct.Struct("!iff")
tetra = struct.Struct("!iiff")
tank = struct.Struct("!iffff")
bullet = struct.Struct("!iffif")
