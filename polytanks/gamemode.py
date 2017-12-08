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

TIME = 10

class GameModeConf:
    """Esta estructura evita pasar muchos argumentos a :class:`GameMode`.
    
    Ya tiene valores por defecto.
    """
    def __init__(self):
        self.ready_time = 3
        self.running_time = TIME
        self.end_time = 5
        self.on_ready = None
        self.on_running = None
        self.on_end = None
        self.on_tick = None

class GameMode:
    READY = 1
    RUNNING = 2
    END = 3
    
    def __init__(self, conf):
        self._ready_time = conf.ready_time
        self._running_time = conf.running_time
        self._end_time = conf.end_time
        self._seconds = 0.
        self._limit = 0.
        self._state = GameMode.READY
        self._on_ready = conf.on_ready
        self._on_running = conf.on_running
        self._on_end = conf.on_end
        self._on_tick = conf.on_tick
    
    @property
    def state(self):
        return self._state
        
    def get_ready(self):
        self._state = GameMode.READY
        self._limit = self._ready_time
        if callable(self._on_ready):
            self._on_ready(self._limit)
        
    def tick(self, dt):
        self._seconds += dt
        if self._seconds >= self._limit:
            self._seconds = 0.
            if self._state == GameMode.READY:
                self._state = GameMode.RUNNING
                self._limit = self._running_time
                if callable(self._on_running):
                    self._on_running(self._limit)
            elif self._state == GameMode.RUNNING:
                self._state = GameMode.END
                self._limit = self._end_time
                if callable(self._on_end):
                    self._on_end(self._limit)
            elif self._state == GameMode.END:
                self.get_ready()
        if callable(self._on_tick):
            self._on_tick(self._seconds)
