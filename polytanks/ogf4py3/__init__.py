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

from math import cos, sin, atan2
from . import toyblock3

from .director import Director
from .scene import Scene

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
