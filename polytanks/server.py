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

from collections import deque
import time
from time import perf_counter
import math
from math import degrees
import asyncio
from . import engine, level, protocol, gamemode, COLORS
from .snapshot import Snapshot, DUMMY_SNAPSHOT

class Player:
    def __init__(self, tank):
        self.tank = tank
        self.last_time = time.monotonic()
        self.ping = 0.
        self.input = False
        self._ack = True
        
    def send(self):
        self.last_time = time.monotonic()
        self._ack = False
        
    def ack(self):
        self._ack = True
        now = time.monotonic()
        self.ping = (now - self.last_time)/2.
        self.last_time = now

class Server(asyncio.DatagramProtocol):
    """El servidor se basa en el protocolo UDP
    
    Parameters:
        address ((ip, puerto)): Dirección el cual el servidor va a atender.
        nplayers (integer): Número máximo de jugadores soportado.
    """
    TICKRATE = 60   #:  Cuántos ticks por segundos corre el servidor
    SNAPSHOT_RATE = 30  #:  Cuántos snapshots por segundo son enviados a los jugadores
    
    class Repeater:
        """Un repetidor básico que llama una funcion *f* cada *secs* segundos.
        
        La instancia devuelta se puede ejecutar para que sea llamada la función
        si ha pasado el tiempo indicado.
        
        Se creó esta clase porque asyncio sólo repite las tareas una sola vez
        y el control del tiempo entre varias corutinas no es exacto.
        
        Args:
            f (function): La función a llamar.
            secs (float): Los segundos entre cada llamada.
            
        Example:
            .. code-block:: python
            
                    def hola_mundo():
                        print("Hola mundo")
                    
                    repetir_saludo = Repeater(hola_mundo, 1.)  #  Hola mundo cada segundo
                    while True:
                        repetir_saludo()
            
        """
        def __init__(self, f, secs):
            self._f = f
            self.last = perf_counter()
            self.secs = secs
                
        def __call__(self, *args, **kwargs):
            now = perf_counter()
            if now - self.last >= self.secs:
                self.last = now
                self._f(*args, **kwargs)

    def __init__(self, address, *args, nplayers=1, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = engine.Engine()
        level.load_level(level.basic, self.engine.platform_pool)
        self._address = address
        self._loop = asyncio.get_event_loop()
        self._loop.set_debug(debug)
        self.transport = None
        self.tick = 0
        self.clients = {}
        self.NPLAYERS = nplayers
        self.players = [None]*nplayers
        self._send_snapshot = Server.Repeater(self._send_snapshot, 1./Server.SNAPSHOT_RATE)
        self.snapshots = deque([], 32)
        
        game_conf = gamemode.GameModeConf()
        game_conf.on_ready = self.on_ready
        game_conf.on_running = self.on_running
        game_conf.on_end = self.on_end
        game_conf.on_tick = self.on_tick
        self.standard_game = gamemode.GameMode(game_conf)
        self.standard_game.get_ready()
        
        listen = self._loop.create_datagram_endpoint(lambda: self,
            local_addr=address)

        asyncio.ensure_future(listen)
        asyncio.ensure_future(self._tick())
    
    def on_ready(self, time):
        print("on ready", time)
        
    def on_running(self, time):
        print("on running", time)
        
    def on_end(self, time):
        print("on end", time)
    
    def on_tick(self, seconds):
        pass
        #print("seconds", seconds)
    
    def add_player(self, tank):
        for i, player in enumerate(self.players):
            if player is not None: continue
            player = Player(tank)
            self.players[i] = player
            return (i, player)
    
    def connection_made(self, transport):
        self.transport = transport
        print("Connection", transport)
    
    def connection_lost(self, cls):
        print("lost", cls)
    
    def datagram_received(self, data, addr):
        """Aquí se reciben los datos y se procesan según el comando
        identificado mediante el protocolo.
        
        Parameters:
            data (bytes): Datos recibidos desde la red.
            addr ((ip, puerto)): Dirección de donde se ha recibido esos datos.
            
        .. graphviz::
            
            digraph datagram {
                "data" -> {"JOIN", "REQUEST_SNAPSHOT", "LOGOUT", "CLIENT_INPUT", "CLIENT_ACK"};
            }
        """
        command = protocol.mono.unpack_from(data)[0]
        #print("command", command)
        if command == protocol.JOIN:
            self._join(addr, data)
        elif command == protocol.REQUEST_SNAPSHOT:
            snapshot = Snapshot(self.engine, self.standard_game, -1)
            self.snapshots.appendleft(snapshot)
            diff = snapshot.diff(DUMMY_SNAPSHOT)
            data = Snapshot.to_network(diff)
            print("snapshots", len(self.snapshots))
            print("first snapshot", self.snapshots[0])
            print(addr, "requests a snapshot", diff)
            self.transport.sendto(data, addr)
        elif command == protocol.LOGOUT:
            self._logout(addr)
        elif command == protocol.CLIENT_INPUT:
            self.client_input(data, addr)
            #print("client input", addr, len(data))
        elif command == protocol.CLIENT_ACK:
            player = self.clients[addr]
            #player.ack()
            #print("ping de ", addr, player.ping)

    def client_input(self, data, addr):
        player = self.clients.get(addr)
        if player is None: return
        tank = player.tank
        command, tick, *player_input = protocol.input.unpack(data)
        move, cannon_angle, accumulate_power, do_jump = player_input
        tank.input.move = move
        tank.input.cannon_angle = cannon_angle
        #print("accumulate_power", accumulate_power)
        if (not tank.input.shooted and not accumulate_power
            and tank.input.accumulate_power):
            tank.input.shoots = True
        elif tank.input.shooted and not accumulate_power:
            tank.input.shooted = False
        tank.input.accumulate_power = accumulate_power
        tank.input.do_jump = do_jump
        player.input = True
        #print("input", addr, tick, move, cannon_angle, shoots,
        #    jumps)

    def _join(self, addr, data):
        command, nickname = protocol.join.unpack(data)
        nickname = nickname.decode()
        tank = self.engine.create_tank()
        i, player = self.add_player(tank)
        color = COLORS[i][:3]
        self.clients[addr] = player
        tank.set("body", x=128., y=128.)
        tank.set("tank", nickname=nickname, color=color)
        print("Player {} from {} added".format(nickname, addr))
        print(self.players)
        message = protocol.joined.pack(protocol.JOINED, self.NPLAYERS,
            tank.id)
        self.transport.sendto(message, addr)

    def _logout(self, addr):
        print("logout", self.clients)
        player = self.clients[addr]
        player.tank.free()
        del self.engine.entities[player.tank.id]
        del self.clients[addr]
        self.players = [None if player == p else p for p in self.players]
        print(self.players)
        #self.transport.sendto(protocol.mono.pack(protocol.DONE), addr)
        print("Client {} removed", addr)
        print(self.clients)

    def run(self):
        self._past_time = self._loop.time()
        self._loop.run_forever()
        return 0

    @asyncio.coroutine
    def _tick(self):
        """Un tick del juego. Cada marco por segundo es un tick.
        
        Esta es una corutina usada internamente por asyncio.
               
        Yields:
            coroutine: desde asyncio.sleep(1./:obj:`TICKRATE`)
        
        """
        TIME = 1./Server.TICKRATE
        dt = TIME
        standard_tick = self.standard_game.tick
        print("sleep for", TIME)
        while True:
            standard_tick(dt)
            player_input = True
            for player in self.players:
                if player is None: continue
                player_input = player_input and player.input

            if not player_input:
                yield from asyncio.sleep(TIME)
                #print("Esperar entrada")
                continue
            #print("continue with input")
            self._send_snapshot()
            self.engine.update(dt)
            for message in self.engine.messages: pass
            self.tick += 1
            for player in self.players:
                if player is None: continue
                player.input = False
            yield from asyncio.sleep(TIME)
        
    def _send_snapshot(self):
        snapshot = Snapshot(self.engine, self.standard_game, self.tick)
        snapshots = self.snapshots
        snapshots.appendleft(snapshot)
        data = b''
        if len(snapshots) > 1:
            diff = snapshots[0].diff(snapshots[1])
            data = Snapshot.to_network(diff)
        #print("send snapshot", data)
        clients = self.clients
        for client in clients:
            player = clients[client]
            #player.send()
            self.transport.sendto(data, client)

    def __del__(self):
        if self.transport is not None:
            self.transport.close()
        self._loop.close()
