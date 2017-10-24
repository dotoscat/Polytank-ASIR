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

class PlayerManager:
    def __init__(self):
        self.voices = {}
        
    def add(self, name, source, repeat=False):
        if repeat:
            voice = pyglet.media.Player()
            voice.queue(source)
            self.voices[name] = (voice, source)
        else:
            self.voices[name] = source
        
    def play(self, name):
        voice = self.voices[name]
        if isinstance(voice, tuple):
            if not voice[0].playing:
                voice[0].queue(voice[1])
                voice[0].play()
                return voice[0]
        else:
            return voice.play()

    def __contains__(self, name):
        return name in self.voices

ASSETS_DIR = "assets"

pyglet.resource.path = [ASSETS_DIR]
pyglet.resource.reindex()

images = {
    entry.name.split('.')[0] : pyglet.resource.image(entry.name)
    for entry in os.scandir(os.path.realpath(ASSETS_DIR))
    if entry.name.endswith(".png")
}

sounds = {
    entry.name.split('.')[0] : pyglet.resource.media(entry.name, streaming=False)
    for entry in os.scandir(os.path.realpath(ASSETS_DIR))
    if entry.name.endswith(".wav")
}

images["tank-base"].anchor_x = 8.
images["tank-base"].anchor_y = 8.
images["tank-cannon"].anchor_x = 0.
images["tank-cannon"].anchor_y = 4.
images["bullet"].anchor_x = 4.
images["bullet"].anchor_y = 4.
images["eyehole"].anchor_x = 8.
images["eyehole"].anchor_y = 8.
images["explosion"].anchor_x = 8.
images["explosion"].anchor_y = 8.
images["heal"].anchor_x = 8.
images["heal"].anchor_y = 8.
images["power"].anchor_x = 8.
images["power"].anchor_y = 8.

player = PlayerManager()
player.add("explosion", sounds["explosion"])
player.add("float", sounds["float"], repeat=True)
player.add("touch-floor", sounds["hit-platform"])
player.add("jump", sounds["jump"])
player.add("powerup", sounds["powerup"])
player.add("shoot", sounds["shoot"])
