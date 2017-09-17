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

import pyglet

class Scene(object):
    """Use scenes to organize what is going to happen on screen.
    
    An scene has at least a batch and *n* ordered groups used as layers.
        
    Parameters:
        n_groups (int): Number of groups (layers) for this scene.
        
    Returns:
        An instance of Scene.
    """

    def __init__(self, n_groups):
        self._batch = pyglet.graphics.Batch()
        self._groups = [pyglet.graphics.OrderedGroup(i) for i in range(n_groups)]

    @property
    def batch(self):
        """Access to the scene batch."""
        return self._batch

    @property
    def group(self):
        """Access to the ordered groups of this scene.
        
        Returns:
            A list of ordered groups.
        """
        return self._groups

    def draw(self):
        """Called by :class:`Director` to draw the graphics added to this scene.
        """
        self._batch.draw()

    def init(self):
        """This is called when this scene is set to the director.
        
        Does nothing, so you can override this to do something useful.
        """
        pass

    def quit(self):
        """This is called when this scene is about to set another scene and *before* that scene.
        
        Does nothing, so you can override this to do something useful.
        """
        pass

    def update(self, dt):
        """The scene's heart. This is called periodically.
        
        Does nothing, so you can override this to do something useful.
        
        Parameters:
            dt (float): Time elapsed from the last call to update.
        """
        pass
