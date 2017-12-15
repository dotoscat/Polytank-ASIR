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

import socket
import argparse
import signal
import polytanks.server

signal.signal(signal.SIGINT, signal.SIG_DFL)

hostname = socket.gethostname()
default_ip = socket.gethostbyname_ex(hostname)[2].pop()

parse = argparse.ArgumentParser(description="Polytanks server")
parse.add_argument("-p", "--port", default=7777, type=int)
parse.add_argument("-np", "--nplayers", default=1, type=int, choices=range(1, 5))
parse.add_argument("-i", "--ip", default=default_ip)
arguments = parse.parse_args()

port = arguments.port
nplayers = arguments.nplayers
ip = arguments.ip

ADDRESS = (ip, port)

if __name__ == "__main__":
    print("Run polytanks at {}:{} with {} players".format(ip, port, nplayers))
    server = polytanks.server.Server(ADDRESS, debug=True)
    try:
        server.run()
    except KeyboardInterrupt:
        pass
