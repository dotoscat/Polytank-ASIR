===============================================================
devlog de **juego multijugador en línea de tanques: Polytanks**
===============================================================

2017-06-11
==========

¡Por fin me dibuja algo el cliente por la pantalla! El servidor da la orden
a quien se conectó y ahí está. Al final el servidor se encarga nada más
que de los datos como las físicas o la posición, mientras que el cliente
se encarga pues de dibujarlo por pantalla. Estoy siguiendo el modelo-vista-
controlador, solamente que este modelo está implementado en el servidor
y el cliente.

2017-06-08
==========

Quiero implementar un motor en común tanto para el cliente como para el
servidor. El caso es que al servidor no le importa los gráficos que tiene
los objetos, mientras que el cliente sí.

Sería como distintas versiones de un objeto. Por ejemplo, el que me estoy
peleando ahora mismo, sería el tanque. Un tanque tiene un cuerpo, con su posición,
su identificador y su gráfico de tanque, en el cliente. El servidor, solamente
el tanque tiene el cuerpo, y nada más. Cada objeto del cuerpo tiene una combinación
única de elementos.

Y estoy tratando de mejorar el protocolo más. Desde el cliente envía la
entrada del jugador (el jugador pulsa la tecla de mover),
mientras que el servidor envía a todos los clientes un evento (el tanque se mueve).

2017-06-05
==========

Cuando conseguí implementar twisted y pyglet al lado del cliente daba
un problema: Al menos uno de los métodos de run de twisted y pyglet no se llegaba
a ejecutar para iterar los eventos; Cuando afectaba a pyglet dejaba la ventana
bloqueada y cuando afectaba a twisted no recibía ni enviaba mensajes. 
Una solución era ejecutar los eventos del otro framework desde una función
que se llamaba temporalmente desde el principal framework.

Haciendo investigación `encontré una solución y era llamar manualmente <https://www.gamedev.net/topic/509570-python--twisted-for-game-networking/>`_
los métodos necesarios para los eventos de red y las funciones que se llamaban periódica
mente desde twisted, desde el reactor principal. Aquí lo haría desde pyglet

::

    def iterate_reactor(dt):
        reactor.runUntilCurrent()
        reactor.doSelect(0)
        
    pyglet.clock.schedule(iterate_reactor)

También mirando un poco la documentación de pyglet encontré que podría hacerlo de la forma
contraria, haciendo una subclase desde la clase *EventLoop* de pyglet y sobrecargar su método *idle*,
para después pasar dicho método al reactor de twisted para ser llamado periódicamente.
Incluso lo podría hacer de las dos formas, pero eso ya es complicarse demasiado. La primera solución
basta, y de hecho me funciona. La segunda solución también funcionaría. Teóricamente
el problema ya está resuelto.

2017-06-04
==========

Comienzo el blog contando todo lo que tengo hecho hasta ahora.

Por el momento lo que tengo hecho un un programa que hará de servidor y
otro de cliente. Quiero que cada clase o método de
dicha clase tenga un propósito y nada más, que no dependa unas de otras.
En lo posible utilizaré la orientación a objetos. Sin embargo para el motor
del juego utilizaré un sistema de entidad-componentes. He creado un paquete llamado
toyblock_, para el sistema de entidad-componentes.

.. _toyblock: https://pypi.python.org/pypi/toyblock

Lo siguiente que estoy haciendo es hacer que el cliente envíe mensajes
al servidor. Para el cliente es prioritario primero iniciar una ventana
y luego hacer que cada evento se envíe al servidor. El servidor dará una
respuesta al cliente.
