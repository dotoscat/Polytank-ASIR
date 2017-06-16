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

#COMMANDS
CONNECT = 0x0001
DISCONNECT = 0x0002
INPUT = 0x0003
SNAPSHOT = 0x0004

#INPUT
MOVE_LEFT = 0x0100 << 1
MOVE_RIGHT = 0x0100 << 2
PRESS_SHOT = 0x0100 << 3
RELEASE_SHOT = 0x0100 << 4
JUMP = 0x0100 << 5
AIM = 0x0100 << 6

#OBJECT TYPE
TANK = 0x0100

_buffer = bytearray(64)
_buffer_iterator = range(len(_buffer))

_command = struct.Struct("!xi")
_recreate_tank = struct.Struct("!iiff")
_move = struct.Struct("!iif")

def reset_buffer():
    for i in _buffer_iterator:
        _buffer[i] = 0

def command_is(command, data):
    return _command.unpack_from(data)[0] & command == command

def get_command(data):
    return _command.unpack_from(data)[0]

def connect():
    _command.pack_into(_buffer, 0, CONNECT)
    return _buffer

def move(id_, direction):
    return _move.pack(MOVE, id_, direction)

def get_move(data):
    return _move.unpack(data)

def recreate_tank(id_, x, y):
    return _recreate_tank.pack(RECREATE_TANK, id_, x, y)

def get_recreate_tank(data):
    return _recreate_tank.unpack(data)
