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
from .engine import Engine

tank = namedtuple("tank", "id do_jump x y vel_x vel_y damage")
tank_struct = struct.Struct("!i?ffffi")

bullet = namedtuple("bullet", "id x y vel_x vel_y owner power")
bullet_struct = struct.Struct("!iffffif")

explosion = namedtuple("explosion", "id x y max_time")
explosion_struct = struct.Struct("!ifff")

gamemode = namedtuple("gamemode", "state total_time current_time")
gamemode_struct = struct.Struct("!bhh")

SnapshotDiff = namedtuple("SnapshotDiff", "tick gamemode tanks bullets explosions")
DiffSection = namedtuple("DiffSection", "created destroyed modified")

POS_X = 1
POS_Y = 2
VEL_X = 3
VEL_Y = 4
DAMAGE = 5
DO_JUMP = 6

FLOAT = 1
BOOL = 2
INT = 3

DIFF_TABLE = {
    "x": POS_X,
    "y": POS_Y,
    "vel_x": VEL_X,
    "vel_y": VEL_Y,
    "damage": DAMAGE,
    "do_jump": DO_JUMP
}

INV_DIFF_TABLE = {v: k for k, v in DIFF_TABLE.items()}

field_float = struct.Struct("!bf")
field_bool = struct.Struct("!b?")
field_int = struct.Struct("!bi")

id_nfields = struct.Struct("!ib")

body_set = frozenset(("x", "y", "vel_x", "vel_y"))
tank_set = frozenset(("damage",))
input_set = frozenset(("do_jump",))
timer_set = frozenset(("max_time",))

class Snapshot:
    def __init__(self, engine, game, tick=0):
        self.ack = False
        self.tick = tick
        self.snapshot = self._make_from_engine(engine, game)
        
    def _make_from_engine(self, engine, game):
        snapshot = {}
        tanks = {}
        bullets = {}
        explosions = {}
        used_tanks = engine.tank_pool._used
        for atank in used_tanks:
            body = atank.body
            tank_snapshot = tank(atank.id, atank.input.do_jump, body.x, body.y,
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
        used_explosions = engine.explosion_pool._used
        for anexplosion in used_explosions:
            body = anexplosion.body
            explosion_snapshot = explosion(anexplosion.id, body.x,
                body.y, anexplosion.timer.max_time)
            explosions[anexplosion.id] = explosion_snapshot
        snapshot["explosions"] = explosions
        snapshot["gamemode"] = gamemode(game.state, game.total_time, game.current_time)
        return snapshot
    
    def diff(self, other_snapshot):
        """Generates a SnapshotDiff with respect another snapshot."""
        
        self_game = self.snapshot["gamemode"]
        
        if self_game.state != other_snapshot.snapshot["gamemode"].state:
            gamemode_diff = gamemode(*self_game)
        else:
            gamemode_diff = gamemode(0, self_game.total_time, self_game.current_time)
        
        other_tanks = other_snapshot.snapshot["tanks"]
        self_tanks = self.snapshot["tanks"]
        tanks_diff = Snapshot._generate_diff_section(self_tanks,
            other_tanks)
        other_bullets = other_snapshot.snapshot["bullets"]
        self_bullets = self.snapshot["bullets"]
        bullets_diff = Snapshot._generate_diff_section(self_bullets,
            other_bullets)
        other_explosions = other_snapshot.snapshot["explosions"]
        self_explosions = self.snapshot["explosions"]
        explosions_diff = Snapshot._generate_diff_section(self_explosions,
            other_explosions)
        return SnapshotDiff(self.tick, gamemode_diff, tanks_diff,
            bullets_diff, explosions_diff)
    
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
        data += Snapshot._diff_to_data(diff.explosions, explosion_struct)
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
            deleted.appendleft(id_[0])
        offset += deleted_size
        
        N_ENTITIES_MODIFIED = from_bytes(data[offset:offset + 1], "big")
        offset += 1
        modified = deque()
        for entities in range(N_ENTITIES_MODIFIED):
            id_, FIELDS = id_nfields.unpack_from(data, offset)
            offset += id_nfields.size
            modified_fields = deque()
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
                modified_fields.appendleft((INV_DIFF_TABLE[field], value))
            modified.appendleft((id_, modified_fields))
            
        diff_section = DiffSection(created, deleted, modified)
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
        bullets_section, offset = Snapshot._data_to_diff(data, offset,
            bullet, bullet_struct)
        explosions_section, offset = Snapshot._data_to_diff(data, offset,
            explosion, explosion_struct)
        snapshot_diff = SnapshotDiff(tick, tanks_section, bullets_section,
            explosions_section)
        return snapshot_diff
        
    @staticmethod
    def set_engine_from_diff(diff, engine, player_tank):
        """Set engine from the diff."""
        tanks_modified = diff.tanks.modified
        
        for id_, fields in tanks_modified:
            tank = engine.entities.get(id_)
            for name, value in fields:
                if name in body_set:
                    setattr(tank.body, name, value)
                elif name in tank_set:
                    setattr(tank.tank, name, value)
                elif name in input_set:
                    if tank is player_tank: continue
                    setattr(tank.input, name, value)
                    print(id_, tank.input.do_jump)
                    
        bullets_created = diff.bullets.created
        bullets_destroyed = diff.bullets.destroyed
        
        for bullet in bullets_created:
            bullet_created = engine.spawn_bullet(bullet.id)
            bullet_created.set("body", x=bullet.x, y=bullet.y,
                vel_x=bullet.vel_x, vel_y=bullet.vel_y)
            bullet_created.set("bullet", power=bullet.power,
                owner=engine.entities[bullet.owner])
            engine.add_message((Engine.SHOOT, bullet.owner))
    
        for id_ in bullets_destroyed:
            engine.entities[id_].free()

        explosions_created = diff.explosions.created

        for explosion in explosions_created:
            explosion_created = engine._spawn_explosion(explosion.x,
                explosion.y, id_=explosion.id)
            explosion_created.timer.max_time = explosion.max_time
            engine.add_message((Engine.EXPLOSION, explosion.id))
