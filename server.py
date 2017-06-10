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

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from polytanks.engine import Engine, Body

class Server(DatagramProtocol):
    """
    Esta clase sirve como puente o traductor para la clase Engine.
    Enviar y recibe los datos a través de la red a todos los clientes
    a partir de la interfaz de Engine.
    """
    def __init__(self):
        super(Server, self).__init__()
        self._engine = Engine()
    
    def datagramReceived(self, data, addr):
        """Aquí el servidor recibe datos de los clientes y debe transformarlos
        para que lo pueda manejar el motor.
        """
        import polytanks.protocol as protocol
        command = protocol.get_command(data)
        if command == protocol.CONNECT:
            id_, x, y = self._engine.create_tank()
            recreate_tank = protocol.recreate_tank(id_, x, y)
            action = "CONNECT"
            self.transport.write(recreate_tank, addr)
        elif command == protocol.MOVE:
            action = "MOVE"
            command, id_, direction = protocol.get_move_tank(data)
            print(command, id_, direction)
        else:
            action = "NOT DEFINED ACTION"
        print("{} from {}".format(action, addr))

if __name__ == "__main__":
    reactor.listenUDP(7777, Server())
    reactor.run()
