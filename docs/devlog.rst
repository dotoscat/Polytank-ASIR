==================================================
devlog de *juego multijugador en línea*: Polytanks
==================================================

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
