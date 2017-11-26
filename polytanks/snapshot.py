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

SnapshotDiff = namedtuple("SnapshotDiff", "tick tanks bullets")
DiffSection = namedtuple("DiffSection", "created destroyed modified")

POS_X = 1
POS_Y = 2
VEL_X = 3
VEL_Y = 4
DAMAGE = 5

FLOAT = 1
BOOL = 2
INT = 3

DIFF_TABLE = {
    "x": POS_X,
    "y": POS_Y,
    "vel_x": VEL_X,
    "vel_y": VEL_Y,
    "damage": DAMAGE
}

INV_DIFF_TABLE = {v: k for k, v in DIFF_TABLE.items()}

field_float = struct.Struct("!bf")
field_bool = struct.Struct("!b?")
field_int = struct.Struct("!bi")

id_nfields = struct.Struct("!ib")

class Snapshot:
    def __init__(self, engine, tick=0):
        self.ack = False
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
        """Generates a SnapshotDiff with respect another snapshot."""
        other_tanks = other_snapshot.snapshot["tanks"]
        self_tanks = self.snapshot["tanks"]
        tanks_diff = Snapshot._generate_diff_section(self_tanks,
            other_tanks)
        other_bullets = other_snapshot.snapshot["bullets"]
        self_bullets = self.snapshot["bullets"]
        bullets_diff = Snapshot._generate_diff_section(self_bullets,
            other_bullets)
        return SnapshotDiff(self.tick, tanks_diff, bullets_diff)
    
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
        diff_data += to_bytes(len(diff_section.created), 1, "big")
        for entity in diff_section.created:
            diff_data += entity_struct.pack(*entity)
        diff_data += to_bytes(len(diff_section.destroyed), 1, "big")
        for id_ in diff_section.destroyed:
            diff_data += to_bytes(id_, 4, "big")
        diff_data += to_bytes(len(diff_section.modified), 1, "big")
        for id_, fields in diff_section.modified:
            diff_data += id_nfields.pack(id_, len(fields))
            for field, value in fields:
                if type(value) is float:
                    diff_data += to_bytes(FLOAT, 1, "big")
                    diff_data += field_float.pack(field, value)
                elif type(value) is bool:
                    diff_data += to_bytes(BOOL, 1, "big")
                    diff_data += field_bool.pack(field, value)
                elif type(value) is int:
                    diff_data += to_bytes(INT, 1, "big")
                    diff_data += field_int.pack(field, value)
                else:
                    print("Missing!")
        return diff_data
    
    @staticmethod
    def to_network(diff):
        data = bytearray()
        data += protocol.di_i.pack(protocol.SNAPSHOT, diff.tick)
        data += Snapshot._diff_to_data(diff.tanks, tank_struct)
        data += Snapshot._diff_to_data(diff.bullets, bullet_struct)
        return data
    
    @staticmethod
    def _data_to_diff(data, offset, entity, entity_struct):
        from_bytes = int.from_bytes
        
        n_entities_created = from_bytes(data[offset:offset + 1], "big")
        offset += 1
        created = deque()
        created_size = n_entities_created*entity_struct.size
        created_block = data[offset:offset + created_size]
        for entity_info in entity_struct.iter_unpack(created_block):
            created.appendleft(entity._make(entity_info))
        offset += created_size
        
        n_entities_deleted = from_bytes(data[offset:offset + 1], "big")
        offset += 1
        deleted_size = n_entities_deleted*4
        deleted_block = data[offset:offset + deleted_size]
        deleted = deque()
        for id_ in protocol.mono.iter_unpack(deleted_block):
            delete.appendleft(id_)
        offset += deleted_size
        
        N_ENTITIES_MODIFIED = from_bytes(data[offset:offset + 1], "big")
        offset += 1
        modified = deque()
        for entities in range(N_ENTITIES_MODIFIED):
            id_, FIELDS = id_nfields.unpack_from(data, offset)
            print("id", id_, "fields", FIELDS)
            offset += id_nfields.size
            for f in range(FIELDS):
                type_ = from_bytes(data[offset:offset + 1], "big")
                offset += 1
                if type_ == FLOAT:
                    field, value = field_float.unpack_from(data, offset)
                    offset += field_float.size
                elif type_ == BOOL:
                    field, value = field_bool.unpack_from(data, offset)
                    offset += field_bool.size
                elif type_ == INT:
                    field, value = field_int.unpack_from(data, offset)
                    offset += field_int.size
                else:
                    print("Error!!!")
                print("field", field, "value", value)
            
        diff_section = DiffSection(created, deleted, None)
        return diff_section, offset
    
    @staticmethod
    def from_network(data):
        """Convert a snapshot send from network to :class:`SnapshotDiff`.
            
            Parameters:
                data (byte): Data received from network
                
            Returns:
                SnapshotDiff
            
        """
        command, tick = protocol.di_i.unpack_from(data)
        offset = protocol.di_i.size
        tanks_section, offset = Snapshot._data_to_diff(data, offset,
            tank, tank_struct)
        #bullets_section, offset = Snapshot._data_to_diff(data, offset,
        #    bullet, bullet_struct)
        print(tanks_section)
        snapshot_diff = SnapshotDiff(tick, tanks_section, None)
        return snapshot_diff
    
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
