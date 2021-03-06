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
    def __init__(self, gravity=False, max_falling_speed=0., max_ascending_speed=0.):
        self.x = 0.0
        self.y = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.max_falling_speed = max_falling_speed
        self.max_ascending_speed = max_ascending_speed
        self.gravity = gravity

    def update(self, dt, g_force=0.):
        if self.gravity: self.vel_y += g_force*dt
        if self.vel_y < 0. and fabs(self.vel_y) > self.max_falling_speed > 0.:
            self.vel_y = -self.max_falling_speed
        elif self.vel_y > self.max_ascending_speed > 0.:
            self.vel_y = self.max_ascending_speed
        self.x += self.vel_x*dt
        self.y += self.vel_y*dt

    def apply_force(self, dt, x=0., y=0.):
        self.vel_x += x*dt
        self.vel_y += y*dt

class Collision(object):
    """Rect collision.
    
    Attributes:
        x (Float):
        y (Float):
        type (Int): Type of collision.
        collides_with (Int): Use this as flag of *type*
        width (Float):
        height (Float):
        offset (Tuple(x, y)): offset to respect a point. For instance a Body's position.
    """
    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y + self.height

    def __init__(self, x=0., y=0., type_=0, collides_with=0, width=0., height=0., offset=(0, 0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type_ = type_
        self.offset = offset
        self.collides_with = collides_with

    def update(self, x, y):
        self.x = x + self.offset[0]
        self.y = y + self.offset[1]

    def intersects(self, b):
        if b.y >= self.top: return False    # top
        if b.top <= self.y: return False    # bottom
        if b.right <= self.x: return False  # left
        if b.x >= self.right: return False  # right
        return True

    def __contains__(self, pair):
        return self.x <= pair[0] <= self.right and self.y <= pair[1] <= self.top

class Platform(Collision):
    """This collision component is specific for platform collisions.
    
    Returns:
        An instance of Platform.
        
    Attributes:
        platform (Entity or None): This is the last platform which this entity's component has touched.
        touch_floor (Bool): Tells if *platform* is not None.
    """
    
    FOOT = 1000
    PLATFORM = 1001
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.platform = None
        
    @property
    def touch_floor(self):
        return self.platform is not None
        
    def reset(self):
        self.platform = None
        
    @staticmethod
    def get_foot(*args, **kwargs):
        collision = Platform(*args, **kwargs)
        collision.type_ = Platform.FOOT
        return collision

    @staticmethod
    def get_platform(*args, **kwargs):
        collision = Platform(*args, **kwargs)
        collision.type_ = Platform.PLATFORM
        return collision

class Timer:
    def __init__(self, time):
        self.time = 0.
        self.max_time = time

    @property
    def done(self):
        return self.time >= self.max_time
