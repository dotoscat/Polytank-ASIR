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

import socket
import pyglet
import polytanks
from polytanks import constant
from polytanks.ogf4py3 import Scene, Director
from polytanks.ogf4py3.gui import Node, VisibleLabel, TextEntry, Button

class Main(Scene):
    
    COLORS = [
        polytanks.WHITE,
        polytanks.RED,
        polytanks.GREEN,
        polytanks.BLUE
    ]
    
    def __init__(self):
        super().__init__(2)
        self.current_color = 0
        self._current_menu = None
        self.title = pyglet.text.Label("POLYTANKS", font_size=24,
        batch=self.batch, group=self.group[0], anchor_x="center",
        anchor_y="center", align="center", x=constant.VWIDTH/2.,
        y=constant.VHEIGHT-constant.VHEIGHT/4.)
        
        common_layout_options = {
            "batch": self.batch
        }
        
        menu_x = self.title.x - self.title.content_width/2.
        menu_y = self.title.y - 64
        
        self.main_menu = Node(x=menu_x , y=menu_y)
        main_menu = self.main_menu
        main_menu.add_child(Button("Unirse a partida", action=self.join_game, **common_layout_options))
        main_menu.add_child(Button("Salir", action=self.app_exit, **common_layout_options))
        self.children.append(main_menu)
        
        self._build_join_game_menu(common_layout_options, menu_x, menu_y)
    
    def _build_join_game_menu(self, common_layout_options, menu_x, menu_y):
        self.join_game_menu = Node(x=menu_x, y=menu_y)
        join_game_menu = self.join_game_menu
        
        ip_horizontal = Node(orientation=Node.HORIZONTAL)
        ip_horizontal.add_child(VisibleLabel("Ip", **common_layout_options))
        self._ip_entry = TextEntry(120, 16, **common_layout_options)
        ip_horizontal.add_child(self._ip_entry)
        join_game_menu.add_child(ip_horizontal)
        
        port_horizontal = Node(orientation=Node.HORIZONTAL)
        port_horizontal.add_child(VisibleLabel("Puerto", **common_layout_options))
        self._port_entry = TextEntry(64, 16, text="7777", **common_layout_options)
        port_horizontal.add_child(self._port_entry)
        join_game_menu.add_child(port_horizontal)
        
        join_game_menu.add_child(Button("Unirse", **common_layout_options, action=self.join_game))
        join_game_menu.add_child(Button("Cancelar", **common_layout_options, action=self.to_main_menu))
        self._join_error_message = VisibleLabel("",
            **dict(color=(255, 128, 128, 255), **common_layout_options))
        join_game_menu.add_child(self._join_error_message)
        join_game_menu.visible = False
        self.children.append(join_game_menu)
    
    def listen(self, data, socket):
        command = protocol.mono.unpack(data)[0]
        if command == protocol.DONE:
            print("El servidor ha terminado")

    def join_game(self, button, x, y, buttons, modifiers):
        hostname = socket.gethostname()
        ip = socket.gethostbyname_ex(hostname)[2].pop()
        self._ip_entry.value = ip
        self.main_menu.visible = False
        self.join_game_menu.visible = True
        self._current_menu = self.join_game_menu
        
    def app_exit(self, button, x, y, buttons, modifiers):
        pyglet.app.exit()
    
    def _to_main_menu(self):
        if self._current_menu is None: return
        self._current_menu.visible = False
        self.main_menu.visible = True
        self._current_menu = None
    
    def to_main_menu(self, button, x, y, buttons, modifiers):
        self._to_main_menu()
    
    def change_color(self, dt):
        self.current_color += 1
        self.title.color = Main.COLORS[self.current_color % len(Main.COLORS)]
        
    def init(self):
        pyglet.clock.schedule_interval(self.change_color, 0.25)
        #self.director.push_handlers(self.edit.caret)
        
    def update(self, dt):
        pass
    
if __name__ == "__main__":
    director = Director(
        caption="Polytanks", fullscreen=False,
        width=constant.WIDTH, height=constant.HEIGHT,
        vwidth=constant.VWIDTH, vheight=constant.VHEIGHT)
    director.set_background_color(0., 0., 0.)
    director.scene = Main()
    pyglet.app.run()
    
