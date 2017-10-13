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
Los jugadores se registrarán en un servidor a través de un cliente de escritorio.
Durante la partida los jugadores manejarán un tanque que disparan balas.
Los jugadores tratarán de echar a los demás jugadores del resto del escenario.

Bibliotecas usadas
------------------

* pyglet: Un framework orientado al desarrollo de juegos.
* twisted: Un framework de red asíncrona.
* toyblock3: Un sistema de entidad-componentes.
* ogf4py3: Un framework basado en toyblock3 y pyglet que asiste en la 
    creación de juegos.
    
Estructura
----------

El proyecto consta del servidor y el cliente.

El servidor es autoritativo. Para los jugadores para poder jugar en ese
servidor deberán registrarse primero para poder acceder a jugar a través de los
clientes.

El cliente es dónde el usuario se conectará a un servidor con su usuario y contraseña
para poder jugar contra otros jugadores registrados.

El proyecto consta además de un módulo propio *polytanks* con sistemas y tipos en común
tanto del servidor como del cliente.

El sistema de entidad-componentes
---------------------------------

Para el desarrollo de juegos es común el uso de la orientación a objetos.
Por ejemplo, partiendo de las clase Entrada, Vida, y Salto, y con la herencia múltiple
te puedes construir la clase Jugador. Lo mismo a partir de Vida y Salto te
puedes construir un EnemigoSalto. Si necesitas un enemigo que no salta entonces
te construyes la clase Enemigo a partir de Vida. ¿Y si necesitas un enemigo
que se puede controlar con Entrada, o un Enemigo invencible sin Vida? Contando
además que deberás de tratar cada uno de los tipos en el sistema de juego.
Aquí ya es donde entra un sistema de entidad-componentes.

Aquí, una entidad es simplemente un contenedor de cada uno de los componentes
que se usa. Un componente es un conjunto de datos de los que va a manejar un sistema.
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
