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

import toyblock

class Body:
    __slots__ = ("type", "id", "x", "y")
    
    TANK = 1
    ID = 0
    
    def __init__(self, type_=None):
        self.type = type_
        self.id = Body.ID
        Body.ID += 1
        self.x = 0.0
        self.y = 0.0


class Physics:
    __slots__ = ("vel_x", "vel_y")
    
    def __init__(self):
        self.vel_x = 0.0
        self.vel_y = 0.0

class Cannon:
    __slots__ = ("aim", "canon_x", "canon_y")
    
    def __init__(self):
        self.aim = 0.0
        self.canon_x = 0.0
        self.canon_y = 0.0

object_def = {
    Body.TANK: (Body, Physics)
}

class Engine(object):

    MAX_ENTITIES = 32
        
    def __init__(self):
        args = (
            ((Body.TANK,), None),
            None
        )
        self._tanks_pool = toyblock.Pool(4, object_def[Body.TANK], args)
        self._entities = [None for i in range(Engine.MAX_ENTITIES)]
        self._n_entities = 0
        self._systems = {}
        #self._systems["physics"] = toyblock.System()#Add some callable for the system
        
    def _get_object_from_pool(self, pool):
        entity = pool.get()
        id_ = entity.get_component(Body).id
        self._entities[id_] = entity
        self._n_entities += 1
        return entity
    
    def move(self, id_, direction):
        entity = self._entities[id_]
        physics = entity.get_component(Physics)
        physics.vel_x = 32.0*direction
    
    def create_tank(self, x=0.0, y=0.0):
        entity = self._get_object_from_pool(self._tanks_pool)
        body = entity.get_component(Body)
        body.x = x
        body.y = y
        return entity, body.id
        
    def _physics_system(self, system, entity, dt):
        body = entity.get_component(Body)
        physics = entity.get_component(Physics)
        body.x = physics.vel_x*dt
        body.y = physics.vel_y*dt

    def entities(self):
        for ent in self._entities:
            if ent is None: continue
            yield ent
