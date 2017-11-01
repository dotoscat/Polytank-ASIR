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

import math
from math import degrees
from pprint import pprint
import asyncio
from . import protocol
from . import engine, level

class Server(asyncio.DatagramProtocol):
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
        
        listen = self._loop.create_datagram_endpoint(lambda: self,
            local_addr=address)

        asyncio.ensure_future(listen)
        asyncio.ensure_future(self._tick(self._loop.time))

    def connection_made(self, transport):
        self.transport = transport
        asyncio.ensure_future(self._send_snapshot())
        print("Connection", transport)
    
    def connection_lost(self, cls):
        print("lost", cls)
    
    def datagram_received(self, data, addr):
        data_len = len(data)
        print("payload size", data_len)
        if data_len == protocol.mono.size:
            command = protocol.mono.unpack(data)[0]
            print("command", command)
            if command == protocol.JOIN:
                self._join(addr)
            elif command == protocol.LOGOUT:
                self._logout(addr)
        elif data_len == protocol.di.size:
            command, v1 = protocol.di.unpack(data)
            if command == protocol.MOVE:
                if v1 == 0:
                    print("El jugador {} se para".format(addr))
                else:
                    print("El jugador {} se mueve: {}".format(addr, v1))
            elif command == protocol.AIM:
                print("El jugador {} apunta hacia {}".format(addr, degrees(v1)))
        #message = "echo from {}: {}".format(str(data, "utf8"), addr).encode()
        #self.transport.sendto(message, addr)

    def _join(self, addr):
        tank = self.engine.tank_pool.get()
        self.clients[addr] = tank
        tank.set("body", x=128., y=128.)
        print("Client {} added".format(addr), tank, tank.id, tank.body.x, tank.body.y)
        message = protocol.tetra.pack(protocol.JOINED, tank.id, tank.body.x, tank.body.y)
        self.transport.sendto(message, addr)

    def _logout(self, addr):
        print("logout", self.clients)
        self.clients[addr].free()
        del self.clients[addr]
        self.transport.sendto(protocol.mono.pack(protocol.DONE), addr)
        print("Client {} removed", addr)
        print(self.clients)

    def run(self):
        self._past_time = self._loop.time()
        self._loop.run_forever()

    @asyncio.coroutine
    def _tick(self, time):
        while True:
            dt = time() - self._past_time
            #for k in self.clients:
             #   print(self.clients[k].body.x, self.clients[k].body.y)
            self.engine.update(dt)
            self._past_time = time()
            self._send_seconds(dt)
            yield from asyncio.sleep(0.01)
    
    @asyncio.coroutine
    def _send_snapshot(self):
        FRAMERATE = 1./30.
        snapshot_buffer = bytearray()
        clients = self.clients
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
            #print("send this", len(snapshot_buffer))
            for client in clients:
                self.transport.sendto(snapshot_buffer, client)
            yield from asyncio.sleep(FRAMERATE)
    
    def _send_seconds(self, dt):
        self.dt += dt
        if self.dt < 1.0: return
        self.dt = 0.
        self.secs += 1
        print(self.secs, "dt: ", dt)
        message = "Secs {}".format(self.secs).encode()
        for client in self.clients:
            self.transport.sendto(message, client)

    def __del__(self):
        if self.transport is not None:
            self.transport.close()
        self._loop.close()
