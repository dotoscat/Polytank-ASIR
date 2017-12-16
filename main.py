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

import re
import socket
import pyglet
import argparse
import polytanks
from polytanks import constant, protocol
from polytanks.client import Client
from polytanks.ogf4py3 import Scene, Director, Connection
from polytanks.ogf4py3.gui import Node, VisibleLabel, TextEntry, Button

class Main(Scene):
    
    COLORS = [
        polytanks.WHITE,
        polytanks.RED,
        polytanks.GREEN,
        polytanks.BLUE,
        polytanks.YELLOW
    ]
    
    def __init__(self):
        super().__init__(2)
        self.current_color = 0
        self._current_menu = None
        self._connection = None
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
        
        nickname_horizontal = Node(orientation=Node.HORIZONTAL)
        nickname_horizontal.add_child(VisibleLabel("Nick", **common_layout_options))
        self._nick_entry = TextEntry(120, 16, text="Participante", **common_layout_options)
        nickname_horizontal.add_child(self._nick_entry)
        join_game_menu.add_child(nickname_horizontal)
        
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
        
        join_game_menu.add_child(Button("Unirse", **common_layout_options, action=self._join_game))
        join_game_menu.add_child(Button("Cancelar", **common_layout_options, action=self.to_main_menu))
        self._join_error_message = VisibleLabel("",
            **dict(color=(255, 0, 0, 255), **common_layout_options))
        join_game_menu.add_child(self._join_error_message)
        join_game_menu.visible = False
        self.children.append(join_game_menu)
        
    def listen(self, data, socket):
        command = protocol.mono.unpack_from(data)[0]
        if command == protocol.JOINED:
            command, nplayers, id_= protocol.joined.unpack(data)
            print("joined", nplayers, id_)
            client = Director.get_scene("client")
            client.set_connection(self._connection)
            client.joined(nplayers, id_)
            Director.set_scene("client")
            self._connection.send(protocol.mono.pack(protocol.REQUEST_SNAPSHOT))

    def join_game(self, button, x, y, buttons, modifiers):
        hostname = socket.gethostname()
        ip = socket.gethostbyname_ex(hostname)[2].pop()
        self._join_error_message.text = ""
        self._ip_entry.value = ip
        self.main_menu.visible = False
        self.join_game_menu.visible = True
        self._current_menu = self.join_game_menu
       
    def _join_game(self, button, x, y, buttons, modifiers):
        nickname = self._nick_entry.value
        ip = self._ip_entry.value
        if re.fullmatch("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip) is None:
            self._join_error_message.text = "Dirección IP malformada."
            return
        try:
            port = int(self._port_entry.value)
        except ValueError:
            self._join_error_message.text = "Puerto tiene que ser un número entero."
            return
        print(ip, port, self._connection)
        if not self._connection is None:
            print("close previus connection")
            self._connection.close()
        self._connection = Connection((ip, port), self.listen)
        sent = self._connection.send(protocol.join.pack(protocol.JOIN, nickname.encode()))
        print("Join game!", ip, port, nickname)
    
    def app_exit(self, button, x, y, buttons, modifiers):
        pyglet.app.exit()
    
    def _to_main_menu(self):
        if self._current_menu is None: return
        self._current_menu.visible = False
        self.main_menu.visible = True
        self._current_menu = None
        if not self._connection is None:
            self._connection.close()
            self._connection = None
    
    def to_main_menu(self, button, x, y, buttons, modifiers):
        self._to_main_menu()
    
    def change_color(self, dt):
        self.current_color += 1
        self.title.color = Main.COLORS[self.current_color % len(Main.COLORS)]
        
    def init(self):
        self._connection = None
        self._to_main_menu()
        pyglet.clock.schedule_interval(self.change_color, 0.25)
    
    def quit(self):
        pyglet.clock.unschedule(self.change_color)
    
    def update(self, dt):
        if not self._connection is None:
            try:
                self._connection.tick()
            except ConnectionResetError:
                self._join_error_message.text = "La partida no existe."
                
if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="Polytanks client")
    parse.add_argument("-s", "--scale", default=2, help="Escala de la pantalla", type=int, choices=range(1, 3))
    
    arguments = parse.parse_args()
    
    scale = arguments.scale
    
    director = Director(
        caption="Polytanks", fullscreen=False,
        width=constant.VWIDTH*scale, height=constant.VHEIGHT*scale,
        vwidth=constant.VWIDTH, vheight=constant.VHEIGHT,
        exit_with_ESC=False)
    director.set_background_color(0., 0., 0.)
    director.add_scene("main", Main())
    director.add_scene("client", Client())
    director.set_scene("main")
    pyglet.app.run()
    
