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

tank = namedtuple("tank", "id x y vel_x vel_y damage")
tank_struct = struct.Struct("!iffffi")

bullet = namedtuple("bullet", "id x y vel_x vel_y owner power")
bullet_struct = struct.Struct("!iffffif")

SnapshotDiff = namedtuple("SnapshotDiff", "tanks bullets")
DiffSection = namedtuple("DiffSection", "created destroyed modified")

POS_X = 1
POS_Y = 2
VEL_X = 3
VEL_Y = 4
DAMAGE = 5

DIFF_TABLE = {
    "x": POS_X,
    "y": POS_Y,
    "vel_x": VEL_X,
    "vel_y": VEL_Y,
    "damage": DAMAGE
}

class Snapshot:
    def __init__(self, engine, tick=0):
        self._ack = False
        self.tick = tick
        self.snapshot = self._make_from_engine(engine)
        
    def _make_from_engine(self, engine):
        snapshot = {}
        tanks = {}
        bullets = {}
        used_tanks = engine.tank_pool._used
        for atank in used_tanks:
            body = atank.body
            tank_snapshot = tank(atank.id, body.x, body.y,
                body.vel_x, body.vel_y, atank.tank.damage)
            tanks[atank.id] = tank_snapshot
        snapshot["tanks"] = tanks
        used_bullets = engine.bullet_pool._used
        for abullet in used_bullets:
            body = abullet.body
            bullet_snapshot = bullet(abullet.id, body.x, body.y,
                body.vel_x, body.vel_y, abullet.bullet.owner.id,
                abullet.bullet.power)
            bullets[abullet.id] = bullet_snapshot
        snapshot["bullets"] = bullets
        return snapshot
    
    def diff(self, other_snapshot):
        other_tanks = other_snapshot.snapshot["tanks"]
        self_tanks = self.snapshot["tanks"]
        tanks_diff = Snapshot._generate_diff_section(self_tanks,
            other_tanks)
        other_bullets = other_snapshot.snapshot["bullets"]
        self_bullets = self.snapshot["bullets"]
        bullets_diff = Snapshot._generate_diff_section(self_bullets,
            other_bullets)
        return SnapshotDiff(tanks_diff, bullets_diff)
    
    @staticmethod
    def _generate_diff_section(self_entities, other_entities):
        diff_section = DiffSection(deque(), deque(), deque())
        created = diff_section.created
        destroyed = diff_section.destroyed
        modified = diff_section.modified
        for self_ent_id in self_entities:
            self_entity = self_entities.get(self_ent_id)
            other_entity = other_entities.get(self_ent_id)
            if other_entity is None:
                created.append(self_entity)
                continue
            modified_fields = deque()
            for field in self_entity._fields:
                value = getattr(self_entity, field)
                if value == getattr(other_entity, field):
                    continue
                modified_fields.append((DIFF_TABLE[field], value))
            modified.append((self_ent_id, modified_fields))
        
        for other_ent_id in other_entities:
            other_entity = other_entities[other_ent_id]
            if self_entities.get(other_ent_id) is not None:
                continue
            destroyed.append(other_ent_id)
        
        return diff_section
    
    @staticmethod
    def _diff_to_data(diff_section, entity_struct):
        to_bytes = int.to_bytes
        diff_data = bytearray()
        diff_data += to_bytes(len(diff_section.created), 4, "big")
        for entity in diff_section.created:
            diff_data += entity_struct.pack(*entity)
        diff_data += to_bytes(len(diff_section.destroyed), 4, "big")
        for id_ in diff_section.destroyed:
            diff_data += to_bytes(id_, 4, "big")
        diff_data += to_bytes(len(diff_section.modified), 4, "big")
        for id_, fields in diff_section.modified:
            print(id_, fields)
        return diff_data
    
    @staticmethod
    def _to_network(diff):
        data = bytearray()
        data += Snapshot._diff_to_data(diff.tanks, tank_struct)
        data += Snapshot._diff_to_data(diff.tanks, bullet_struct)
        return data
    
    @property
    def ack(self):
        return self.ack
            
    def to_network(self):
        """Returns bytes of the current snapshot to send over the network."""
        data = bytearray()
        snapshot = self.snapshot
        data += protocol.di_i.pack(protocol.SNAPSHOT, self.tick)
        data += protocol.mono.pack(len(snapshot["tanks"]))
        snapshot_tanks = snapshot["tanks"]
        for tank in snapshot_tanks:
            data += tank_struct.pack(*snapshot_tanks[tank])
        data += protocol.mono.pack(len(snapshot["bullets"]))
        snapshot_bullets = snapshot["bullets"]
        for bullet in snapshot_bullets:
            data += bullet_struct.pack(*snapshot_bullets[bullet])
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
