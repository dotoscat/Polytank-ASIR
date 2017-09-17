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

import pyglet
from pyglet.sprite import Sprite
from pyglet.gl import glViewport, glOrtho, glMatrixMode, glLoadIdentity
from pyglet import gl
import toyblock
from .components import (Body, PlatformSprite, FloorCollision,
    Collision, Input)
from . import constants
from .constants import Type, GRAVITY

@toyblock.system
def input_sys(system, entity, engine):
    input_ = entity[Input]
    body = entity[Body]
    floor_collision = entity[FloorCollision]

    if input_.left:
        body.vel_x = -constants.SPEED
        entity[Sprite].image = engine.assets["car_left"]
    if input_.right:
        body.vel_x = constants.SPEED
        entity[Sprite].image = engine.assets["car_right"]
    if not input_.left and not input_.right and body.vel_x != 0.:
        body.vel_x = 0.
    # print(input_.jump, input_.jump_pressed, input_._jumps)
    if input_.jump and input_.jump_pressed and floor_collision.touch_floor:
        floor_collision.touch_floor = False
        body.vel_y = constants.JUMP
        body.gravity = True
        input_._jumps -= 1
        engine.decrease_fuel(5.)
        engine.sound["second_jump"].play()
    elif (input_.jump and input_.jump_pressed
        and not floor_collision.touch_floor and input_._jumps > 0):
        body.vel_y = constants.JUMP/1.5
        input_._jumps -= 1
        engine.decrease_fuel(2.5)
        engine.sound["second_jump"].play()
    elif not input_._jump and body.vel_y > 0.0:
        body.vel_y = 0.
    input_.jump_pressed = False
    if floor_collision.touch_floor:
        input_.reset_jumps()

@toyblock.system
def physics(system, entity, dt, gravity):
    body = entity[Body]
    body.update(dt, gravity)

@toyblock.system
def update_graphics(system, entity):
    body = entity[Body]
    entity[Sprite].set_position(body.x, body.y)

@toyblock.system
def recycle(system, entity):
    if entity[Body].y + 16. < 0.0:
        entity.free()

@toyblock.system
def update_platform_sprite(system, entity):
    body = entity[Body]
    platform = entity[PlatformSprite]
    platform.x = body.x
    platform.y = body.y

@toyblock.system
def update_collision(system, entity):
    body = entity[Body]
    collision = entity[Collision]
    collision.x = body.x
    collision.y = body.y

def player_powerup(player, powerup, engine):
    powerup.free()
    engine.increase_fuel(25.)
    engine.sound["fuel_pickup"].play()

collision_t = {
    (Type.PLAYER, Type.POWERUP): player_powerup
}

@toyblock.system
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

@toyblock.system
def platform_collision(system, entity, engine):
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
    if not touched and floor_collision.touch_floor:
        engine.sound["landing"].play()

def do(dt, engine):
    input_sys(engine)
    physics(dt, -GRAVITY)
    recycle()
    update_collision()
    platform_collision(engine)
    do_collision(engine)
    update_platform_sprite()
    update_graphics()
