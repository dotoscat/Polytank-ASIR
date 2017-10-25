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

import asyncio
from . import protocol
from . import engine

class Server(asyncio.DatagramProtocol):
    def __init__(self, address, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = engine.Engine()
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
            
        asyncio.ensure_future(
            asyncio.gather(listen, self._tick(self._loop.time)))
        
    def connection_made(self, transport):
        self.transport = transport
        print("Connection", transport)
    
    def connection_lost(self, cls):
        print("lost", cls)
    
    def datagram_received(self, data, addr):
        data_len = len(data)
        print("payload size", data_len)
        if data_len == 4:
            command = protocol.mono.unpack(data)[0]
            print("command", command)
            if command == protocol.JOIN:
                self._join(addr)
            elif command == protocol.LOGOUT:
                self.clients.remove(addr)
                print("Client {} removed", addr)
                print(self.clients)
        #message = "echo from {}: {}".format(str(data, "utf8"), addr).encode()
        #self.transport.sendto(message, addr)

    def _join(self, addr):
        tank = self.engine.tank_pool.get()
        self.clients[addr] = tank
        tank.set("body", x=128., y=128.)
        print("Client {} added".format(addr), tank, tank.id, tank.body.x, tank.body.y)
        message = protocol.tetra.pack(protocol.JOINED, tank.id, tank.body.x, tank.body.y)
        self.transport.sendto(message, addr)

    def run(self):
        self._past_time = self._loop.time()
        self._loop.run_forever()

    @asyncio.coroutine
    def _tick(self, time):
        while True:
            dt = time() - self._past_time
            self.engine.update(dt)
            self._past_time = time()
            self._send_seconds(dt)
            yield from asyncio.sleep(0.01)
    
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
