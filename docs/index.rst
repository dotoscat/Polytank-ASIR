.. Polytanks-ASIR documentation master file, created by
   sphinx-quickstart on Thu Oct 12 09:26:16 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentación de Polytanks-ASIR!
================================

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    servidor


Objetivo
--------

El objetivo es crear un juego multijugador en línea de hasta 4 jugadores.
Los jugadores se registrarán en un servidor a través de un cliente web de escritorio.
Durante la partida los jugadores manejarán un tanque que dispara balas.
Los jugadores tratarán de echar a los demás jugadores del resto del escenario.

Bibliotecas usadas
------------------

* pyglet: Un framework orientado al desarrollo de juegos.
* toyblock3: Un sistema de entidad-componentes.
* ogf4py3: Un framework basado en toyblock3 y pyglet que asiste en la 
    creación de juegos.
    
Herramientas usadas
-------------------

* Sphinx: Para crear la documentación a partir del proyecto.
* sfxr: Para generar sonidos.
* GIMP: Para crear los gráficos del juego.
* git: Un sistema de control de versiones.

Requisitos
----------

Cliente
+++++++

- Python >= 3.4
- Tarjeta de red
- Tarjeta gráfica con soporte OpenGL

Estructura del proyecto
-----------------------

El proyecto consta del servidor y el cliente.

Cliente
+++++++

El cliente es dónde el usuario se conectará a un servidor con su usuario y contraseña
para poder jugar contra otros jugadores registrados. Hace uso del módulo **selectors**
por tener un mayor control sobre los sockets que **asyncio** y con posibilidad
de integrarse mejor con el bucle de eventos de **pyglet**.

*polytanks*
+++++++++++

Módulo del proyecto con sistemas, tipos en común y utilidades 
tanto del servidor como del cliente.

*resources*
+++++++++++

Carpeta dónde están los archivos del juego para ser editados.

*assets*
++++++++

Carpeta donde están los archivos que son usados por el juego, generados
a partir de los archivos de la carpeta *resources*.

Jugabilidad
-----------

Cada jugador mueve su tanque con las teclas WASD, o con las teclas de dirección
y apunta el cañón moviendo el ratón. Para disparar mantiene y suelta cualquier
botón del ratón. Más tiempo presionado mayor fuerza de ataque.

Un jugador podrá saltar una vez. En cualquier momento y mientras no toque el suelo
el jugador podrá flotar por el aire durante unos segundos manteniendo pulsado
el botón de salto (W o tecla de dirección ARRIBA). El jugador al ascender mientras flota mantiene la
inercia, cosa que no mantiene mientras desciende y el jugador flota.

Cada tanque del jugador tiene un medidor de daño. A más porcentaje, más posibilidades
de salir fuera del escenario con las explosiones de las balas.
El daño se aumenta recibiendo daño de las explosiones a partir de los
disparos de otros jugadores. También las explosiones es la manera de causar
que otros jugadores salgan volando.

En condiciones normales los tanques tienen una velocidad máxima de ascenso y movimiento
pero si reciben una explosión los jugadores pierden el control del tanque por unos momentos
y no tienen velocidad máxima de ascenso. Pasado ese tiempo los tanques tienen inercia pero
los jugadores pueden tener de nuevo el control del tanque. El control del tanque se recupera
antes si toca el suelo también.

Bots
++++

Los bots se han añadido principalmente por motivos de pruebas pero pueden
servir perfectamente como jugadores del servidor.

Un bot recive una entrada, un mapa del mundo y su entidad asociada.
Su salida es el input de su entidad asociada. Los bots es cualquier *callable*
(puede ser una clase que implemente __call__)

    .. code-block:: python
        
        #  Un bot que salta nada más tocar suelo.
        def jumper(entity, world):
            if entity.platform.touch_floor:
                entity.input.jump()

Red
---

Se ha elegido el protocolo UDP para el intercambio de mensajes entre cliente y servidor.
UDP permite construir fácilmente un protocolo de red según lo que se necesite
y no ser lento como TCP, la velocidad es importante en los juegos.
La fiabilidad de la conexión se tiene que implementar, cosa que TCP ya tiene
incorportado.

