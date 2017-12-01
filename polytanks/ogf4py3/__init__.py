# ogf4py3
# Copyright (C) 2017  Oscar Triano @cat_dotoscat

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import selectors
import socket
from math import cos, sin, atan2
from . import toyblock3

from .director import Director
from .scene import Scene
from . import gui

def magnitude_to_vector(magnitude, angle):
    """
    Parameters:
        magnitude (number):
        angle (float): In radians.
    
    Returns:
        A :class:`tuple` with x, y
    
    """
    x = magnitude*cos(angle)
    y = magnitude*sin(angle)
    return x, y

def get_angle_from(p1_x, p1_y, p2_x, p2_y):
    """Get the angle from two points. p2 around p1.
    
    Returns:
        The angle, in radians.
    """
    return atan2(p2_y - p1_y, p2_x - p1_x)

class Connection:
    """Async UDP connection to a server.
    
    If you want to receive data from server say first a "hello" to the server.
    
    Parameters:
        address ((host, port)):
        listener (callable): It uses the next signature listener(data, socket).
    
    Returns:
        An instance of this class.
        
    Raises:
        TypeError: If listener is not a callable.
    """
    def __init__(self, address, listener):
        if not callable(listener):
            raise TypeError("listener is not a callable. {} passed".format(type(listener)))
        self._address = address
        self._socket = socket.socket(type=socket.SOCK_DGRAM)
        self._socket.connect(address)
        self._socket.setblocking(False)
        self._selector = selectors.DefaultSelector()
        self._selector.register(self._socket, selectors.EVENT_READ,
            listener)
        self._selector_select = self._selector.select
    
    @property
    def socket(self):
        """Outside of :meth:`tick` you can use the socket to send data."""
        return self._socket
    
    def tick(self):
        """Receive and process network events."""
        events = self._selector_select(0)
        for key, mask in events:
            try:
                socket = key.fileobj
                data = socket.recv(1024)
                key.data(data, socket)
            except ConnectionResetError:
                print("Could not connect to the server: {}".format(self._address))
    
    def __del__(self):
        self._socket.close()
        self._selector.close()
