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
from collections import deque, namedtuple
from . import protocol

TANK = 1
BULLET = 2
EXPLOSION = 3
POWERUP = 4

tank = namedtuple("tank", "id x y vel_x vel_y damage")
tank_struct = struct.Struct("!iffffi")

class Snapshot:
    def __init__(self, engine, tick=0):
        self._ack = False
        self.tick = tick
        self.snapshot = self._make_from_engine(engine)
        
    def _make_from_engine(self, engine):
        snapshot = {}
        tanks = deque()
        used_tanks = engine.tank_pool._used
        for atank in used_tanks:
            body = atank.body
            tank_snapshot = tank(atank.id, body.x, body.y,
                body.vel_x, body.vel_y, atank.tank.damage)
            tanks.append(tank_snapshot)
        snapshot["tanks"] = tanks
        return snapshot
    
    @property
    def ack(self):
        return self.ack
            
    def to_network(self):
        """Returns bytes of the current snapshot to send over the network."""
        data = bytearray()
        snapshot = self.snapshot
        data += protocol.di_i.pack(protocol.SNAPSHOT, self.tick)
        data += protocol.mono.pack(len(snapshot["tanks"]))
        for tank in snapshot["tanks"]:
            data += tank_struct.pack(*tank)
        return data

    @staticmethod
    def restore(data, engine):
        """Restore engine from the data."""
        command, tick = protocol.di_i.unpack_from(data)
        n_tanks = protocol.mono.unpack_from(data, protocol.di_i.size)[0]
        #print("n tanks", n_tanks)
        offset = protocol.di_i.size + protocol.mono.size
        tanks_data = data[offset:offset + n_tanks*tank_struct.size]
        for id_, x, y, vel_x, vel_y, damage in tank_struct.iter_unpack(tanks_data):
            tank = engine.entities.get(id_)
            if tank is None:
                print("tank {} does not exist.".format(id_))
                continue
            body = tank.body
            body.x = x
            body.y = y
            body.vel_x = vel_x
            body.vel_y = vel_y
            tank.tank.damage = damage
        return tick
