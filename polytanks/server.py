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

from functools import partial
import math
from math import degrees
from pprint import pprint
import asyncio
from . import protocol
from . import engine, level, bot

class Server(asyncio.DatagramProtocol):
    
    TICKRATE = 60
    
    def __init__(self, address, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = engine.Engine()
        level.load_level(level.basic, self.engine.platform_pool)
        self._address = address
        self._loop = asyncio.get_event_loop()
        self._loop.set_debug(debug)
        self._past_time = 0.
        self.transport = None
        self.dt = 0.
        self.secs = 0
        self.clients = {}
        self.players = [0]*4
        self.bots = [None]*4
        
        listen = self._loop.create_datagram_endpoint(lambda: self,
            local_addr=address)

        asyncio.ensure_future(listen)
        asyncio.ensure_future(self._tick(self._loop.time))
        
        #self.add_bot(bot.jumper)

    def add_bot(self, bot):
        for i, id_ in enumerate(self.players):
            if id_ != 0: continue
            tank = self.engine.create_tank()
            tank.set("body", x=200., y=100.)
            self.players[i] = tank.id
            self.bots[i] = partial(bot, tank)
            return
        raise Exception("Assure enough slots, players, for bots")
    
    def add_player(self, tank):
        for i, id_ in enumerate(self.players):
            if id_ != 0: continue
            self.players[i] = tank.id
            break
    
    def connection_made(self, transport):
        self.transport = transport
        asyncio.ensure_future(self._send_snapshot())
        print("Connection", transport)
    
    def connection_lost(self, cls):
        print("lost", cls)
    
    def datagram_received(self, data, addr):
        command = protocol.mono.unpack_from(data)[0]
        #print("command", command)
        if command == protocol.JOIN:
            self._join(addr)
        elif command == protocol.LOGOUT:
            self._logout(addr)
        elif command == protocol.JOINED:
            self._start_game(addr)
        elif command == protocol.CLIENT_INPUT:
            self.client_input(data)
            #print("client input", addr, len(data))

    def client_input(self, data):
        input_buffer = data[protocol.mono.size:]
        fdata_iterator = protocol.struct.iter_unpack("!f", input_buffer)
        idata_iterator = protocol.struct.iter_unpack("!i", input_buffer)
        for idata, fdata in zip(idata_iterator, fdata_iterator):
            tick = idata[0]
            n_input = next(idata_iterator)[0]
            next(fdata_iterator)
            if n_input:
                print("tick", tick)
            for i in range(n_input):
                command = next(idata_iterator)[0]
                next(fdata_iterator)
                if command == protocol.MOVE_LEFT:
                    print("mover izquierda")
                elif command == protocol.MOVE_RIGHT:
                    print("mover derecha")
                elif command == protocol.STOP:
                    print("parar")
                elif command == protocol.JUMP:
                    print("saltar")
                elif command == protocol.NO_JUMP:
                    print("no saltar")
                elif command == protocol.SHOOT:
                    print("disparar")
                elif command == protocol.NO_SHOOT:
                    print("no disparar")
                elif command == protocol.AIM:
                    value = next(fdata_iterator)[0]
                    next(idata_iterator)
                    print("apuntar", -degrees(value))

    def _start_game(self, addr):
        data_size = protocol.mono.size + len(self.players)*protocol.tri.size
        data = bytearray(data_size)
        protocol.mono.pack_into(data, 0, protocol.START_GAME)
        offset = protocol.mono.size
        entities = self.engine.entities
        for i, id_ in enumerate(self.players):
            if id_ == 0:
                protocol.tri.pack_into(data, offset, 0, 0., 0.)
            else:
                body = entities[id_].body
                protocol.tri.pack_into(data, offset, id_, body.x, body.y)
            offset += protocol.tri.size
        self.transport.sendto(data, addr)

    def _send_action_to_clients(self, command, id_):
        data = protocol.di_i.pack(command, id_)
        for client in self.clients:
            self.transport.sendto(data, client)

    def _jump(self, addr, pressed):
        tank = self.clients[addr]
        if pressed == 1.:
            tank.input.jump()
        else:
            tank.input.not_jump()

    def _shoot(self, addr, release):
        tank = self.clients[addr]
        if release == 1.:
            tank.input.accumulate_power = True
        else:
            tank.input.accumulate_power = False
            tank.input.shoots = True
            data = protocol.di_i.pack(protocol.SHOOTED, self.clients[addr].id)
            for client in self.clients:
                self.transport.sendto(data, client)

    def _join(self, addr):
        tank = self.engine.create_tank()
        self.clients[addr] = tank
        tank.set("body", x=128., y=128.)
        self.add_player(tank)
        print("Client {} {} added".format(addr, tank.id))
        print(self.players)
        message = protocol.tetra.pack(protocol.JOINED, tank.id, tank.body.x, tank.body.y)
        self.transport.sendto(message, addr)

    def _logout(self, addr):
        print("logout", self.clients)
        tank = self.clients[addr]
        del self.engine.entities[tank.id]
        del self.clients[addr]
        self.players = [0 if tank.id == id_ else id_ for id_ in self.players]
        print(self.players)
        tank.free()
        self.transport.sendto(protocol.mono.pack(protocol.DONE), addr)
        print("Client {} removed", addr)
        print(self.clients)

    def run(self):
        self._past_time = self._loop.time()
        self._loop.run_forever()

    @asyncio.coroutine
    def _tick(self, time):
        TIME = 1./Server.TICKRATE
        print("sleep for", TIME)
        while True:
            dt = time() - self._past_time
            #for k in self.clients:
             #   print(self.clients[k].body.x, self.clients[k].body.y)
            for bot in self.bots:
                if bot is None: continue
                bot(None)
            self.engine.update(dt)
            self._past_time = time()
            self._send_seconds(dt)
            for message, entity in self.engine.messages:
                if message == "jump":
                    self._send_action_to_clients(protocol.JUMP, entity.id)
            yield from asyncio.sleep(TIME)
    
    @asyncio.coroutine
    def _send_snapshot(self):
        FRAMERATE = 1./10.
        snapshot_buffer = bytearray()
        clients = self.clients
        bullets = self.engine.bullet_pool._used
        print("FRAMERATE", FRAMERATE)
        while True:
            snapshot_buffer.clear()
            snapshot_buffer += protocol.mono.pack(protocol.SNAPSHOT)
            n_players = len(clients)
            snapshot_buffer += protocol.mono.pack(n_players)
            for client in clients:
                tank = clients[client]
                id_ = tank.id
                x = tank.body.x
                y = tank.body.y
                mov = tank.input.move
                canon = tank.input.cannon_angle
                snapshot_buffer += protocol.tank.pack(id_, x, y, mov, canon)
            for bullet in bullets:
                pass
                #print(bullet)
            for client in clients:
                self.transport.sendto(snapshot_buffer, client)
            yield from asyncio.sleep(FRAMERATE)
    
    def _send_seconds(self, dt):
        self.dt += dt
        if self.dt < 1.0: return
        self.dt = 0.
        self.secs += 1
        #print(self.secs, "dt: ", dt)
        message = "Secs {}".format(self.secs).encode()
        for client in self.clients:
            self.transport.sendto(message, client)

    def __del__(self):
        if self.transport is not None:
            self.transport.close()
        self._loop.close()
