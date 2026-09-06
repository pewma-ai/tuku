# Escenario · 002-006-transclusiones-sincronizadas

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 002, fase 2, regla 6 de [`../../spec/pendientes.md`](../../spec/pendientes.md). `jntr.transclusiones-sync`, las dos direcciones de falla.

## Estado inicial

El que dejó [`002-005-escribir-en-un-dia-fecha`](002-005-escribir-en-un-dia-fecha.md): el callout `^2026-08-12` con un ítem, y su transclusión al inicio del miércoles.

Las dos inyecciones de este escenario entran por la **segunda vía**: no son hechos de la vida del autor, así que no pasan por la bitácora. Se rompe el archivo a mano y se invoca el janitor, que es la única otra puerta que existe ([`../../spec/flujo-informacion.md`](../../spec/flujo-informacion.md)).

## Escenario: callout sin transclusión, la falla silenciosa

Dado el pendiente fechado y su transclusión en el miércoles 12
Cuando se borra a mano la línea de transclusión, dejando el callout intacto
Y se corre `jntr.transclusiones-sync`
Entonces la línea de transclusión vuelve al inicio del miércoles 12
Y el diff contra el estado inicial de este escenario es vacío

Es la peligrosa de las dos. No se ve: el pendiente simplemente no aparece en la agenda, y el autor se entera cuando ya venció.

## Escenario: transclusión sin callout, la falla visible

Dado el mismo estado, ya reparado
Cuando se agrega a mano `![[PENDIENTES#^2026-08-14]]` bajo el viernes 14, sin que ese ancla exista
Y se corre `jntr.transclusiones-sync`
Entonces la línea se quita del viernes
Y no se crea el callout `^2026-08-14` para justificarla

Esta se ve sola: hay una caja de error en el día y alguien la arregla. El janitor la quita igual, porque una caja de error en `AHORA.md` es un defecto y no un estado válido.

## Escenario: las anclas de horizonte no necesitan vigilancia

Dado que los cinco callouts de horizonte son permanentes
Cuando corre el janitor
Entonces no toca ninguna transclusión de horizonte
Y el problema queda acotado a los callouts fechados, que aparecen y desaparecen con el uso

## Escenario: correrlo sobre un vault sano no hace nada

Dado el vault ya sincronizado
Cuando se corre el janitor dos veces seguidas
Entonces el diff es vacío las dos veces

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_006
```

## Qué se mira a mano

- Abrir el vault en Obsidian **entre las dos inyecciones**, con la transclusión rota, y confirmar que la falla silenciosa efectivamente no se ve. Es lo que justifica que el janitor exista.
- Que el estado final sea indistinguible del que dejó `002-005`, comparándolo con `diff -r` contra su carpeta de playground.
