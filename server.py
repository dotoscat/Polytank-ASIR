#!/usr/bin/env python

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
import signal
import asyncio
from functools import partial

signal.signal(signal.SIGINT, signal.SIG_DFL)

class ServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, time, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._past_time = time()
        self.dt = 0.
        self.secs = 0
        self.clients = []
    
    def connection_made(self, transport):
        self.transport = transport
        print("Connection", transport)
    
    def connection_lost(self, cls):
        print("lost", cls)
    
    def datagram_received(self, data, addr):
        if data.decode() == "close":
            self.transport.sendto("bye".encode(), addr)
            asyncio.get_event_loop().stop()
            return
        elif data.decode() == "join":
            self.clients.append(addr)
            print("Client {} added".format(addr))
        elif data.decode() == "out":
            self.clients.remove(addr)
            print("Client {} removed", addr)
            print(self.clients)
        #message = "echo from {}: {}".format(str(data, "utf8"), addr).encode()
        #self.transport.sendto(message, addr)

    @asyncio.coroutine
    def tick(self, time):
        while True:
            dt = time() - self._past_time
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
        
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    server = ServerProtocol(loop.time)
    
    listen = loop.create_datagram_endpoint(lambda: server,
        local_addr=("127.0.0.1", 7777))
    #transport, protocol = loop.run_until_complete(listen)
    asyncio.ensure_future(
        asyncio.gather(listen, server.tick(loop.time)))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    
    transport.close()
    loop.close()