Tanto el cliente como el servidor corren a 60 FPS. El cliente envía en cada ciclo
una copia de la entrada, CLIENT_INPUT, al servidor.

Modelo cliente/servidor vs p2p (peer to peer)
+++++++++++++++++++++++++++++++++++++++++++++

El juego usa el modelo de cliente/servidor.

Ventajas
~~~~~~~~

* Sencillo de desarrollar.
* Sencillo de escalar.
* Es complicado hacer trampas (el servidor es autoritativo).

Inconvenientes
~~~~~~~~~~~~~~

* Más complicado de ponerlo en marcha para el público.

Protocolo
+++++++++

Mensajes desde el cliente
~~~~~~~~~~~~~~~~~~~~~~~~~

============    =====================================================   ===========
Comando         Parámetros                                              Descripción
============    =====================================================   ===========
JOIN                                                                    Unirse al servidor
LOGOUT                                                                  Desconectarse de un servidor
CLIENT_INPUT    [tick, move, cannon_angle, accumulate_power, do_jump]   Estado actual de la entrada
ACK                                                                     Ha recibido el snapshot
JOINED                                                                  El cliente se ha unido
============    =====================================================   ===========

Mensajes desde el servidor
~~~~~~~~~~~~~~~~~~~~~~~~~~

==========  =================== ===========
Comando     Parámetros          Descripción
==========  =================== ===========
JOINED      [id, x, y]          Id y posición del jugador al unirse
DONE                            El cliente se ha desconectado
SHOOTED     [id]                Quién dispara
SNAPSHOT    [...]               Estado actual del juego
START_GAME  [[[id, x, y], ...]] Empieza el juego con los jugadores y su posición actual
==========  =================== ===========

Orden del intercambio de mensajes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-------------------+-------------------+------------------------------+----------------------------------------------------+
|Cliente -> Servidor|Servidor -> Cliente|Servidor -> Todos los clientes| Comentarios                                        |
+===================+===================+==============================+====================================================+
|JOIN               |-                  |-                             | Petición del unirse al servidor                    |
+-------------------+-------------------+------------------------------+----------------------------------------------------+
|-                  |JOINED             |-                             | Aceptado, empezar juego                            |
+-------------------+-------------------+------------------------------+----------------------------------------------------+
|JOINED             |                   |                              | Reconocimiento de haberse unido (ACK)              |
+-------------------+-------------------+------------------------------+----------------------------------------------------+
|                   |START_GAME         |                              | Empieza el juego indicando los jugadores           |
+-------------------+-------------------+------------------------------+----------------------------------------------------+
|CLIENT_INPUT       |                   |                              | Envía las entradas acumuladas desde el cliente     |
+-------------------+-------------------+------------------------------+----------------------------------------------------+
|ACK                |                   |                              | Notificar que ha recibido el snapshot              |
+-------------------+-------------------+------------------------------+----------------------------------------------------+
|                   |                   |SNAPSHOT                      | Estado del juego a todos los clientes              |
+-------------------+-------------------+------------------------------+----------------------------------------------------+
|LOGOUT             |-                  |-                             | Petición de desconectarse del servidor             |
+-------------------+-------------------+------------------------------+----------------------------------------------------+
|-                  |DONE               |                              | Aceptada la petición del cliente de desconectarse  |
+-------------------+-------------------+------------------------------+----------------------------------------------------+

Referencias
-----------

* `https://7webpages.com/blog/writing-online-multiplayer-game-with-python-asyncio-getting-asynchronous/`
* `https://gamedev.stackexchange.com/questions/67738/limitations-of-p2p-multiplayer-games-vs-client-server`
* `https://en.wikipedia.org/wiki/Handshaking`
* `https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking`
* `https://gamedev.stackexchange.com/questions/120033/resolving-prediction-error-from-client-side-prediction-and-server-reconciliation`
* `http://fabiensanglard.net/quake3/network.php`
* `https://gamedev.stackexchange.com/questions/22815/how-can-i-alleviate-network-lag-issues-with-players-from-other-countries`
* `https://www.gamedev.net/forums/topic/375992-lag-over-the-internet/`
* `https://www.youtube.com/watch?v=qv6UVOQ0F44`
* `https://en.wikipedia.org/wiki/Entity%E2%80%93component%E2%80%93system`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
