Protocolo
=========

Un protocolo en la informática son reglas para comunicarse o para transmitir
información de un medio a otro.

Tanto el servidor como el cliente hacen uso de un protocolo para poder comunicarse
entre sí y hacer que progrese el transcurso de la partida.

El protocolo en este proyecto consiste en enviar y recibir bytes a través de la red.
Cada mensaje que se envía a través de la red tiene un formato, que consiste
en dar significado a los bytes que se envían por red.

Cada uno de los mensajes que se transmiten tienen como cabecera llamado
*comando* que indica el tipo de mensaje. Esta cabecera tiene un longitud
de 4 bytes. El resto de los bytes, si tiene mas el mensaje, y su significado dependerá
del tipo de comando.

El orden de los bytes a enviar es big endian.

Comandos del cliente
--------------------

* JOIN: Unirse al servidor
* LOGOUT: Desconectarse de un servidor
* CLIENT_INPUT: Estado actual de la entrada
* REQUEST_SNAPSHOT: Pide al cliente que envíe un snapshot completo.
* CLIENT_ACK: Indica el servidor que ha recibido el snapshot enviado por éste.

Comandos del servidor
---------------------

* JOINED: Indica al cliente que se ha unido
* DONE: Indica que se va a desconectar del servidor al cliente.
* SNAPSHOT: Envía snapshot a un cliente.

Orden de los mensajes
---------------------

Por lo general cuando un cliente o un servidor envía un comando este
recibe una respuesta, otro comando, para continuar con el proceso si es necesario
o simplemente acaba.

Login
+++++

    .. graphviz::
    
        digraph login{
            "raw!";
        }
