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
import polytanks.server

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    
    server = polytanks.server.Server(loop.time)
    
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
