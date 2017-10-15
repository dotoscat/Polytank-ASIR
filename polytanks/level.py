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

from .constant import SIZE

basic = [
    "........................__......",
    "........................._......",
    ".....___............_...........",
    "...__......__............_......",
    "..____________....._______......",
    "................................",
    "................................",
]

def load_level(level, pool):
    x = 0.
    y = 0.
    #  pool.free_all()
    for line in reversed(level):
        x = 0.
        for tile in line:
            print(tile, end='')
            if tile == '_':
                platform = pool.get()
                platform.set("sprite", x=x, y=y)
                collision_attrs = {
                    "x": x,
                    "y": y,
                    "width": SIZE,
                    "height": SIZE/4.
                }
                print(collision_attrs)
                platform.set("body", x=x, y=y)
                platform.set("collision", **collision_attrs)
                platform.set("platform", **collision_attrs)
            x += SIZE
        print()
        y += SIZE
