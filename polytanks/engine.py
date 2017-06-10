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
    __slots__ = ("x", "y", "id")
    
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.id = 0

_tank_def = (Body,)

class Engine(object):
    def __init__(self):
        self._id = 1
        self._tanks_pool = toyblock.Pool(4, _tank_def)
        self._entities = {}
    
    def _give_id(self):
        id_ = self._id
        self._id += 1
        return id_
    
    def _get_object_from_pool(self, pool, id_=0):
        entity = pool.get()
        body = entity.get_component(Body)
        if id_ == 0:
            id_ = self._give_id()
        body.id = id_
        self._entities[id_] = entity
        return entity, body
    
    def create_tank(self, x=0.0, y=0.0):
        entity, body = self._get_object_from_pool(self._tanks_pool)
        body.x = x
        body.y = y
        return body.id, x, y
    
    def recreate_tank(self, id_, x, y):
        entity, body = self._get_object_from_pool(self._tanks_pool, id_)
        body.x = x
        body.y = y
        
