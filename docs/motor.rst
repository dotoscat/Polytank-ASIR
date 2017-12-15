Motor
=====

Un motor ayuda a abstraer al servidor y al cliente de crear y gestionar
las entidades y gestionar los sistemas del juego como las físicas.

Este motor tiene un procedimiento que ejecuta todos los sistemas asignados
al motor.

Entidades
---------

Todas las entidades tienen una posición (x, y) y una velocidad (vel_x, vel_y).

Tanque
++++++

Los cliente manejan al menos un tanque con un id asignado por el motor.
Los tanques tienen además un daño, un campo que indica el último jugador
del que ha recibido daño, una lista de tanques noqueados y una lista
de los jugadores que derrotaron al jugador.
Los tanques almacenan en todo momento la entrada del jugador como el estado de la acción de salto y
disparo, la dirección del movimiento del tanque [-1., 0, 1.] y a dónde apunta el cañón en radianes.
El estado de disparo es necesario para poder calcular la potencia.

Bala
++++

Las balas hacen daño a los tanques. Una bala tiene poder. A mayor tiempo
de disparo presionado mayor poder. Hace colisión con los tanques
y los suelos. Cuando chocan produce una explosión.

Explosión
+++++++++

Al explotar la bala transmite su poder a la explosión. A mayor poder, mayor cantidad de daño hecho
al tanque y mayor fuerza ejercida contra el tanque. El tanque coge inercia por unos
momentos pudiendo tomar el control después.

Suelos
++++++

Es una entidad especial porque no es necesaria transmitir información entre el cliente
y el servidor. Tienen un área de colisión estática. En el que colisionan
los tanques y las balas. Tanto el servidor como el cliente deben tener la misma
distribución de suelos para que la simulación sea acorde.

Sistemas
--------

Los sistemas se encargan de procesar las entidades activas en el juego. Tanto
el cliente como el servidor requerirán unos sistemas u otros. En el cliente
los sistemas a procesar son menores que los del servidor puesto que el cliente
se encarga de interpretar siendo lo más fiel posible a lo que pasa en el servidor.

Físicas
+++++++

Un sistemas esencial para juegos de acción basados en físicas. Además procesa
la gravedad.

Colisiones
++++++++++

Este sistema se encarga de procesar las colisiones entre las distintas colisiones
que ocurren en el motor, y si ocurren o no. Es un sistema del servidor.

Gráfico
++++++++

Este es un sistema exclusivo del cliente puesto que se encarga de actualizar
los gráficos del juego según el estado de las entidades.

Límite
++++++

Este sistema se encarga de saber si una entidad está fuera de la zona del juego, dónde
se procesará según la entidad. Es un sistema exclusivo del servidor.

Entrada
+++++++

Se encarga de gestionar las entradas asignadas a los tanques y aplicarla
a la velocidad de los tanques. Por ejemplo, si hay un salto y toca suelo el
tanque aplicar un velocidad sobre la velocidad y del tanque.

Orden de ejecución de los sistemas
----------------------------------

Según si es servidor o cliente el motor ejecutará diferentes sistemas
o tendrá una configuración ligeramente diferente de un sistema.

Servidor
++++++++

    .. graphviz::
    
        digraph servidor {
            label = "servidor";
            "empezar" [shape=box];
            "fin" [shape=box];
            "empezar" -> "entrada" -> "físcas" -> "colisiones" -> "límite" -> "fin";
        }

Cliente
+++++++

    .. graphviz::
    
        digraph servidor {
            label = "cliente";
            "empezar" [shape=box];
            "fin" [shape=box];
            "empezar" -> "entrada" -> "físicas" -> "colisiones (sólo tanque y suelo)" -> "gráficos" -> "fin";
        }
