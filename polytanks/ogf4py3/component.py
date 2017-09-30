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

from math import fabs

class Body(object):
    """Basic component for physics.
       
    You can enable or disable gravity for this :class:`Body` with the
    attribute *gravity*.
    """
    def __init__(self, gravity=False, max_fall_speed=0.):
        self.x = 0.0
        self.y = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.max_fall_speed = max_fall_speed
        self.gravity = gravity

    def update(self, dt, g_force=0.):
        if self.gravity: self.vel_y += g_force*dt
        if self.vel_y < 0. and fabs(self.vel_y) > self.max_fall_speed > 0.:
            self.vel_y = -self.max_fall_speed
        self.x += self.vel_x*dt
        self.y += self.vel_y*dt

    def apply_force(self, dt, x=0., y=0.):
        self.vel_x += x*dt
        self.vel_y += y*dt

class FloorCollision(object):
    """This collision component is specific for floor collisions.
    
    This component uses two points (x, y), stored as pairs.
    
    Parameters:
        x1 (Float): Pair 1's x.
        y1 (Float): Pair 1's y.
        x2 (Float): Pair 2's x.
        y2 (Float): Pair 2's y.

    Returns:
        An instance of FloorCollision.
        
    Attributes:
        platform (Entity or None): This is the last platform which this entity's component has touched.
        touch_floor (Bool): Tells if *platform* is not None.
    """
    def __init__(self, x1, y1, x2, y2):
        self._xy1 = (x1, y1)
        self._xy2 = (x2, y2)
        self.platform = None

    @property
    def touch_floor(self):
        return self.platform is not None

    def get_points(self, x, y):
        """Get two new points given *x* and *y*."""
        xy1 = self._xy1
        xy2 = self._xy2
        return ((x + xy1[0], y + xy1[1]), (x + xy2[0], y + xy2[1]))

    def reset(self):
        self.platform = None

class Collision(object):
    """Rect collision.
    
    Attributes:
        x (Float)
        y (Float)
        type (Int): Type of collision.
        collides_with (Int): Use this as flag of *type*
    """
    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y + self.height

    def __init__(self, type_=0, collides_with=0, offset=(0, 0)):
        self.x = 0.0
        self.y = 0.0
        self.width = 0.0
        self.height = 0.0
        self.type_ = type_
        self.offset = offset
        self.collides_with = collides_with

    def update(self, x, y):
        self.x = x - self.offset[0]
        self.y = y - self.offset[1]

    def intersects(self, b):
        if b.y >= self.top: return False    # top
        if b.top <= self.y: return False    # bottom
        if b.right <= self.x: return False  # left
        if b.x >= self.right: return False  # right
        return True

    def __contains__(self, pair):
        return self.x <= pair[0] <= self.right and self.y <= pair[1] <= self.top
