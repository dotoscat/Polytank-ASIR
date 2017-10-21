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

signal.signal(signal.SIGINT, signal.SIG_DFL)

class ServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def connection_made(self, transport):
        self.transport = transport
        print("Connection", transport)
        
    def datagram_received(self, data, addr):
        if data.decode() == "close":
            self.transport.sendto("bye".encode(), addr)
            asyncio.get_event_loop().stop()
            return
        message = "echo from {}: {}".format(str(data, "utf8"), addr).encode()
        self.transport.sendto(message, addr)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    listen = loop.create_datagram_endpoint(ServerProtocol,
        local_addr=("127.0.0.1", 7777))
    transport, protocol = loop.run_until_complete(listen)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    
    transport.close()
    loop.close()
