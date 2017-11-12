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

tank = namedtuple("tank", "id x y")
tank_struct = struct.Struct("!iff")

class Snapshot:
    """To make snapshots is better pass the engine (and forget it)."""
    def __init__(self, engine):
        self._engine = engine
        self.tick = 0
        self.snapshots = deque()
    
    def __iadd__(self, value):
        snapshot = self.make()
        self.snapshots.appendleft((self.tick, snapshot))
        self.tick += value
        return self

    def make(self):
        snapshot = {}
        tanks = deque()
        used_tanks = self._engine.tank_pool._used
        for atank in used_tanks:
            tank_snapshot = tank(atank.id, atank.body.x, atank.body.y)
            tanks.append(tank_snapshot)
        snapshot["tanks"] = tanks
        return snapshot
        
    def digest(self):
        """Returns bytes of the current snapshot to send over the network."""
        if not self.snapshots:
            return b'click!'
        data = bytearray()
        tick, current = self.snapshots[0]
        data += protocol.di_i.pack(protocol.SNAPSHOT, tick)
        data += protocol.mono.pack(len(current["tanks"]))
        for tank in current["tanks"]:
            data += tank_struct.pack(*tank)
        return data

    def restore(self, data):
        """Restore engine from the data."""
        protocol, tick = protocol.di_i.unpack_from(data)
        pass
