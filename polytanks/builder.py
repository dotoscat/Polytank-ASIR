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

from pyglet.sprite import Sprite
from .ogf4py3 import toyblock3
from .ogf4py3.component import Body, Collision, FloorCollision, Timer
from .component import PlayerInput, Tank, Bullet
from . import constant
from .constant import G, SIZE

tank = toyblock3.InstanceBuilder()
tank.add("id", int)
tank.add("tank", Tank)
tank.add("player_input", PlayerInput)
tank.add("floor_collision", FloorCollision, *(0., 0.), *(constant.SIZE, 0.))
tank.add("collision", Collision, type_=constant.TANK, width=SIZE,
    height=SIZE)
tank.add("body", Body, gravity=True, max_falling_speed=G/2., max_ascending_speed=G/2.)

bullet = toyblock3.InstanceBuilder()
bullet.add("id", int)
bullet.add("bullet", Bullet)
bullet.add("body", Body, gravity=True)
bullet.add("collision", Collision, type_=constant.BULLET,
    collides_with=constant.PLATFORM | constant.TANK, offset=(-2., -2.))

platform = toyblock3.InstanceBuilder()
platform.add("collision", Collision, type_=constant.PLATFORM)

explosion = toyblock3.InstanceBuilder()
explosion.add("id", int)
explosion.add("body", Body)
explosion.add("collision", Collision,
    type_=constant.EXPLOSION, collides_with=constant.EXPLOSION,
    offset=(-4., -4.), width=16., height=16.)
explosion.add("timer", Timer, 0.25)
