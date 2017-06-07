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

class _Protocol(object):
    def __init__(self):
        self._command = struct.Struct("!i")
        
    def get_command(self, data):
        return self._command.unpack_from(data)[0]

class _Client(_Protocol):
    CONNECT = 0
    MOVE = 1
        
    def __init__(self):
        super(_Client, self).__init__()
        self._move_tank = struct.Struct("!iif")
        
    def connect(self):
        return self._command.pack(_Client.CONNECT)

    def move_tank(self, id_, direction):
        return self._move_tank.pack(_Client.MOVE, id_, direction)

    def get_move_tank(self, data):
        return self._move_tank.unpack(data)

class _Server(_Protocol):
    CREATE_TANK = 0
    
    def __init__(self):
        super(_Server, self).__init__()
        self._create_tank = struct.Struct("!iiff")
        
    def create_tank(self, id_, x, y):
        return self._create_tank.pack(_Server.CREATE_TANK, id_, x, y)
    
    def get_create_tank(self, data):
        return self._create_tank.unpack(data)

client = _Client()
server = _Server()
