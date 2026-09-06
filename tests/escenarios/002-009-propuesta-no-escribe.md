# Escenario · 002-009-propuesta-no-escribe

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 002. El principio 3 convertido en test: la propuesta se muestra y espera, y rechazarla no deja rastro. Es la prueba dura del epic 005 anticipada barato, con la única consecuencia que a propósito no tiene janitor.

## Estado inicial

El que dejó [`002-008-crear-nota`](002-008-crear-nota.md). Es el último paso determinista de la cadena, así que su estado final es el que se revisa contra el criterio de salida del epic.

## Escenario: el hecho se registra y lo que sugiere se propone

Dado el ámbito `depto-centro` creado y un pendiente de GGCC ya cerrado en el martes 11
Cuando se inyecta
`- 20:40 - [[depto-centro]] **señal**: la administradora respondió que este mes no pagará los GGCC, y se repite`
Entonces la entrada queda escrita en el martes 11
Y el sistema propone abrir un pendiente de recobro
Y el diff contra el estado anterior es **exactamente** esa línea de `AHORA.md`
Y `PENDIENTES.md`, `ambitos/` y `notas/` quedan byte a byte iguales

El impago recurrente pide un pendiente, pero el autor no lo pidió. No se agrega lo que no se dijo ([`../../spec/bitacora.md`](../../spec/bitacora.md)).

## Escenario: rechazar la propuesta no deja rastro en ninguna primitiva

Dado la propuesta emitida y no aprobada
Cuando el autor la rechaza
Entonces el diff contra el estado que había antes de rechazarla es vacío
Y no queda registro del rechazo en ninguna primitiva

Una propuesta rechazada no escribe nada, así que no hay nada que limpiar, y por eso esta consecuencia es la única sin janitor ([`../../spec/flujo-informacion.md`](../../spec/flujo-informacion.md)).

## Escenario: aprobarla sí escribe, y por la vía normal

Dado la misma propuesta
Cuando el autor la aprueba
Entonces se abre el pendiente igual que en [`002-003`](002-003-abrir-pendiente.md), en `^sin-fecha`
Y el resultado es indistinguible de haberlo dictado

Este escenario aprueba y después revierte, para que el estado que hereda [`002-010`](002-010-dictado-del-dia-uno.md) sea el del rechazo. La aprobación se afirma, no se conserva: el día uno del corpus termina sin ese pendiente.

## Escenario: la propuesta no se emite dos veces

Dado la propuesta ya rechazada
Cuando se vuelve a correr el flujo sobre la misma entrada
Entonces vuelve a proponerse, porque no hay estado que recuerde el rechazo
Y el diff sigue vacío

Que insista es correcto mientras no escriba. Si algún día molesta, la solución es memoria de rechazos y eso es un cambio de diseño, no un defecto de este paso.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_009
```

## Qué se mira a mano

- **El estado final de la cadena, contra el criterio de salida del epic:** un vault donde hay pendientes abiertos, un ámbito nuevo y una nota enlazada, sin que el autor haya abierto `PENDIENTES.md` ni `ambitos/` a mano. Este playground es el artefacto que se revisa para cerrar el epic 002.
- Cómo se ve la propuesta cuando aparece: si no se distingue de una afirmación, el principio 3 está roto en la superficie aunque el diff esté limpio.
