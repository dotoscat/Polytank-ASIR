#!/usr/bin/env  python
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

import pyglet
import polytanks
from polytanks import constant
import polytanks.ogf4py3 as ogf4py3

class Main(ogf4py3.Scene):
    
    COLORS = [
        polytanks.WHITE,
        polytanks.RED,
        polytanks.GREEN,
        polytanks.BLUE
    ]
    
    def __init__(self):
        super().__init__(2)
        self.current_color = 0
        self.title = pyglet.text.Label("POLYTANKS", font_size=24,
        batch=self.batch, group=self.group[0], anchor_x="center",
        anchor_y="center", align="center", x=constant.VWIDTH/2.,
        y=constant.VHEIGHT-constant.VHEIGHT/4.)

        Button = ogf4py3.gui.Button
        
        self.main_buttons = ogf4py3.gui.Node(16, x=constant.VWIDTH/2., y=self.title.y - 64.)
        
        main_buttons = [
            Button("Unirse a partida", batch=self.batch, action=self.unirse_a_partida),
            Button("Crear servidor", batch=self.batch, action=self.crear_servidor),
            Button("Salir", batch=self.batch, action=self.app_exit),
        ]

        for i, button in enumerate(main_buttons):
            self.main_buttons.add_child(button)

        self.children.append(self.main_buttons)
        
        self.edit = ogf4py3.gui.TextEntry(256, 24, batch=self.batch)
        
    def crear_servidor(self, button, x, y, buttons, modifiers):
        print("crear servidor")

    def unirse_a_partida(self, button, x, y, buttons, modifiers):
        print("Unirse a partida")
    
    def app_exit(self, button, x, y, buttons, modifiers):
        pyglet.app.exit()
    
    def change_color(self, dt):
        self.current_color += 1
        self.title.color = Main.COLORS[self.current_color % len(Main.COLORS)]
        
    def init(self):
        pyglet.clock.schedule_interval(self.change_color, 0.25)
        self.director.push_handlers(self.edit.caret)
        
    def update(self, dt):
        pass
    
if __name__ == "__main__":
    director = ogf4py3.Director(
        caption="Polytanks", fullscreen=False,
        width=constant.WIDTH, height=constant.HEIGHT,
        vwidth=constant.VWIDTH, vheight=constant.VHEIGHT)
    director.set_background_color(0., 0., 0.)
    director.scene = Main()
    pyglet.app.run()
    
