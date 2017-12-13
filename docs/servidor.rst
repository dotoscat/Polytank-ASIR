Servidor
========

El servidor es autoritativo. Hace uso del módulo **asyncio** para atender a las conexiones de red y gestionar
los eventos del juego. Estas conexiones de red son asíncronas.

El servidor tiene que correr a una velocidad en concreto, esto se mide en marcos
por segundos (TICKRATE). A mayor marcos por segundos mejor precisión de la simulación a costa
de mayor tiempo de procesamiento. Un buen valor para empezar son de 60 marcos por
segundos (1./60.), que es un buen valor para juegos de acción. Este valor tiene que ser el mismo
que el cliente para mayor consistencia en la simulación por parte del cliente.

Cada ciclo del juego tiene que hacer un *tick*. Un *tick* será un procedimiento
donde se procesará el motor, con sus entidades, y las respuesta, sólo si ha
recibido todas las entradas de los jugadores para ese tick. Una vez procesado
se duerme el servidor 1/TICKRATE para luego procesar el siguiente *tick*. Si
no ha recivido todas las entradas de los clientes se hace dormir igualmente.

    .. graphviz::

        digraph tick {
            "EMPEZAR" [shape=box];
            "EMPEZAR" -> "tick modo juego";
            "tick modo juego" -> "entrada clientes";
            "entrada clientes" -> "sleep(1./TICKRATE)" [shape=box,label="No ha recibido todas las entradas de los clientes."];
            "entrada clientes" -> "enviar snapshot" [label="Ha recibido todas las entradas de los clientes."];
            "enviar snapshot" -> "actualizar motor";
            "sleep(1./TICKRATE)" [shape=box];
            "actualizar motor" -> "sleep(1./TICKRATE)";
            "sleep(1./TICKRATE)" -> "EMPEZAR" [label="Esperar entradas de los clientes."];
        }

Atender conexiones de los clientes
----------------------------------

El servidor tiene que recibir datagramas de los cliente, por estar basado en UDP.
Cada datagrama tiene un campo al comienzo de 4 bytes que indica el comando que son enviados desde
un cliente. La información se puede extraer fácilmente con la clase :class:`Struct` del
módulo :obj:`struct`.
    
    .. code-block:: python
    
        # '!' es para indicar que es el formato de los datos es de red, que es *big endian*.
        import struct
        
        comando_struct = struct.Struct("!i")
        
        #y lo trasforma a un valor manejable transformado al formato del sistema.
        comando = comand_struct.unpack_from(data)[0]

    .. graphviz::

        digraph datagrama {
            node [shape=ellipse,fontname=verdana];
            edge [fontname=verdana];
            "data" [shape=record,label="comando|resto bytes"];
            "data" -> "extraer comando";
            "fin" [shape=box];
            "extraer comando" -> "fin" [label="Ningún comando reconocible"];
            "extraer comando" -> {"JOIN", "REQUEST_SNAPSHOT", "LOGOUT", "CLIENT_INPUT", "CLIENT_ACK"};
            {"JOIN", "REQUEST_SNAPSHOT", "LOGOUT", "CLIENT_INPUT", "CLIENT_ACK"} -> "fin";
        }

Según el comando se procesa según el resto de los bytes, si tiene.

Entrada del cliente
-------------------

Cuando el comando es CLIENT_INPUT entoces el resto de los bytes son el estado
de la entrada del cliente. Tiene el siguiente formato:

    .. graphviz::
        
        graph entrada_cliente {
            "entrada cliente" [shape=record,
            label="(CLIENT_INPUT)|tick del servidor|movimiento tanque|ángulo cañón|acumular poder|salto"
            ];
        }

* tick del servidor (entero): El tick actual del servidor
* movimiento tanque (flotante): Indica el movimiento del tanque [-1.| 0.| 1.]
* ángulo del cañón (flotante): Indica la dirección del tanque en radianes.
* acumular poder (booleano): El jugador presiona el botón de acumular poder.
* salto (booleano): Botón de salto presionado o no.

Tick del modo de juego
----------------------

Este paso aparte es para separar el proceso del servidor, tick del servidor, del proceso de juego.
Según el modo de juego se irá alterando el estado del juego y el estado del motor.

    .. graphviz::
    
        digraph modo_juego {
            node [shape=circle,fontname=verdana];
            "READY" -> "RUNNING" [label="a segundos"];
            "RUNNING" -> "END" [label="b segundos"];
            "END" -> "READY" [label="c segundos"];
        }

Enviar snapshot
---------------

Un snapshot, es como una captura o una captura, del estado actual del juego, 
incluyendo el motor y el modo de juego.
Es bastante recomendable almacenar la información relevante para ser procesada
y enviada a los clientes para que estos los interprete.

Para enviar snapshots del servidor a los clientes tiene que ser en un tiempo
no superior a :obj:`TICKRATE`. Lo que se envía en verdad es la diferencia
entre dos snapshots a los clientes, y ya luego los clientes interpreta esas diferencias.
A mayor :obj:`TICKRATE` mayor garantías de corregir la simulación en el cliente
a costa de mayor tiempo de procesamiento. El tiempo que transcurre que se envía entre
cada snapshot queda determinado por :obj:`SNAPSHOT_RATE`. Un valor de :obj:`TICKRATE`/2 para
SNAPSHOT_RATE es buen valor para empezar.
