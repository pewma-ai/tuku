# Escenario · 002-005-escribir-en-un-dia-fecha

**Cubre:** epic 002, punto 3, la razón de ser del epic: agendar es escribir donde corresponde, sin un comando aparte para fechar.

## Estado inicial

El que dejó [`002-004-cerrar-pendiente`](002-004-cerrar-pendiente.md): los cinco horizontes existen y están vacíos.

## Escenario: escribir un pendiente en un día futuro lo fecha

Dado el ciclo abierto del 11 al 17 de agosto, con HOY en el martes 11
Cuando se inyecta, bajo `## Miércoles 12 de agosto`, la línea
`- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo`
Entonces nace el callout de fecha `^2026-08-12` en `PENDIENTES.md`
Y contiene `- [[personal]] - pagar la sesión con el psicólogo`
Y el miércoles 12 de `AHORA.md` abre con la transclusión de ese ancla
Y el pendiente **no** aparece en `^sin-fecha` ni en ningún horizonte con nombre

Nació con fecha exacta sin pasar por la escalera, que describe cómo se concreta lo que nació difuso y no es un camino obligatorio ([`spec/pendientes.md`](../../spec/pendientes.md)).

## Escenario: fechar mueve, nunca copia

Dado el mismo estado
Cuando se termina la inyección
Entonces el pendiente está en exactamente un callout
Y `jntr.pendientes-lint` no encuentra ninguna aparición duplicada

Regla 1 de `spec/pendientes.md`, y el error que el vault real tuvo que prohibir por escrito: la misma tarea en el callout del día y en la caja de la semana ([`lecciones-macjpgil.md`](../../devel/lecciones-macjpgil.md), lección 7).

## Escenario: el callout de fecha es efímero, el de horizonte no

Dado que `^2026-08-12` no existía antes de esta inyección
Cuando nace
Entonces nace por debajo de los cinco horizontes permanentes, sin desplazarlos
Y ninguno de los cinco desaparece por seguir vacío

## Escenario: el movimiento de escalón no se registra en la bitácora

Dado el pendiente ya fechado
Cuando se revisa `AHORA.md`
Entonces la única línea nueva es la entrada `**pendiente**` que el autor escribió
Y no hay ninguna entrada que narre que el pendiente cambió de callout

Mover un pendiente es un hecho del sistema, no de la vida del autor.

## Escenario: inyectar dos veces no duplica el callout ni la transclusión

Dado el pendiente ya fechado y transcluido
Cuando se corre el janitor otra vez
Entonces el diff es vacío
Y hay un solo callout `^2026-08-12` y una sola línea de transclusión en el miércoles

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_005
```

## Qué se mira a mano

- **Abrirlo en Obsidian**, que es donde esto se verifica: el miércoles 12 muestra el pendiente transcluido, no una caja de error ni el texto crudo del embed.
- Que agendar se haya sentido como escribir en una agenda de papel. Si el autor tuvo que pensar en callouts o anclas, el punto 3 del epic no está cumplido.
