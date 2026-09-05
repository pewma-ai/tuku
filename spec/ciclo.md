# spec · ciclo

> `AHORA.md` es el ciclo en curso. Se justifica por el principio 1 y el principio 9 de `../docs/principios.md`. Si el ciclo es o no una primitiva propia sigue abierto (ver `README.md`).

## `AHORA.md`, el ciclo en curso

Lo único canónico aquí son **las entradas**. El resto es vista y entra por transclusión.

```markdown
---
ciclo: turno
desde: 2026-08-25
hasta: 2026-09-01
---

# Plan

![[planes/plan-2026-08-25-turno.md]]

# Actividad diaria

## Martes 25 de agosto
![[PENDIENTES.md#^2026-08-25]]
- 09:12 - [[ambito]] **clasificacion**: cuerpo
- 14:30 - [[ambito]] **clasificacion**: cuerpo

## Miércoles 26 de agosto
![[PENDIENTES.md#^2026-08-26]]
```

**No tiene resumen.** El resumen se genera al cerrar, así que no existe mientras el ciclo está abierto.

## `bitacoras/bitacora-<desde>-<hasta>.md`, el ciclo cerrado

```markdown
---
ciclo: turno
desde: 2026-08-25
hasta: 2026-09-01
---

# Plan

(texto del plan, aplanado)

# Actividad diaria

## Martes 25 de agosto
(pendientes de ese día, aplanados)
- 09:12 - [[ambito]] **clasificacion**: cuerpo

# Resumen del ciclo

[Resumen del ciclo](../reportes/resumen-2026-08-25-turno.md)
```

## Qué cambia al cerrar

| Bloque | Abierto | Cerrado |
| --- | --- | --- |
| Plan | transclusión desde `planes/` | texto aplanado |
| Pendientes del día | transclusión desde `PENDIENTES.md` | texto aplanado |
| Entradas | canónicas | sin cambios |
| Resumen | no existe | enlace a `reportes/` |

Aplanar no contradice la fuente única. La fuente única evita que dos copias **vivas** diverjan, y al cerrar nada sigue vivo: lo que queda es un snapshot. Lo que sí se rompería es el principio 1, porque un archivo lleno de `![[...]]` no se lee con un editor básico ni dentro de veinte años.

El resumen es la excepción y va como enlace: es un documento de decisión completo, demasiado grande para copiarlo, y un enlace markdown sí se lee en texto plano.

**Durante el ciclo, transclusión. Al cerrarlo, texto. El resumen, siempre enlace.**

## Abrir un ciclo

En este orden:

1. Crear `AHORA.md` con frontmatter (`ciclo`, `desde`, `hasta`) → `jntr.ciclo-abrir`
2. Sembrar los días con `## Día, DD de MM` → `jntr.ciclo-abrir`
3. Rodar y promover pendientes: `este-turno` sin fecha rueda, `proximo-turno` promueve → `jntr.pendientes-promover`
4. Colectar cadencias desde el árbol y emitir lo que corresponda → `jntr.cadencias-colectar`, `jntr.cadencias-resolver`, `jntr.cadencia-inyectar`
5. Generar el plan en `planes/` y transcluirlo → `jntr.capacidad-calcular` lo alimenta
6. Transcluir los pendientes de cada día → `jntr.transclusiones-sync`

Idempotencia: abrir dos veces no duplica días, ni pendientes, ni emisiones.

## Cerrar un ciclo

En este orden:

1. Generar el resumen en `reportes/`, que necesita el plan y las entradas todavía vivos → `jntr.ciclo-extracto` lo alimenta
2. Aplanar el plan y los pendientes de cada día → `jntr.transclusiones-aplanar`
3. Dejar el enlace al resumen → `jntr.ciclo-cerrar`
4. Mover a `bitacoras/bitacora-DESDE-HASTA.md` → `jntr.ciclo-cerrar`
5. Dejar `AHORA.md` limpio para el ciclo siguiente → `jntr.ciclo-cerrar`

**El orden importa**: aplanar antes de generar el resumen lo deja sin de dónde leer.

Idempotencia: cerrar dos veces no vuelve a mover ni a duplicar.

## Planes

Estructura del plan:

- **Intención del ciclo**: lista corta, cada punto es un ámbito y su acción principal
- **No entra, y por qué**: la razón es parte del plan, no un comentario
- **Restricciones y contexto**: lo que acota el ciclo antes de empezar
- **Señales a vigilar**: qué observar durante el ciclo sin que sea tarea

Calcular la capacidad antes de planificar → `jntr.capacidad-calcular`:

- Partir de las horas del ciclo y restar el costo fijo: roles operativos, viajes, días con los niños.
- Un rol operativo cuesta horas **por día**, no una vez.
- Se planifica contra lo que queda. Planificar contra las horas brutas es la forma más común de fallar.

Trae al plan:

- Pendientes heredados del ciclo anterior → `jntr.pendientes-promover`
- Cadencias que caen dentro del ciclo → `jntr.cadencias-resolver`
- Qué quedó abierto y sin cerrar en el ciclo anterior → `jntr.ciclo-extracto`

El plan se propone al autor y no se escribe sin su aprobación. Mover algo a "No entra" pospone sus pendientes y silencia sus alertas de ausencia → `jntr.plan-no-entra`.

Registrar cuánto corrigió el autor el plan propuesto → `jntr.plan-delta`. Sin correcciones también es información: dice que la propuesta estuvo bien calibrada.

## Resumen del ciclo

Al cerrar, se genera en `reportes/` y se deja solo el enlace en la bitácora → `jntr.ciclo-extracto`.

Estructura del resumen:

- **Resumen ejecutivo**: tema dominante del ciclo, qué se logró, dónde está el foco urgente
- **Veredicto por intención**: cumplida, parcial, en riesgo o sin avance, cada una con su acción siguiente
- **Desglose por ámbito**: estado, pendientes que siguen abiertos, actividad realizada
- **Emergente**: lo que ocurrió sin estar en el plan
- **Momentum y señales**: pocos logros que cambian la trayectoria, y señales que merecen atención más allá del ciclo

El veredicto sale de comparar plan contra ejecución, no de resumir la actividad.

## No entra

- **Juzgar la calidad de la prosa** del plan o el resumen.
- **Decidir el tipo de ciclo real de quien lo usa.** El estado cero arranca en semanal y el tipo verdadero emerge después; esa regla de arranque vive en `../devel/que_implementar.md` (estrategia de pruebas, estado cero).
