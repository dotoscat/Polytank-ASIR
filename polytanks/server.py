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
import time
from time import perf_counter
import math
from math import degrees
from pprint import pprint
import asyncio
from . import protocol
from . import engine, level, bot, snapshot

class Player:
    def __init__(self, tank):
        self.tank = tank
        self.last_time = time.monotonic()
        self.ping = 0.
        self._ack = True
        
    def send(self):
        self.last_time = time.monotonic()
        self._ack = False
        
    def ack(self):
        self._ack = True
        now = time.monotonic()
        self.ping = (now - self.last_time)/2.
        self.last_time = now

class Server(asyncio.DatagramProtocol):
    
    TICKRATE = 60
    SNAPSHOT_RATE = 1
    
    class Repeater:
        """Basic repeater. Only calls the function each *secs*."""
        def __init__(self, f, secs):
            self._f = f
            self.last = perf_counter()
            self.secs = secs
                
        def __call__(self, *args, **kwargs):
            now = perf_counter()
            if now - self.last >= self.secs:
                self.last = now
                self._f(*args, **kwargs)

    def __init__(self, address, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = engine.Engine()
        level.load_level(level.basic, self.engine.platform_pool)
        self._address = address
        self._loop = asyncio.get_event_loop()
        self._loop.set_debug(debug)
        self.transport = None
        self.tick = 0
        self.clients = {}
        self.players = [None]*4
        self.snapshot = snapshot.Snapshot(self.engine)
        self._send_snapshot = Server.Repeater(self._send_snapshot, 1.)
        
        listen = self._loop.create_datagram_endpoint(lambda: self,
            local_addr=address)

        asyncio.ensure_future(listen)
        asyncio.ensure_future(self._tick(self._loop.time))
        
        #self.add_bot(bot.jumper)

    def add_bot(self, bot):
        for i, player in enumerate(self.players):
            if player is not None: continue
            tank = self.engine.create_tank()
            tank.set("body", x=200., y=100.)
            self.players[i] = partial(bot, tank)
            return
        raise Exception("Assure enough slots, players, for bots")
    
    def add_player(self, tank):
        for i, player in enumerate(self.players):
            if player is not None: continue
            player = Player(tank)
            self.players[i] = player
            return player
    
    def connection_made(self, transport):
        self.transport = transport
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
            self.client_input(data, addr)
            #print("client input", addr, len(data))
        elif command == protocol.CLIENT_ACK:
            player = self.clients[addr]
            player.ack()
            print("ping de ", addr, player.ping)

    def client_input(self, data, addr):
        player = self.clients.get(addr)
        if player is None: return
        tank = player.tank
        input_buffer = data[protocol.mono.size:]
        fdata_iterator = protocol.struct.iter_unpack("!f", input_buffer)
        idata_iterator = protocol.struct.iter_unpack("!i", input_buffer)
        for idata, fdata in zip(idata_iterator, fdata_iterator):
            tick = idata[0]
            n_input = next(idata_iterator)[0]
            next(fdata_iterator)
            #if n_input:
            #    print("tick", tick)
            for i in range(n_input):
                command = next(idata_iterator)[0]
                next(fdata_iterator)
                if command == protocol.MOVE_LEFT:
                    tank.input.move_left()
                    print("mover izquierda")
                elif command == protocol.MOVE_RIGHT:
                    tank.input.move_right()
                    print("mover derecha")
                elif command == protocol.STOP:
                    tank.input.stop_moving()
                    print("parar")
                elif command == protocol.JUMP:
                    tank.input.jump()
                    print("saltar")
                elif command == protocol.NO_JUMP:
                    tank.input.not_jump()
                    print("no saltar")
                elif command == protocol.SHOOT:
                    tank.input.accumulate_power = True
                    print("disparar")
                elif command == protocol.NO_SHOOT:
                    tank.input.accumulate_power = False
                    print("no disparar")
                elif command == protocol.AIM:
                    value = next(fdata_iterator)[0]
                    next(idata_iterator)
                    tank.input.cannon_angle = value
                    #print("apuntar", -degrees(value))

    def _start_game(self, addr):
        data_size = protocol.mono.size + len(self.players)*protocol.tri.size
        data = bytearray(data_size)
        protocol.mono.pack_into(data, 0, protocol.START_GAME)
        offset = protocol.mono.size
        entities = self.engine.entities
        for i, player in enumerate(self.players):
            if player is None:
                protocol.tri.pack_into(data, offset, 0, 0., 0.)
            else:
                if callable(player):
                    tank = player.args[0]
                else:
                    tank = player.tank
                body = tank.body
                protocol.tri.pack_into(data, offset, tank.id, body.x, body.y)
            offset += protocol.tri.size
        self.transport.sendto(data, addr)

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
        player = self.add_player(tank)
        self.clients[addr] = player
        tank.set("body", x=128., y=128.)
        print("Client {} {} added".format(addr, tank.id))
        print(self.players)
        message = protocol.tetra.pack(protocol.JOINED, tank.id, tank.body.x, tank.body.y)
        self.transport.sendto(message, addr)

    def _logout(self, addr):
        print("logout", self.clients)
        player = self.clients[addr]
        player.tank.free()
        del self.engine.entities[player.tank.id]
        del self.clients[addr]
        self.players = [None if player == p else p for p in self.players]
        print(self.players)
        self.transport.sendto(protocol.mono.pack(protocol.DONE), addr)
        print("Client {} removed", addr)
        print(self.clients)

    def run(self):
        self._past_time = self._loop.time()
        self._loop.run_forever()

    @asyncio.coroutine
    def _tick(self, time):
        TIME = 1./Server.TICKRATE
        dt = TIME
        print("sleep for", TIME)
        while True:
            #print(self.tick)
            self._send_snapshot()
            #print(dt)
            for player in self.players:
                if not callable(player): continue
                bot(None)
            self.engine.update(dt)
            for message, entity in self.engine.messages:
                pass
            self.tick += 1
            yield from asyncio.sleep(TIME)
        
    def _send_snapshot(self):
        self.snapshot += 1
        data = self.snapshot.digest()
        #print("send snapshot", len(data))
        clients = self.clients
        for client in clients:
            player = clients[client]
            if isinstance(player, Player):
                player.send()
            self.transport.sendto(data, client)

    def __del__(self):
        if self.transport is not None:
            self.transport.close()
        self._loop.close()
