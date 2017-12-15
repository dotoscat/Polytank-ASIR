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

El cliente se une al servidor
+++++++++++++++++++++++++++++

    .. graphviz::
    
        digraph login{
            rankdir = LR;
            node [shape=plaintext];
            subgraph cluster0 {
                "JOIN";
                "REQUEST_SNAPSHOT"
                "fin";
                label = "cliente";
            }
            subgraph cluster1 {
                "JOINED";
                "SNAPSHOT"
                label = "servidor";
            }
            "JOIN" -> "JOINED" [label="[n jugadores e id asignado]"];
            "JOINED" -> "REQUEST_SNAPSHOT";
            "REQUEST_SNAPSHOT" -> "SNAPSHOT" [label="[datos del snapshot]"];
            "SNAPSHOT" -> "fin";
        }

Tick del servidor
+++++++++++++++++

    .. graphviz::
    
        digraph tick{
            rankdir = RL;
            node [shape=plaintext];
            subgraph cluster1 {
                "CLIENT_ACK";
                label = "cliente";
            }
            subgraph cluster0 {
                "SNAPSHOT";
                "end";
                label = "servidor";
            }
            "SNAPSHOT" -> "CLIENT_ACK" [label="[datos del snapshot]"];
            "CLIENT_ACK" -> "end";
        }

Logout del cliente
++++++++++++++++++

    .. graphviz::
    
        digraph login{
            rankdir = RL;
            node [shape=plaintext];
            subgraph cluster0 {
                "LOGOUT";
                "end";
                label = "cliente";
            }
            subgraph cluster1 {
                "DONE";
                label = "servidor";
            }
            "LOGOUT" -> "DONE" -> "end";
        }

Formatos de los mensajes
------------------------

Todos los mensajes empiezan por 4 bytes que indica qué comando es. Hay
mensajes que llevan mas información según el comando.

JOIN
++++

    .. graphviz::
    
        graph join_struct {
            "join" [shape=record,label="comando|nick(9 caracteres)"];
        }

JOINED
++++++

    .. graphviz::
    
        graph joined_struct {
            "joined" [shape=record,label="comando|n_jugadores|id"];
        }

* n_jugadores (entero): Número de jugadores actuales del servidor.
* id (entero): Número asignado por el servidor para el cliente.

CLIENT_INPUT
++++++++++++

En cada tick por parte del cliente tiene que enviar un CLIENT_INPUT al
servidor al que está conectado.

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

SNAPSHOT
++++++++

El snapshot lleva un estado del modo de juego con el estado actual,
el tiempo estimado en segundos y el tiempo restante en segundos.

El snapshot tiene 3 listas para TANQUES, BALAS y EXPLOSIONES.

* Objetos creados
* Objetos modificados
* Objetos destruidos
