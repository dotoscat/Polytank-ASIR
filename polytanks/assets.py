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

import os
import pyglet

ASSETS_DIR = "assets"

pyglet.resource.path = [ASSETS_DIR]
pyglet.resource.reindex()

images = {
    entry.name.split('.')[0] : pyglet.resource.image(entry.name)
    for entry in os.scandir(os.path.realpath(ASSETS_DIR))
    if entry.name.endswith(".png")
}

images["tank-cannon"].anchor_x = 0.
images["tank-cannon"].anchor_y = 4.
images["bullet"].anchor_x = 4.
images["bullet"].anchor_y = 4.
images["eyehole"].anchor_x = 8.
images["eyehole"].anchor_y = 8.
images["explosion"].anchor_x = 8.
images["explosion"].anchor_y = 8.
