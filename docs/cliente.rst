Cliente
=======

El cliente usa :obj:`pyglet` para procesar entradas y procesar los gráficos. Pyglet
tiene un sistemas de eventos propio como :obj:`asyncio`. Usar asyncio con pyglet
hace bastante complicado su uso. Así que para poder usar la conexión asíncrona
cómodamente se usa el módulo :obj:`selectors`. :obj:`selector` es mas bajo nivel
que :obj:`asyncio` pero se integra muy bien con el sistema de evento de :obj:`pyglet`
ya que no tiene control del flujo o del tiempo.

El cliente debe correr a la misma velocidad que el servidor a :obj:`TICKRATE`, que
por lo general es de 60 marcos por segundo.

El cliente también tiene un tick.

Interfaces
----------

Interfaz de usuario
+++++++++++++++++++

Permite al usuario conectarse cómodamente a un servidor y notificar si ha habido
fallos de conexión con el servidor.

.. image:: interfaz.png

Pantalla de juego
+++++++++++++++++

.. image:: juego.png

En la pantalla de juego muestra dónde transcurre el juego, el estado actual
del servidor. Tiene contadores de daños de cada uno de los tanques que se
actualizarán si reciben daño los tanques correspondientes, el nick se asocia
al contador. También se muestra el estado del modo de juego del servidor, como el tiempo
restante.

Pasos del tick
--------------

    .. graphviz::

        digraph tick {
            "EMPEZAR" [shape=box];
            "EMPEZAR" -> "recibir entradas";
            "recibir entradas" -> "enviar entradas";
            "enviar entradas" -> "recibir conexiones";
            "recibir conexiones" -> "actualizar motor";
            "actualizar motor" -> "actualizar gráficos";
            "actualizar gráficos" -> "interpretar mensajes";
            "interpretar mensajes" -> "FIN";
            "FIN" [shape=box];
        }

Recibir mensajes del servidor
-----------------------------

Los únicos mensajes que reciben el cliente del servidor son los SNAPSHOT periódicamente
una vez conectado con JOIN. También si el snapshot es pedido explícitamente
con REQUEST_SNAPSHOT después de haber recibido JOINED del servidor.

Corrección a partir del snapshot
--------------------------------

El cliente debe corregir el estado del juego a partir del snapshot recibido del servidor.
Estos snapshots se almacenan en una cola, hasta 32. En la corrección hay que asegurarse
no aplicar la entrada del tanque del servidor a la entrada del tanqued del cliente.

Enviar entradas
---------------

El cliente siempre envía las entradas, del estado del tanque, al servidor.

Interpretar mensajes
--------------------

Durante el transcurso del juego la cola de mensajes del motor se va llenando
y tiene que ser consumida por cliente. Esto permite la reproducción de sonidos sin
romper con el diseño modular del motor.

