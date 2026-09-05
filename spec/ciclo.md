# spec · ciclo

> `AHORA.md` es el ciclo en curso. Se justifica por el principio 1 y el principio 9 de [`../docs/principios.md`](../docs/principios.md). Si el ciclo es o no una primitiva propia sigue abierto (ver [`README.md`](README.md)).

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
5. Generar el plan en `planes/` y transcluirlo → `jntr.capacidad-calcular` lo alimenta, leyendo los `CAPACIDAD.md` del árbol
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

- Partir de los días que cuentan en el ciclo y restarles el costo fijo: roles operativos, viajes, días con los niños.
- Un rol operativo se cobra **cada día que dura**, no una vez.
- Se planifica contra lo que queda. Planificar contra el ciclo entero es la forma más común de fallar.

### De dónde lee: `CAPACIDAD.md`

El bruto y los costos fijos los declara el autor en archivos `CAPACIDAD.md` repartidos por el árbol de ámbitos (dónde vive cada uno y por qué se acumulan, en [`ambitos.md`](ambitos.md)).

**No se declara en horas.** Pedirle al autor que cuantifique su semana es la forma más rápida de que deje de mantener el archivo, y además es una precisión falsa: nadie sabe cuántas horas le va a costar un turno. Se declara con el mismo vocabulario grueso con que uno lo diría en voz alta.

```markdown
## Bruto

**Días que cuentan:** de lunes a viernes
**Qué tan lleno:** un día completo, salvo el viernes, que es media jornada

## Costo fijo

### Turno operativo
**Cuesta:** casi todo el día
**Cuándo:** los días de turno del ciclo
**Por qué:** el turno no deja bloques largos, solo huecos entre operaciones

### Traslado a Paranal
**Cuesta:** el día entero
**Cuándo:** el primer y el último día del turno
```

`Bruto` va una sola vez, en `ambitos/personal/`. Cada bloque de `Costo fijo` va en el ámbito que lo causa, y todos se restan del mismo bruto.

Dos campos son de máquina, uno es de persona:

| Campo | Para quién | Qué hace |
| --- | --- | --- |
| `Cuesta` | máquina | Cuánto consume del día, en el vocabulario cerrado de abajo |
| `Cuándo` | máquina | Qué días del ciclo lo cobran |
| `Por qué` | persona | La razón, para que no se borre cuando parezca exagerado |

**El vocabulario de magnitud es cerrado**, como las tres marcas de la bitácora. Cuatro escalones, y el autor no los puede extender:

| Se escribe | Qué significa |
| --- | --- |
| `el día entero` | Ese día no entra nada más |
| `casi todo el día` | Queda un hueco, sirve para una cosa corta |
| `media jornada` | Queda la mitad utilizable |
| `un rato` | Descuenta, pero el día sigue siendo un día |

Cerrado porque es lo que permite que el janitor sume sin interpretar, y corto porque un quinto escalón obliga al autor a deliberar sobre la diferencia entre dos etiquetas parecidas, que es exactamente el trabajo que el sistema le está quitando. Las variantes de redacción (*"casi entero"*, *"casi completo"*) las normaliza el linter, igual que hace con las clasificaciones.

Lo que sale de sumar no es un número de horas: es cuánto cabe en el ciclo, en la misma escala. El plan se dimensiona contra eso.

`Cuándo` depende del tipo de ciclo, igual que el trigger de una cadencia: *"los días de turno"* no se resuelve con un almanaque. El cálculo de capacidad hereda esa dependencia y sus dos trampas conocidas (ver [`cadencias.md`](cadencias.md)).

`Por qué` cumple aquí el mismo papel que `Historia` en una cadencia. Un costo fijo sin razón escrita es lo primero que el autor recorta cuando quiere que el ciclo le quepa, y es exactamente lo que no debe recortar.

**La capacidad no se registra en la bitácora.** Declararla es escribir una regla, no ocurrió como hecho. Cambiarla sí es una decisión y el autor puede registrarla como tal, pero eso es una entrada más, no el mecanismo.

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
- **Decidir el tipo de ciclo real de quien lo usa.** El estado cero arranca en semanal y el tipo verdadero emerge después; esa regla de arranque vive en [`../devel/que_implementar.md`](../devel/que_implementar.md) (estrategia de pruebas, estado cero).
