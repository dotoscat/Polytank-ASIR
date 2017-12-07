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

import sys
from collections import deque
import logging
from random import choice
from math import degrees
import pyglet

from pyglet.sprite import Sprite
from pyglet.window import key
from .ogf4py3 import gui
from .ogf4py3 import magnitude_to_vector, get_angle_from, Connection
from .ogf4py3 import toyblock3
from .ogf4py3 import Scene
from .ogf4py3 import system
from .system import update_user_input
from .constant import G
from . import engine, protocol, builder, level, constant, assets
from .snapshot import Snapshot
from .engine import Engine

class TankGraphic:
    def __init__(self, batch, group):
        self.base = Sprite(assets.images["tank-base"], batch=batch, group=group[2])
        self.cannon = Sprite(assets.images["tank-cannon"], batch=batch, group=group[1])
        
@toyblock3.system("body", "tank_graphic")
def update_tank_graphic(self, entity):
    body = entity.body
    tank = entity.tank
    tank.update(body.x, body.y)
    entity.tank_graphic.base.set_position(body.x, body.y)
    entity.tank_graphic.cannon.set_position(tank.cannon_x, tank.cannon_y)

systems = engine.systems
systems.append(system.sprite)
systems.append(update_tank_graphic)
# Remove systems from client that can alter game state
systems.remove(engine.system_alive_zone)
#systems.remove(system.lifespan)
systems.remove(engine.system_client_collision)

