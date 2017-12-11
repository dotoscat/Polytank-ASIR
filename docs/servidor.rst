Servidor
========

El servidor es autoritativo. Para poder jugar en un servidor se deberá registrar
primero a través de la web del servidor para poder acceder a jugar a través del
cliente. Hace uso del módulo **asyncio** para atender a las conexiones de red y gestionar
los eventos del juego.

Se planeaba el registro a través de una web pero se ha descartado por 
restricciones de tiempo.

El servidor corre a 60 marcos por segundo. 

Requisitos
----------

- Python >= 3.4
- Tarjeta de red

.. automodule:: polytanks.server
.. autoclass:: polytanks.server.Server
