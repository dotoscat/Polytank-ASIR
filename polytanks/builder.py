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

from itertools import count
from pyglet.sprite import Sprite
from .ogf4py3 import toyblock3
from .ogf4py3.component import Body, Collision, Platform, Timer
from .component import PlayerInput, Tank, Bullet, Explosion, PowerUp
from . import constant
from .constant import G, SIZE

def _id_generator():
    c = count(1)
    def _get_id(*args, **kwargs):
        return next(c)
    return _get_id

get_id = _id_generator()

tank = toyblock3.InstanceBuilder()
tank.add("id", get_id)
tank.add("tank", Tank, (0., 4.))
tank.add("input", PlayerInput)
tank.add("platform", Platform.get_foot, width=SIZE, height=1.,
    offset=(SIZE/-2., SIZE/-2.))
tank.add("collision", Collision, type_=constant.TANK, width=SIZE,
    height=SIZE, offset=(SIZE/-2., SIZE/-2.))
tank.add("body", Body, gravity=True, max_falling_speed=G/2., max_ascending_speed=G/2.)

bullet = toyblock3.InstanceBuilder()
bullet.add("id", get_id)
bullet.add("bullet", Bullet)
bullet.add("body", Body, gravity=True)
bullet.add("collision", Collision, type_=constant.BULLET,
    collides_with=constant.PLATFORM | constant.TANK, offset=(-2., -2.))

platform = toyblock3.InstanceBuilder()
platform.add("body", Body)
platform.add("collision", Collision, type_=constant.PLATFORM)
platform.add("platform", Platform.get_platform)

explosion = toyblock3.InstanceBuilder()
explosion.add("id", get_id)
explosion.add("explosion", Explosion)
explosion.add("body", Body)
explosion.add("collision", Collision,
    type_=constant.EXPLOSION, collides_with=constant.TANK,
    offset=(-4., -4.), width=16., height=16.)
explosion.add("timer", Timer, 0.12)

powerup = toyblock3.InstanceBuilder()
powerup.add("id", get_id)
powerup.add("timer", Timer, 3.)
powerup.add("body", Body)
powerup.add("powerup", PowerUp)
powerup.add("collision", Collision, type_=constant.POWERUP,
    collides_with=constant.TANK, width=SIZE, height=SIZE,
    offset=(SIZE/-2., SIZE/-2.))