class Client(Scene):
    
    class Point:
        def __init__(self, x=0., y=0.):
            self.x = x
            self.y = y
            
        @property
        def point(self):
            return (self.x, self.y)
            
        @point.setter
        def point(self, pair):
            if not isinstance(pair, tuple):
                raise TypeError("Use a tuple for the point")
            self.x = pair[0]
            self.y = pair[1]
        
        def __iter__(self):
            return iter((self.x, self.y))
        
        def __getitem__(self, i):
            if not isinstance(i, int):
                raise TypeError("Use an integer for indexing")
            if i == 0: return self.x
            if i == 1: return self.y

    def __init__(self, connection):
        super().__init__(5)
        
        self.connection = connection
        self._joined = False
        self.tank = None
        self._send_cannon_rotation = False
        
        builder.tank.add("tank_graphic", TankGraphic, self.batch, self.group)
        builder.bullet.add("sprite", Sprite, assets.images["bullet"],
            batch=self.batch, group=self.group[2])
        builder.platform.add("sprite", Sprite, assets.images["platform"],
            batch=self.batch, group=self.group[0])
        builder.explosion.add("sprite", Sprite, assets.images["explosion"],
            batch=self.batch, group=self.group[3])
        builder.powerup.add("sprite", Sprite, assets.images["heal"],
            batch=self.batch, group=self.group[3])
        
        self.player = assets.PlayerManager()
        player = self.player
        player.add(Engine.EXPLOSION, assets.sounds["explosion"])
        player.add(Engine.FLOAT, assets.sounds["float"], repeat=True)
        player.add(Engine.TOUCH_FLOOR, assets.sounds["hit-platform"])
        player.add(Engine.JUMP, assets.sounds["jump"])
        player.add(Engine.POWERUP, assets.sounds["powerup"])
        player.add(Engine.SHOOT, assets.sounds["shoot"])
        
        self.engine = engine.Engine()
        level.load_level(level.basic, self.engine.platform_pool)

        self.engine.bullet_pool.init(self.init_entity)
        self.engine.bullet_pool.clean(self.clean_entity)
        self.engine.explosion_pool.init(self.init_entity)
        self.engine.explosion_pool.clean(self.clean_entity)
        self.engine.powerup_pool.init(self.init_entity)
        self.engine.powerup_pool.clean(self.clean_entity)
        
        self.cursor_point = Client.Point()
        self.cursor = Sprite(assets.images["eyehole"], batch=self.batch, group=self.group[3])
        
        self.damage = []
        self.dt = 0.
        self.last_server_tick = -1
        self.tick = 0
        self.snapshots = deque([], 32)
        
    def send_input(self, dt):
        if self.tank is None: return
        tank_input = self.tank.input
        #print(self.tick, tank_input.move, tank_input.cannon_angle,
        #    tank_input.accumulate_power, tank_input.do_jump)
        data = protocol.input.pack(protocol.CLIENT_INPUT, self.tick,
            tank_input.move, tank_input.cannon_angle,
            tank_input.accumulate_power, tank_input.do_jump)
        self.conn.socket.send(data)

    def init(self):
        self.director.set_exclusive_mouse(True)
        self.cursor_point.x = constant.VWIDTH/2.
        self.cursor_point.y = constant.VHEIGHT/2.

    def quit(self):
        self.director.set_exclusive_mouse(False)

    def clean_entity(self, entity):
        if (isinstance(entity, self.engine.bullet_pool)
            or isinstance(entity, self.engine.explosion_pool)
            or isinstance(entity, self.engine.powerup_pool)):
            entity.sprite.visible = False

    def init_entity(self, entity):
        if (isinstance(entity, self.engine.bullet_pool)
            or isinstance(entity, self.engine.explosion_pool)
            or isinstance(entity, self.engine.powerup_pool)):
            entity.sprite.visible = True
        logging.info("init", entity)

    def update(self, dt):
        # This comented part is a server thing (game mode) 
        #self.dt += dt
        #if self.dt > 3.:
        #    self.dt = 0.
        #    if choice((True, False)):
        #        powerup = self.engine._spawn_powerup(128., 128., "heal")
        #        powerup.sprite.image = assets.images["heal"]
        #self.send_input(dt)
        self.connection.tick()
        #self.engine.update(dt)
        if self._joined:
            for damage in self.damage:
                id_ = self.damage[damage]
                tank = self.engine.entities[id_]
                damage.value = tank.tank.damage
        update_tank_graphic()
        self._upgrade_pointer()
        system.sprite()
        player_play = self.player.play
        for message, entity in self.engine.messages:
            player_play(message)
        self.tick += 1
        
    def _upgrade_pointer(self):
        if not self._joined: return
        aim_pointer = self.player_input.aim_pointer
        cannon_position = self.tank.tank_graphic.cannon.position
        angle = get_angle_from(*cannon_position, *aim_pointer)
        self.player_input.cannon_angle = angle
        self.tank.tank_graphic.cannon.rotation = -degrees(angle)
        if self._send_cannon_rotation:
            self._send_cannon_rotation = False

    def on_key_press(self, symbol, modifier):
        if self._joined and symbol == key.L:
            print("logout pressed")
            self.logout()
        if not self._joined:
            return
        if symbol in (key.A, key.LEFT):
            self.player_input.move_left()
        elif symbol in (key.D, key.RIGHT):
            self.player_input.move_right()
        elif symbol in (key.W, key.UP):
            self.player_input.jump()

    def on_key_release(self, symbol, modifier):
        if not self._joined: return
        if symbol in (key.A, key.D, key.LEFT, key.RIGHT) and self.player_input.moves():
            self.player_input.stop_moving()
        if symbol in (key.UP, key.W) and self.player_input.do_jump:
            self.player_input.not_jump()

    def on_mouse_motion(self, x, y, dx, dy):
        #  print("mouse motion", x, y, dx, dy)
        self._update_mouse(dx, dy)
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        #  print("mouse drag", x, y, dx, dy)
        self._update_mouse(dx, dy)

    def _update_mouse(self, dx, dy):
        vdx, vdy = self.director.get_virtual_xy(dx, dy)
        self.cursor_point.x += vdx
        self.cursor_point.y += vdy
        if self.cursor_point.x < 0.:
            self.cursor_point.x = 0.
        elif self.cursor_point.x > constant.VWIDTH:
            self.cursor_point.x = constant.VWIDTH
        if self.cursor_point.y < 0.:
            self.cursor_point.y = 0.
        elif self.cursor_point.y > constant.VHEIGHT:
            self.cursor_point.y = constant.VHEIGHT
        if not self._joined: return 
        self.player_input.aim_pointer = self.cursor_point
        self.cursor.position = self.cursor_point.point
        self._send_cannon_rotation = True

    def on_mouse_press(self, x, y, button, modifiers):
        if not self._joined: return
        self.tank.input.accumulate_power = True
        
    def on_mouse_release(self, x, y, button, modifiers):
        if not self._joined: return
        self.tank.input.accumulate_power = False

    def _shoot(self, id_):
        entity = self.engine.entities[id_]
        if entity is None: return
        entity.input.accumulate_power = False
        entity.input.shoots = True

    def listen(self, data, socket):
        command = protocol.mono.unpack_from(data)[0]
        
        if command == protocol.DONE:
            self._done()
        elif command == protocol.JOINED:
            command, id_, v1, v2 = protocol.tetra.unpack(data)
            self.joined(id_, v1, v2)
        elif command == protocol.START_GAME:
            self.start_game(data)
            command = protocol.mono.unpack_from(data)[0]
        elif command == protocol.SNAPSHOT:
            command, tick = protocol.di_i.unpack_from(data)
            if tick <= self.last_server_tick:
                print(tick, "rejected!")
                return
            self.last_server_tick = tick
            snapshot_diff = Snapshot.from_network(data)
            self.snapshots.appendleft(snapshot_diff)
            self.conn.socket.send(protocol.mono.pack(protocol.CLIENT_ACK))
            Snapshot.set_engine_from_diff(snapshot_diff, self.engine, self.tank)
            
    def start_game(self, data):
        offset = protocol.mono.size
        players = 0
        tanks = data[protocol.mono.size:]
        self.damage = {}
        for id_, x, y in protocol.tri.iter_unpack(tanks):
            if id_ == 0: continue
            players += 1
            print("player", self.tank.id, id_)
            label = gui.NumberLabel("%", batch=self.batch, group=self.group[4])
            self.damage[label] = id_
            label.value = 0
            label.y = 8.
            label.x = x
            if id_ == self.tank.id:
                continue
            print(id_, x, y)
            tank = self.engine.create_tank(id_)
            tank.set("body", x=x, y=y)

    def joined(self, id_, x, y):
        print("Joined with id", id_, x, y)
        self.tank = self.engine.create_tank(id_)
        self.tank.set("body", x=x, y=x)
        self.player_input = self.tank.input
        self.player_input.client = True
        self._joined = True
        self.conn.socket.send(protocol.mono.pack(protocol.JOINED))
    
    def logout(self):
        print("logout", self._joined)
        if not self._joined: return
        self.conn.socket.send(protocol.mono.pack(protocol.LOGOUT))

    def _done(self):
        self.tank.free()
        self.tank = None
        self.player_input = None
        self._joined = False
