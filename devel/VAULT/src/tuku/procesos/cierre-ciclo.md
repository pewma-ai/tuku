# Proceso: cierre de ciclo

> Ejecutable por un humano con un editor de texto, o por un agente de inteligencia media
> (P2). Orden de operaciones completo en `spec/artefactos-ciclo.md` §6.

## Cuándo

Al terminar un ciclo: al final del turno, de la semana, del viaje, etc. El archivo
`plan_*` correspondiente debe existir con `status: open`.

## Pasos

1. **Recoger marcas de completitud.** Propagar al canónico (`tareas/tareas.md`) las marcas
   `[x]` o `[-]` dejadas en proyecciones del plan.

2. **Calcular el alcance evaluable.** Unión de:
   - Entidades declaradas en `## Intención` del plan.
   - Entidades que registraron entradas durante el ciclo (aunque no estuvieran planeadas).
   - **Excluidas**: lo declarado en `## No entra` y lo no tocado ni declarado.

3. **Crear `resultados_<cycle_start>_<cycle_type>.md`** en `ciclos/` con el front matter:

   ```yaml
   ---
   id: resultados-<cycle_start>-<cycle_type>
   type: resultados
   cycle_type: <tipo>
   cycle_start: <YYYY-MM-DD>
   cycle_end: <YYYY-MM-DD>
   status: closed
   created: <YYYY-MM-DD>
   seeded_by: tuku/<version>
   ---
   # Resultados del ciclo
   ```

   Con las secciones obligatorias (C7):
   - `## TL;DR` — una o dos frases: carácter del ciclo y su saldo.
   - `## Avances`
   - `## Desviaciones`
   - `## Aprendizajes`
   - `## Momentum y señales`
   - Bloque derivado `<!-- tuku:derived id=bitacora-ciclo hash=... -->` con entradas congeladas.

4. **Generar informes por audiencia** con `trigger: cycle_close`, si existen en `config.yaml`.

5. **Marcar `status: closed`** en el `plan_*` correspondiente.

6. **Archivar** tareas cuyo plazo de retención venció; archivar meses cerrados de `entradas/`.

7. **Ejecutar janitors** (`tuku janitor`).

8. **Commit semántico.**

## Pasos deterministas vs. agénticos

Los pasos 1–2 y 4–8 son deterministas. Solo el 3 requiere agente para redactar el análisis
contrastando intención vs. resultado por entidad. Sin modelo (`--sin-agente`), el
`resultados_*` se crea con la estructura obligatoria (C7) y la bitácora congelada, sin
redacción — **el ciclo cierra igual sin conexión** (P2).

## Cómo se generan las secciones

| Sección | Origen |
|---|---|
| TL;DR | agente (síntesis del carácter del ciclo) |
| Avances | entradas `Hito` + tareas completadas + contraste por entidad |
| Desviaciones | intención sin correspondencia + arrastre sobre umbral + contraste por entidad |
| Aprendizajes | entradas `Señal`/`Decisión` + lo que el contraste revela |
| Momentum y señales | señales + entidades con actividad anómala |

La fricción no se declara: se descubre en el contraste por entidad (ADR 0010).

## Verificación

- `resultados_*` tiene los cinco encabezados de C7.
- Plan correspondiente tiene `status: closed` (C4).
- `plan_*` y `resultados_*` comparten `cycle_start` y `cycle_type` (C1).
- `tuku janitor` no reporta violaciones C1–C7.
