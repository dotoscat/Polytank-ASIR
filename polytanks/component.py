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

class PlayerInput:
    def __init__(self):
        self.do_jump = False
        self.move = 0.
        self.aim_pointer = (0., 0.)
        self.cannon_angle = 0.
        self.time_floating = 0.
        self.MAX_TIME_FLOATING = 3.
        self.accumulate_power = False
        self.time_power = 0.
        self.MAX_TIME_POWER = 3.
        self.shoots = False
    
    @property
    def floats(self):
        return self.time_floating < self.MAX_TIME_FLOATING
    
    @property
    def release_power(self):
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
    def __init__(self):
        self.damage = 0
        self.hitstun = 0.
        
    def reset(self):
        self.damage = 0
        self.hitstun = 0.

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

class TankGraphic:
    def __init__(self, base, cannon, cannon_anchor=(0., 0.)):
        self.base = base
        self.cannon = cannon
        self.cannon_anchor = cannon_anchor
        
    def set_position(self, x, y):
        self.base.set_position(x, y)
        self.cannon.set_position(self.cannon_anchor[0] + x, self.cannon_anchor[1] + y)
