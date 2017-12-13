Servidor
========

El servidor es autoritativo. Hace uso del módulo **asyncio** para atender a las conexiones de red y gestionar
los eventos del juego. Estas conexiones de red son asíncronas.

El servidor tiene que correr a una velocidad en concreto, esto es mide en marcos
por segundos (TICKRATE). A mayor marcos por segundos mejor precisión de la simulación a costa
de mayor tiempo de procesamiento. Un buen valor para empezar son de 60 marcos por
segundos (1./60.), que se un buen valor para juegos de acción. Este valor tiene que ser el mismo
que el cliente para mayor consistencia en la simulación por parte del cliente.

Cada ciclo del juego tiene que hacer un *tick*. Un *tick* será un procedimiento
donde se procesará el motor, con sus entidades, y las respuesta, sólo si ha
recibido todas las entradas de los jugadores para ese tick. Una vez procesado
se duerme el servidor 1/TICKRATE para luego procesar el siguiente *tick*.

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
