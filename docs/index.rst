.. Polytanks-ASIR documentation master file, created by
   sphinx-quickstart on Thu Oct 12 09:26:16 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentación de Polytanks-ASIR!
================================

.. toctree::
    :maxdepth: 2
    :caption: Contents:

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

Estructura del proyecto
-----------------------

El proyecto consta del servidor y el cliente.

Servidor
++++++++

El servidor es autoritativo. Para poder jugar en un servidor se deberá registrar
primero a través de la web del servidor para poder acceder a jugar a través del
cliente. Hace uso del módulo **asyncio** para atender a las conexiones de red y gestionar
los eventos del juego.

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

Red
---

Modelo cliente/servidor vs p2p (peer to peer)
+++++++++++++++++++++++++++++++++++++++++++++

Protocolo
+++++++++



Referencias
-----------

* `https://7webpages.com/blog/writing-online-multiplayer-game-with-python-asyncio-getting-asynchronous/`

El sistema de entidad-componentes
---------------------------------

Una entidad es simplemente un contenedor de cada uno de los componentes
que se usa para un sistema. Un componente es un conjunto de datos de los que va a manejar un sistema.
Y un sistema maneja como mínimo un componente de una entidad para una tarea específica.
Así puede existir un sistema llamado *salto* que puede funcionar solamente si existe
una entidad con al menos el componente Saltar. Puede existir otro sistemas que maneje
más de un componente como el sistema de físicas, que requiere de un componente Cuerpo
y un componente Colision para calcular la física y respuesta de las entidades que hay
en el juego.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
