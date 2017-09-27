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
from .component import Body, FloorCollision, Collision

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
    collision = entity[Collision]
    collision.x = body.x
    collision.y = body.y

def player_powerup(player, powerup, engine):
    powerup.free()
    engine.increase_fuel(25.)
    engine.sound["fuel_pickup"].play()

#collision_t = {
#    (Type.PLAYER, Type.POWERUP): player_powerup
#}

@toyblock.System
def do_collision(system, entity, game_state):
    entities = system.entities
    entity_collision = entity[Collision]
    for sysentity in entities:
        #3prin
        if sysentity == entity: continue
        sysentity_collision = sysentity[Collision]
        #print(entity_collision.x, entity_collision.y, sysentity_collision.x, sysentity_collision.y)
        if not (entity_collision.intersects(sysentity_collision)
            and entity_collision.collides_with & sysentity_collision.type
            == sysentity_collision.type): continue
        collision_t[(entity_collision.type, sysentity_collision.type)](entity, sysentity, game_state)

@toyblock.System
def platform_collision(system, entity, callback=None):
    body = entity[Body]
    floor_collision = entity[FloorCollision]
    platforms = engine.platforms
    if floor_collision.touch_floor:
        platform_collision = floor_collision.platform[Collision]
        body.y = floor_collision.platform[Body].y + 8.
        points = floor_collision.get_points(body.x, body.y)
        #if (points[0] in platform_collision or points[1] in platform_collision):
        #    return
    points = floor_collision.get_points(body.x, body.y)
    body.gravity = True
    touched = floor_collision.touch_floor
    floor_collision.touch_floor = False
    for platform in platforms:
        platform_collision = platform[Collision]
        if (body.vel_y > 0.0 or
        (points[0] not in platform_collision and
        points[1] not in platform_collision)):
            continue
        body.y = platform_collision.top
        body.vel_y = 0.0
        body.gravity = False
        floor_collision.touch_floor = True
        floor_collision.platform = platform
        break
    if callable(callback) and not touched and floor_collision.touch_floor:
        callback()
