# Escenario · 002-07-transclusiones-sincronizadas

**Cubre:** epic 002, fase 2, regla 6 de [`spec/pendientes.md`](../../spec/pendientes.md). `tuku transclusion sync`, las dos direcciones de falla.

## Estado inicial

El que dejó [`002-06-escribir-en-un-dia-fecha`](002-06-escribir-en-un-dia-fecha.md): el callout `^2026-08-12` con un ítem, y su transclusión al inicio del miércoles.

Las dos inyecciones entran por la **segunda vía**: no son hechos de la vida del autor, así que no pasan por la bitácora. Se rompe el archivo a mano y se invoca el comando, la única otra puerta ([`spec/flujo-informacion.md`](../../spec/flujo-informacion.md)).

## Escenario: callout sin transclusión, la falla silenciosa

Dado el pendiente fechado y su transclusión en el miércoles 12
Cuando se borra a mano la línea de transclusión, dejando el callout intacto
Y se corre `tuku transclusion sync`
Entonces la línea de transclusión vuelve al inicio del miércoles 12
Y el diff contra el estado inicial de este escenario es vacío

La peligrosa de las dos, porque no se ve: el pendiente no aparece en la agenda y el autor se entera cuando ya venció.

## Escenario: transclusión sin callout, la falla visible

Dado el mismo estado, ya reparado
Cuando se agrega a mano `![[PENDIENTES#^2026-08-14]]` bajo el viernes 14, sin que ese ancla exista
Y se corre `tuku transclusion sync`
Entonces la línea se quita del viernes
Y no se crea el callout `^2026-08-14` para justificarla

Esta se ve sola, es una caja de error en el día. El comando la quita igual: una caja de error en `AHORA.md` es un defecto, no un estado válido.

## Escenario: las anclas de horizonte no necesitan vigilancia

Dado que los cinco callouts de horizonte son permanentes
Cuando corre el comando
Entonces no toca ninguna transclusión de horizonte
Y el problema queda acotado a los callouts fechados, que aparecen y desaparecen con el uso

## Escenario: correrlo sobre un vault sano no hace nada

Dado el vault ya sincronizado
Cuando se corre el comando dos veces seguidas
Entonces el diff es vacío las dos veces

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_07
```

## Qué se mira a mano

- Abrirlo en Obsidian **entre las dos inyecciones**, con la transclusión rota, y confirmar que la falla silenciosa no se ve. Es lo que justifica el comando.
- Que el estado final sea indistinguible del que dejó `002-06`, con `diff -r` contra su playground.
