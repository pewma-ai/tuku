# Proceso: apertura de ciclo

> Ejecutable por un humano con un editor de texto, o por un agente de inteligencia media
> (P2). Orden de operaciones completo en `spec/artefactos-ciclo.md` §5.

## Cuándo

Al comienzo de un nuevo ciclo de trabajo: turno, semana, misión, viaje, etc. Puede
dispararse desde una cadencia (`emit: { kind: ciclo, cycle_type: ... }`) o crearse a mano.

## Pasos

1. **Resolver el ciclo.** Determinar `cycle_type`, `cycle_start` y `cycle_end`. Si hay un
   plan sembrado por cadencia, usarlo; si no, crearlo con las fechas reales.

2. **Incrementar `cycles` en tareas abiertas.** Para cada tarea en `tareas/tareas.md` que
   corresponda a este ciclo, incrementar el contador de arrastre.

3. **Re-resolver fechas relativas** (`next:<tipo>`) contra el calendario de planes (`ciclos/`).
   Verificar que las tareas con `next:<tipo>` tengan un plan futuro contra el cual resolver
   (si no, `tuku doctor` lo advertirá — no es error, es advertencia).

4. **Crear `plan_<cycle_start>_<cycle_type>.md`** en `ciclos/` con el front matter:

   ```yaml
   ---
   id: plan-<cycle_start>-<cycle_type>
   type: plan
   cycle_type: <tipo>
   cycle_start: <YYYY-MM-DD>
   cycle_end: <YYYY-MM-DD>
   status: open
   created: <YYYY-MM-DD>
   modified: <YYYY-MM-DD>
   seeded_by: tuku/<version>
   ---
   # Plan del ciclo
   ```

   Con las secciones obligatorias:
   - `## Intención` — qué se busca lograr por entidad.
   - `## No entra (y por qué)` — **no puede estar vacía** (C5). Si nada se excluye, el
     plan no está acotado.
   - `## Restricciones y contexto` — viajes, reuniones fijas, disponibilidad.
   - `## Señales a vigilar` — opcional.
   - Bloque derivado `<!-- tuku:derived id=tareas-del-ciclo hash=... -->`.

5. **Renderizar las derivadas del plan** (`tuku build tareas-del-ciclo`).

6. **Ejecutar janitors** (`tuku janitor`).

7. **Commit semántico.**

## Insumos del sembrado (paso 4)

| Insumo | Aporta |
|---|---|
| `resultados_*` de los 3–4 ciclos anteriores | aprendizajes, desviaciones, momentum |
| `tareas/tareas.md` | vigentes, postergadas, bloqueadas |
| Entidades vigentes con `alineamiento` | qué está activo y qué persigue |
| `estrategia/capacidad.md` | límite contra el que se contrasta la intención |
| Cadencias vigentes | compromisos rítmicos que caen en el ciclo |

## Pasos deterministas vs. agénticos

Los pasos 1–3 y 5–7 son deterministas: funcionan sin ningún modelo. Solo el 4 requiere
agente para redactar la Intención y el análisis. Sin modelo (`--sin-agente`), el plan se
crea con los insumos listados y sin redacción: **el ciclo abre igual sin conexión** (P2).

## Verificación

- `plan_*` tiene front matter completo con `status: open` y `cycle_type`.
- La sección `## No entra (y por qué)` no está vacía (C5).
- `tuku janitor` no reporta violaciones C1–C7.
