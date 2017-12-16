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

from itertools import islice
from time import monotonic
from collections import deque, namedtuple
from .snapshot import DUMMY_SNAPSHOT

class _Snapshot:
    def __init__(self, snapshot):
        """
        Saber si el último snapshot ha sido enviado con éxito o no.
        
        Parameters:
            snapshot (:class:`snapshot.Snapshot`)
        """
        self.snapshot = snapshot
        self.ack = False

class Player:

    def __init__(self, tank):
        self.tank = tank
        self.last_time = monotonic()
        self.ping = 0.
        self.input = False #:  Si ya se ha recibido entrada por parte del jugador
        self.snapshots = deque([], 32)

    def insert_snapshot(self, snapshot):
        """Insertar snapshot de :class:`snapshot.Snapshot`."""
        self.snapshots.appendleft(_Snapshot(snapshot))

    def get_diff(self):
        if not self.snapshots: return
        first_snapshot = self.snapshots[0].snapshot
        for snapshot in islice(self.snapshots, 1, None):
            if not snapshot.ack: continue
            self.last_time = monotonic()
            return first_snapshot.diff(snapshot)
        self.last_time = monotonic()
        return first_snapshot.diff(DUMMY_SNAPSHOT)
        
    def ack(self):
        if self.snapshots:
            self.snapshots[0].ack = True
        now = monotonic()
        self.ping = (now - self.last_time)/2.
        self.last_time = now
