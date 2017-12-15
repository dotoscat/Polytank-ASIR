Motor
=====

Un motor ayuda a abstraer al servidor y al cliente de crear y gestionar
las entidades y gestionar los sistemas del juego como las físicas.

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
