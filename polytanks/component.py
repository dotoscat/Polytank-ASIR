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

from collections import deque

class PlayerInput:
    def __init__(self):
        """
            Setting :attr:'client' to True avoid some processing
            in the input system.
        """
        self.do_jump = False
        self.move = 0.
        self.aim_pointer = (0., 0.)
        self.cannon_angle = 0.
        self.time_floating = 0.
        self.MAX_TIME_FLOATING = 3.
        self.accumulate_power = False
        self.time_power = 0.
        self.MAX_TIME_POWER = 2.
        self.shoots = False
        self.shooted = False
        self.client = False
    
    @property
    def floats(self):
        return self.time_floating < self.MAX_TIME_FLOATING
    
    @property
    def release_power(self):
        if self.client: return
        return self.time_power > self.MAX_TIME_POWER
    
    def reset_time_floating(self):
        self.time_floating = 0.
    
    def move_left(self):
        self.move = -1.
        
    def move_right(self):
        self.move = 1.
        
    def moves(self):
        return self.move != 0.
        
    def stop_moving(self):
        self.move = 0.
    
    def jump(self):
        self.do_jump = True
    
    def not_jump(self):
        self.do_jump = False

class Tank:
    def __init__(self, cannon_anchor):
        self.damage = 0
        self.hitstun = 0.
        self.control = True
        self.cannon_x = 0.
        self.cannon_y = 0.
        self.cannon_anchor = cannon_anchor
        self._ko = deque()
        self._fall = deque()
        self.hit_by = None
        
    def fall(self):
        self._fall.append(self.hit_by)
        self.hit_by = None
        self.damage = 0
    
    @property
    def suicides():
        return self._fall.count(None)
    
    def reset(self):
        self.damage = 0
        self.hitstun = 0.
        self.control = True

    def update(self, x, y):
        self.cannon_x = self.cannon_anchor[0] + x
        self.cannon_y = self.cannon_anchor[1] + y
        
class Bullet:
    """
    Attributes:
        owner (Entity):
    """
    def __init__(self):
        self.owner = None
        self.power = 0.

class Explosion:
    def __init__(self):
        self.damage = 0
        self.knockback = 0
        self.owner = None

class PowerUp:
    def __init__(self):
        self.action = None
        
    def __call__(self, *args, **kwargs):
        self.action(*args, **kwargs)
