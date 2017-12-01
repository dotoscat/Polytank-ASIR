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

from collections import deque
import pyglet

class Bar(object):
    def __init__(self, x, y, width, height, fg, bg, margin=1.):
        """
            x, y, width and height are pixels
            fg: (r, g, b, a) #Foreground
            bg: (r, g, b, a) #Background
            margin: margin for the bar
        """
        self._fg = (pyglet.image.SolidColorImagePattern(fg)
            .create_image(width, height)
        )
        self._bg = (pyglet.image.SolidColorImagePattern(bg)
            .create_image(width, height)
        )
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._margin = margin
        self._value = 0.

    def set_value(self, value, max_value):
        """
            change the bar size, foreground, setting value and max_value.
        """
        self._value = value*(self._width-self._margin*2.)/max_value

    def draw(self):
        margin = self._margin
        self._bg.blit(self._x, self._y)
        self._fg.blit(
            self._x + margin, self._y + margin,
            width=self._value, height=self._height - margin*2.
        )

class Node:
    """Group buttons, labels, text edits, spinners...
    """
    def __init__(self, x=0., y=0.):
        self._children = deque()
        self._x = x
        self._y = y
        self._visible = True
    
    def add_child(self, child):
        child.x += self._x
        child.y += self._y
        self._children.append(child)
    
    @property
    def children(self):
        return self._children
    
    @property
    def visible(self):
        return self._visible
        
    @visible.setter
    def visible(self, value):
        self._visible = value
        for child in self._children:
            child.visible = value
    
class Button(pyglet.text.Label):
    def __init__(self, *args, hover_color=(255, 200, 200, 255),
    idle_color=(255, 255, 255, 255), action=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.__width = self.content_width
        self.__height = self.content_height
        self.action = action
        self.hover_color = hover_color
        self.idle_color = idle_color
        self._visible = True
    
    @property
    def visible(self):
        return self._visible
    
    @visible.setter
    def visible(self, visible):
        if not isinstance(visible, bool):
            raise TypeError("visible uses a bool. Got {} instead".format(type(visible)))
        self._visible = visible
        self.color = self.color[0:3] + (255,) if visible else self.color[0:3] + (0,)
    
    def on_mouse_motion(self, x, y, dx, dy):
        if not self._visible: return
        if (self.x < x < self.x + self.__width
        and self.y < y < self.y + self.__height):
            self.color = self.hover_color
        elif self.color is not self.idle_color:
            self.color = self.idle_color
    
    def on_mouse_release(self, x, y, button, modifiers):
        if not self._visible: return
        if not callable(self.action): return
        if (self.x < x < self.x + self.__width
        and self.y < y < self.y + self.__height):
            self.action(self, x, y, button, modifiers)

class Menu(object):

    class Entry(object):
        def __init__(self, label, action, x, y):
            self._x = x
            self._y = y
            self.label = label
            self._action = action

        def __call__(self, menu):
            self._action(menu)

    def __init__(self, cursor_sprite, x=0., y=0.):
        cursor_sprite.x = x
        self._x = x
        self._y = y
        self._cursor = None
        self._cursor_sprite = cursor_sprite
        self._entry = []

    def add_entry(self, label, action, x, y):
        label.x = self._x + x
        label.y = self._y + y
        entry = Menu.Entry(label, action, x, y)
        self._entry.append(entry)
        if self._cursor is None and self._entry:
            self._cursor = 0
            self._cursor_sprite.y = self._entry[0].label.y

    def set_entry(self, position):
        if self._cursor is None or not 0 <= position < len(self._entry):
            return False
        self._cursor = position
        self._cursor_sprite.y = self._entry[self._cursor].label.y
        return True

    def move_up(self):
        if self._cursor is not None and self._cursor - 1 >= 0:
            self._cursor -= 1
            self._cursor_sprite.y = self._entry[self._cursor].label.y
            return True
        return False

    def move_down(self):
        if self._cursor is not None and self._cursor + 1 < len(self._entry):
            self._cursor += 1
            self._cursor_sprite.y = self._entry[self._cursor].label.y
            return True
        return False

    def execute(self):
        if self._cursor is None: return
        self._entry[self._cursor](self)

class NumberLabel(pyglet.text.Label):
    def __init__(self, suffix, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0
        self.suffix = suffix

    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        self._value = value
        self.text = "{} {}".format(self._value, self.suffix)

class FractionLabel(pyglet.text.Label):
    def __init__(self, width, filler, *args, **kwargs):
        super(FractionLabel, self).__init__(*args, **kwargs)
        self._num = 0
        self._dem = 0
        self._width = width
        self._filler = filler

    def set(self, num, dem):
        self._num = num
        self._dem = dem
        self.update()

    def set_num(self, num):
        self._num = num
        self.update()

    def set_dem(self, dem):
        self._dem = dem
        self.update()

    def update(self):
        self.text = ("{:{filler}>{width}}/{:{filler}>{width}}"
            .format(self._num, self._dem, filler=self._filler, width=self._width))
