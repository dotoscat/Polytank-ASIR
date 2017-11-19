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

bullet = namedtuple("bullet", "id x y vel_x vel_y owner power")
bullet_struct = struct.Struct("!iffffif")

message_struct = struct.Struct("!pi")

class Snapshot:
    def __init__(self, engine, tick=0):
        self._ack = False
        self.tick = tick
        self.snapshot = self._make_from_engine(engine)
        
    def _make_from_engine(self, engine):
        snapshot = {}
        tanks = deque()
        bullets = deque()
        used_tanks = engine.tank_pool._used
        for atank in used_tanks:
            body = atank.body
            tank_snapshot = tank(atank.id, body.x, body.y,
                body.vel_x, body.vel_y, atank.tank.damage)
            tanks.append(tank_snapshot)
        snapshot["tanks"] = tanks
        used_bullets = engine.bullet_pool._used
        for abullet in used_bullets:
            body = abullet.body
            bullet_snapshot = bullet(abullet.id, body.x, body.y,
                body.vel_x, body.vel_y, abullet.bullet.owner.id,
                abullet.bullet.power)
            bullets.append(bullet_snapshot)
        snapshot["bullets"] = bullets
        messages = [message for message in engine.messages]
        snapshot["messages"] = messages
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
        data += protocol.mono.pack(len(snapshot["bullets"]))
        for bullet in snapshot["bullets"]:
            data += bullet_struct.pack(*bullet)
        data += protocol.mono.pack(len(snapshot["messages"]))
        for message, entity in snapshot["messages"]:
            data += message_struct.pack(message.encode(), entity.id)
        return data

    @staticmethod
    def restore(data, engine):
        """Restore engine from the data."""
        command, tick = protocol.di_i.unpack_from(data)
        n_tanks = protocol.mono.unpack_from(data, protocol.di_i.size)[0]
        #print("n tanks", n_tanks)
        offset = protocol.di_i.size + protocol.mono.size
        tanks_offset = n_tanks*tank_struct.size
        tanks_data = data[offset:offset + tanks_offset]
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
        offset += tanks_offset
        n_bullets = protocol.mono.unpack_from(data, offset)[0]
        print("Número de balas del snapshot", n_bullets)
        offset += protocol.mono.size
        bullets_offset = n_bullets*bullet_struct.size
        bullets_data = data[offset:offset + bullets_offset]
        for id_, x, y, vel_x, vel_y, owner_id, power in bullet_struct.iter_unpack(bullets_data):
            bullet = engine.entities.get(id_)
            if bullet is None:
                bullet = engine.spawn_bullet(id_)
            bullet.set("body", x=x, y=y, vel_x=vel_x, vel_y=vel_y)
            bullet.set("bullet", power=power, owner=engine.entities[owner_id])
        return tick
