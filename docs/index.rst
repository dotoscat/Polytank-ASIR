.. Polytanks-ASIR documentation master file, created by
   sphinx-quickstart on Thu Oct 12 09:26:16 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentación de Polytanks-ASIR!
================================

.. toctree::
    :maxdepth: 2
    :caption: Contenidos:

    servidor
    cliente
    motor
    protocolo

Objetivo
--------

El objetivo es crear un juego multijugador en línea de hasta 4 jugadores.
Los jugadores se registrarán en un servidor a través de un cliente web de escritorio.
Durante la partida los jugadores manejarán un tanque que dispara balas.
Los jugadores tratarán de echar a los demás jugadores del resto del escenario.

Entorno de desarollo:
---------------------

* Geany 1.31
* Python 3.6.3

Bibliotecas usadas
------------------

* pyglet: Un framework orientado al desarrollo de juegos.
* toyblock3: Un sistema de entidad-componentes.
* ogf4py3: Un framework basado en toyblock3 y pyglet que asiste en la 
    creación de juegos.
    

Herramientas usadas
-------------------

* Graphviz: Crear diagramas programáticamente.
* Sphinx: Para crear la documentación a partir del proyecto.
* sfxr: Para generar sonidos.
* GIMP: Para crear los gráficos del juego.
* git: Un sistema de control de versiones.

Preparación del entorno
-----------------------

Desde *pip*, de Python3, es necesario instalar el paquete pyglet para
el desarrollo del cliente.

Requisitos
----------

Para el desarrollo del proyecto se ha elegido Python por ser un lenguaje
de programación sencillo de aprender y usar, y que personalmente domino más.
Python permite el desarrollo rápido de aplicaciones. No es rápido como un
lenguaje compilado como C++, así que hacer uso de la biblioteca estándard
de Python como *itertools* para mayor rendimiento siempre que sea posible.

*asyncio* es recomendable para el desarrollo de aplicaciones asíncronas
desde la versión 3.4 de Python dejando obsoleto otros módulos orientados
a la programación asíncrona que estaban en la biblioteca estándard de Python.

Para el **cliente** usa *selectors* con el que tienes mayor control sobre los sockets
que asyncio.

Estructura del proyecto
-----------------------

El proyecto consta del servidor y el cliente.

Cliente
+++++++

Hace uso del módulo **selectors**
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

Problemas encontrados durante el desarrollo
-------------------------------------------

El motor se ha tenido que rediseñar porque estaba pensado para juego offline.
Es complicado trabajar con el motor para añadir y quitar sistemas.

No se ha conseguido implementar los potenciadores y la web para registrarse, por
falta de tiempo. Tampoco se ha implementado del todo los bots rebido a restricciones
de tiempo.

Fué complicado tratar de conseguir la conexión asíncrona con pyglet, pero un control
a más bajo nivel lo ha logrado.

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
