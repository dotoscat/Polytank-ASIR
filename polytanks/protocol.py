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

CONNECT = 0
CREATE_TANK = 1
MOVE = 2

_command = struct.Struct("!i")
_create_tank = struct.Struct("!iiff")
_move_tank = struct.Struct("!iif")

def get_command(data):
    return _command.unpack_from(data)[0]

def connect():
    return self._command.pack(CONNECT)

def move_tank(id_, direction):
    return _move_tank.pack(_Client.MOVE, id_, direction)

def get_move_tank(id_, direction):
    return _move_tank.unpack(data)

def create_tank(id_, x, y):
    return _create_tank.pack(CREATE_TANK, id_, x, y)

def get_create_tank(data):
    return create_tank.unpack(data)
