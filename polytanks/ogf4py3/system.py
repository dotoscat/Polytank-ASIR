# ogf4py3
# Copyright (C) 2017  Oscar Triano @cat_dotoscat

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyglet.sprite import Sprite
import toyblock
from .component import Body, FloorCollision, Collision, Timer

@toyblock.System
def physics(system, entity, dt, gravity):
    body = entity[Body]
    body.update(dt, gravity)

@toyblock.System
def sprite(system, entity):
    body = entity[Body]
    entity[Sprite].set_position(body.x, body.y)

@toyblock.System
def collision(system, entity):
    body = entity[Body]
    entity[Collision].update(body.x, body.y)

class CheckCollision(toyblock.System):
    """System for collisions. This is a naive implementation.
    
    With a :class:Collision component set the attribute *set* and then
    fills its *collides_with* the types, or groups, that you want collide with.
    
    Example:
        PLAYER = 1
        BALL = 1 << 1
        ENEMIES = 1 << 2
    
        Player.set(Collision, {"collides_with": BALL | ENEMIES, "type": PLAYER})
        Ball.set(Collision, {"type": BALL})
    
        my_collision = CheckCollision()
        my_collision.table[(PLAYER, BALL)] = player_ball_callback
    """
    def __init__(self):
        super().__init__(self._call)
        self._table = {}
        
    @property
    def table(self):
        """Return a table where you assign a pair with its callable."""
        return self._table    
    
    def _call(self, system, entity):
        entities = system.entities
        entity_collision = entity[Collision]
        table = self._table
        for sysentity in entities:
            if sysentity == entity: continue
            sysentity_collision = sysentity[Collision]
            if not entity_collision.collides_with & sysentity_collision.type_ == sysentity_collision.type_:
                continue
            if not entity_collision.intersects(sysentity_collision):
                continue
            table[(entity_collision.type_, sysentity_collision.type_)](entity, sysentity)

@toyblock.System
def platform_collision(system, entity, platforms, callback=None):
    """This system requires the next additional parameters
    
    *callback* accepts as parameter the entity.
    
    Parameters:
        platforms (iterable of platforms)
        callback (callable or None): callback when an entity touch the floor. If None, then is not triggered.
    """
    body = entity[Body]
    floor_collision = entity[FloorCollision]
    points = floor_collision.get_points(body.x, body.y)
    body.gravity = True
    touched = floor_collision.touch_floor
    floor_collision.platform = None
    for platform in platforms:
        platform_collision = platform[Collision]
        if (body.vel_y > 0.0 or
        (points[0] not in platform_collision and
        points[1] not in platform_collision)):
            continue
        body.y = platform_collision.top
        body.vel_y = 0.0
        body.gravity = False
        floor_collision.platform = platform
        break
    if callable(callback) and not touched and floor_collision.touch_floor:
        callback(entity)

class AliveZone(toyblock.System):
    """This is a basic system where the entities are freed if they are out of bounds.
    
    The parameters are relative to left and bottom.
    
    Parameters:
        x1 (float):
        y1 (float):
        x2 (float):
        y2 (float):
        
    Returns:
        An :class:AliveZone.    
        
    Example:
    
        .. code-block:: python
            
            safezone = AliveZone(0., 0., SCREEN_WIDTH, SCREEN_HEIGHT)
            entity_systems = (safezone, physics, ...)
            #  ...
    """
    def __init__(self, x1, y1, x2, y2):
        super().__init__(self._call)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    def _call(self, system, entity):
        body = entity[Body]
        if not (self.x1 <= body.x <= self.x2 and self.y1 <= body.y <= self.y2):
            entity.free()

@toyblock.System
def lifespan(system, entity, dt):
    timer = entity[Timer]
    timer.time += dt
    if timer.done:
        timer.time = 0.
        entity.free()
