# spec · cli

> El contrato del comando `tuku`: qué garantiza, cómo informa y con qué códigos sale. Es independiente de quién invoque, persona o agente. Lo que cambia cuando el invocador es un agente está en [agente.md](agente.md).

## Qué es dueño el comando

`tuku` es la capa determinista del sistema. Es dueño de la **forma**: dónde va cada cosa, con qué estructura, en qué orden, y qué invariantes no se pueden romper. No es dueño del **juicio**: qué se registra, con qué palabras, bajo qué clasificación y a qué ámbito pertenece.

El corte no pasa entre estructura y lenguaje, pasa por los **campos**. Quien invoca llena los campos; `tuku` construye la línea canónica de [bitacora.md](bitacora.md), la sitúa en el día que corresponde y mantiene el orden cronológico. Llenar los campos es exactamente el trabajo de inferencia: de qué ámbito es, qué clasificación le cabe, si un dictado da uno o varios registros.

Ese reparto sostiene el principio 1 de [`../docs/principios.md`](../docs/principios.md). Un autor disciplinado hace lo mismo a mano con un editor básico: el comando le ahorra el esfuerzo, no habilita nada que sin él sea imposible. Si un comando empieza a decidir cosas que una persona no podría reproducir a mano, el defecto está en el comando.

**Ningún comando infiere un campo que quien invoca no dio**, salvo donde una spec declare un valor por defecto. Los que hay hoy: la hora de un registro, que por defecto es la actual ([bitacora.md](bitacora.md)).

## Los códigos de salida

Son contrato. Quien invoca decide qué hacer según el código, sin leer el mensaje.

| Código | Significa | Qué hacer |
| --- | --- | --- |
| 0 | Éxito | Seguir |
| 1 | Rechazo: el comando entendió y se negó por el estado del vault | Corregir el estado, o pasar el flag que la salida indica |
| 2 | Error de uso: la invocación está mal formada | Corregir la invocación |
| 3 | Entorno: la instalación de TUKU no está donde debería | No reintentar; se arregla la instalación, no el comando |

El **2 está reservado**: lo emite argparse ante una invocación mal formada y ningún comando puede devolverlo por otra causa. Un rechazo y un comando mal escrito son cosas distintas, y quien invoca tiene que poder distinguirlas sin leer prosa. Es un choque real y ya ocurrió: `TukuHomeInvalido` devolvía 2, igual que argparse, y desde fuera no había forma de saber si corregir el comando o la instalación.

Códigos nuevos se agregan a esta tabla antes que al código. Fijados en `tuku/cli.py` como constantes con nombre, nunca como literales.

## La salida es una sola, para persona y para agente

Un solo mensaje en prosa, que sirve a los dos. **Sin `--json`.** Hoy no lo consume nadie, obligaría a mantener y probar dos caminos de salida, y sobre todo le daría una salida de escape a la prosa: en cuanto el agente lee otra cosa, el mensaje humano deja de importar y se degrada. Los códigos de salida ya son el canal legible por máquina y no necesitan formato estructurado.

**Toda salida de error nombra el defecto y la corrección.** Decir qué pasó no basta; hay que decir qué hacer. `tuku init` sobre un directorio con contenido no dice solo que está ocupado, dice que `--force` lo reemplaza. La regla vale igual para la persona que escribió rápido y para el agente que tiene que decidir el paso siguiente, y por eso el mensaje es uno solo.

Que se cumpla es verificable: la ayuda y los códigos de cada epic se fijan en un escenario, según la convención de [`../devel/epics.md`](../devel/epics.md).

## Ante la duda, informar y no escribir

Un comando que no puede determinar algo **no lo adivina y no escribe a medias**. Sale con el código que corresponde y dice qué le falta. Es el principio 3 de [`../docs/principios.md`](../docs/principios.md) aplicado a la capa determinista, y es lo que hace que la salida sirva como advertencia en vez de como registro de un daño ya hecho.

De ahí la asimetría de `tuku entry lint` ([bitacora.md](bitacora.md)): informa y nunca escribe. Verificar y corregir son operaciones distintas, y mezclarlas quita la oportunidad de revisar.

## No entra

- Qué comandos existen y qué hace cada uno. Eso lo especifica la spec de la primitiva que el comando toca: el registro en [bitacora.md](bitacora.md), los pendientes en [pendientes.md](pendientes.md), el ciclo en [ciclo.md](ciclo.md).
- Cómo se instala `tuku` y dónde vive su árbol. Eso es [`../devel/epics.md`](../devel/epics.md), epic 001.
- Cómo un agente decide qué comandos emitir. Eso es [agente.md](agente.md).
