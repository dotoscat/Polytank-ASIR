=========
POLYTANKS
=========

Polytanks es un Proyecto Integrado para la FP de ASIR de IES Romero Vargas
de Jerez.

Puedes seguir `su blog de desarrollo en docs/devlog.rst <docs/devlog.rst>`_.

Objetivo
========

Crear un juego multijugador en línea gestionado desde una web.
Los jugadores compiten entre sí manejando un tanque.

Paquetes, módulos usados de Python
==================================

- twisted, para conexión de red asíncrona.
- pyglet, para implementar aplicaciones multimedia.
- toyblock, para el sistema de entidad-componentes.

Entidades para el juego
=======================

Estos son los objetos que serán usados en el juego. Para la base de datos
las entidades son distintas.

El juego usará un sistema de entidad-componentes. 

- Base_tanque
- Canyon_tanque
- Plataforma
- Bala
- Powerup

Componentes
-----------

- Cuerpo
- Colision_suelo
- Grafico

Sistemas
--------

**Para hacer**

Instalación
===========

**Para hacer**

Licencia
========

..  image:: https://www.gnu.org/graphics/agplv3-155x51.png
    :alt: AGPL-3.0
