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

import socket
import asyncio
import argparse
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bot(asyncio.DatagramProtocol):
    def __init__(self, address, nickname):
        self._address = address
        self._nickname = nickname
        self._loop = asyncio.get_event_loop()
        self._transport = None
        listen = self._loop.create_datagram_endpoint(lambda: self,
            remote_addr=address)

        asyncio.ensure_future(listen)

    def connection_made(self, transport):
        self.transport = transport
        print("bot connection", transport)
    
    def connection_lost(self, cls):
        print("bot lost", cls)
    
    def datagram_received(self, data, addr):
        print(len(data), addr)

    def run(self):
        self._loop.run_forever()
        return 0

    def __del__(self):
        if self._transport is not None:
            self._transport.close()
        self._loop.close()

hostname = socket.gethostname()
ip = socket.gethostbyname_ex(hostname)[2].pop()

parse = argparse.ArgumentParser(description="Polytanks bot")
parse.add_argument("-n", "--nickname", default="Bot", type=str)
parse.add_argument("-p", "--port", default=7777, type=int)
parse.add_argument("-i", "--ip", default=ip)
arguments = parse.parse_args()

if __name__ == "__main__":
    address = (arguments.ip, arguments.port)
    nickname = arguments.nickname
    
    print("Crear un bot \"{}\" que se conectará a {}".format(nickname, address))
    bot = Bot(address, nickname)
    bot.run()

