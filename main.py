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
        self._current_menu = None
        self.title = pyglet.text.Label("POLYTANKS", font_size=24,
        batch=self.batch, group=self.group[0], anchor_x="center",
        anchor_y="center", align="center", x=constant.VWIDTH/2.,
        y=constant.VHEIGHT-constant.VHEIGHT/4.)

        Button = ogf4py3.gui.Button
        Spinner = ogf4py3.gui.Spinner
        Node = ogf4py3.gui.Node
        VisibleLabel = ogf4py3.gui.VisibleLabel
        
        common_layout_options = {
            "batch": self.batch
        }
        
        menu_x = self.title.x - self.title.content_width/2.
        menu_y = self.title.y - 64
        
        self.main_menu = ogf4py3.gui.Node(x=menu_x , y=menu_y)
        main_menu = self.main_menu
        main_menu.add_child(Button("Unirse a partida", action=self.unirse_a_partida, **common_layout_options))
        self._create_game_button = Button("Crear partida", action=self.configure_game, **common_layout_options)
        main_menu.add_child(self._create_game_button)
        main_menu.add_child(Button("Salir", action=self.app_exit, **common_layout_options))
        self.children.append(main_menu)
        
        created_game_node = Node(x=menu_x, y=menu_y, orientation=Node.HORIZONTAL)
        created_game_node.add_child(Button("X", action=self.close_game, **common_layout_options))
        self._created_game_label = VisibleLabel("Created game blabla", **common_layout_options)
        created_game_node.add_child(self._created_game_label)
        self._created_game_node = created_game_node
        created_game_node.visible = False
        
        hostname = socket.getfqdn()
        ifaces = ["0.0.0.0"] + socket.gethostbyname_ex(hostname)[2]

        self.create_game_menu = Node(x=menu_x, y=menu_y)
        create_game_menu = self.create_game_menu
        ip_horizontal = Node(orientation=Node.HORIZONTAL)
        ip_horizontal.add_child(VisibleLabel("Ip", **common_layout_options))
        self._ip_spinner = Spinner(ifaces, 128, **common_layout_options)
        ip_horizontal.add_child(self._ip_spinner)
        create_game_menu.add_child(ip_horizontal)
        players_horizontal = Node(orientation=Node.HORIZONTAL)
        players_horizontal.add_child(VisibleLabel("Jugadores", **common_layout_options))
        self._players_spinner = Spinner(('1', '2', '3', '4'), 16, **common_layout_options)
        players_horizontal.add_child(self._players_spinner)
        create_game_menu.add_child(players_horizontal)
        port_horizontal = Node(orientation=Node.HORIZONTAL)
        port_horizontal.add_child(VisibleLabel("Puerto", **common_layout_options))
        self._port_entry = ogf4py3.gui.TextEntry(64, 16, text="7777", **common_layout_options)
        port_horizontal.add_child(self._port_entry)
        create_game_menu.add_child(port_horizontal)
        create_game_menu.add_child(Button("Cancelar", **common_layout_options, action=self.to_main_menu))
        create_game_menu.add_child(Button("Listo", **common_layout_options, action=self.create_game))
        self._configure_error_message = VisibleLabel("",
            **dict(color=(255, 128, 128, 255), **common_layout_options))
        create_game_menu.add_child(self._configure_error_message)
        create_game_menu.visible = False
        self.children.append(create_game_menu)
        
    def configure_game(self, button, x, y, buttons, modifiers):
        self._port_entry.value = "7777"
        self._configure_error_message.text = ""
        self.main_menu.visible = False
        self.create_game_menu.visible = True
        self._current_menu = self.create_game_menu

    def create_game(self, button, x, y, buttons, modifiers):
        ip = self._ip_spinner.value
        players = self._players_spinner.value
        try:
            port = int(self._port_entry.value)
            print("Create game", ip, port, players)
            text = "{}:{} {} players".format(ip, port, players)
            self._created_game_label.text = text
            self.main_menu.replace_child(1, self._created_game_node)
            self._to_main_menu()
        except ValueError:
            self._configure_error_message.text = "Puerto debe ser un número"

    def unirse_a_partida(self, button, x, y, buttons, modifiers):
        print("Unirse a partida")
    
    def app_exit(self, button, x, y, buttons, modifiers):
        pyglet.app.exit()
    
    def _to_main_menu(self):
        if self._current_menu is None: return
        self._current_menu.visible = False
        self.main_menu.visible = True
        self._current_menu = None
    
    def close_game(self, button, x, y, buttons, modifiers):
        self._close_game()
    
    def _close_game(self):
        print("Close game")
    
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
    director = ogf4py3.Director(
        caption="Polytanks", fullscreen=False,
        width=constant.WIDTH, height=constant.HEIGHT,
        vwidth=constant.VWIDTH, vheight=constant.VHEIGHT)
    director.set_background_color(0., 0., 0.)
    director.scene = Main()
    pyglet.app.run()
    
