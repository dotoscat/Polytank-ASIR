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
from inspect import getargspec
from . import engine

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

_structs = {
    engine.Body: struct.Struct("!iiff"),
    engine.Physics: struct.Struct("!ff")
}

_actions = {
    engine.Body.TANK: "create_tank"
}

_command = struct.Struct("!i")
_object_type = _command
_move = struct.Struct("!iif")

def command_is(command, data):
    return _command.unpack_from(data)[0] & command == command

def get_command(data):
    return _command.unpack_from(data)[0] & 0x00FF

def connect():
    return _command.pack(CONNECT)

def get_snapshot_buffer(the_engine):
    snapshot_buffer = bytearray()
    snapshot_buffer += _command.pack(SNAPSHOT)
    for entity in the_engine.entities():
        body = entity.get_component(engine.Body)
        object_def = engine.object_def[body.type]
        for type_ in object_def:
            component = entity.get_component(type_)
            component_values = [getattr(component, attr) for attr in component.__slots__]
            snapshot_buffer += _structs[type_].pack(*component_values)
    return snapshot_buffer

def set_engine_from_snapshot(the_engine, buffer_):
    position = _command.size
    buffer_len = len(buffer_)
    while position < buffer_len:
        print(position, buffer_len)
        object_type = _object_type.unpack_from(buffer_, position)[0]
        print('object_type', object_type)
        #You don't increase position because object_Type is part of Body
        object_def = engine.object_def[object_type]
        values = []
        for type_ in object_def:
            type_struct = _structs[type_]
            values.extend(type_struct.unpack_from(buffer_, position))
            position += type_struct.size
        action = _actions[object_type]
        engine_method = getattr(the_engine, action)
        method_spec = getargspec(engine_method)
        n_args = len(method_spec.args) - 1
        engine_method(*values[2:2+n_args])

def move(id_, direction):
    return _move.pack(MOVE, id_, direction)

def get_move(data):
    return _move.unpack(data)

def recreate_tank(id_, x, y):
    return _recreate_tank.pack(RECREATE_TANK, id_, x, y)

def get_recreate_tank(data):
    return _recreate_tank.unpack(data)
