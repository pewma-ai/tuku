# spec · ciclo

> `AHORA.md` es el ciclo en curso. Se justifica por el principio 1 y el principio 9 de [`../docs/principios.md`](../docs/principios.md). El ciclo es un proceso y no una primitiva: `tuku process cycle` lo abre, y se compone sobre la bitácora, los pendientes y las notas.

## `AHORA.md`, el ciclo en curso

Lo único canónico aquí son **los registros**. El resto es vista, y entra de dos maneras distintas: el plan por transclusión, los pendientes del día por propagación ([`pendientes.md`](pendientes.md), "dónde se muestra y cómo llega").

El frontmatter es OKF, con los campos en inglés porque son superficie de máquina (ver [`vault.md`](vault.md), "El frontmatter"). `AHORA.md` y una bitácora cerrada llevan **el mismo `type`**, `Logbook`: los separa `status`, que es `draft` mientras el ciclo está abierto y `stable` cuando se archiva y deja de tocarse. `from` y `to` son el rango que cubre, y son lo que dice dónde termina el ciclo: no hay ninguna marca en el cuerpo que lo repita.

**Cada ciclo tiene un nombre y un rango.** `cycle` dice cuál es (`cycle: semana`, `cycle: turno`) y `from` y `to`, el rango que cubre. Los nombres posibles los declara el autor en `cycle_name` de [`reglas/config.tuku.md`](vault.md), "La configuración", como una lista (`turno, descanso`), y vale `semana` si no declara ninguno. **El ciclo siguiente es el siguiente de la lista**, y al llegar al final vuelve al primero; con un solo nombre, es el mismo.

**El rango se deduce solo con `semana`**, que va de lunes a domingo: `tuku init --at` y `tuku process cycle --at` reciben un día cualquiera y abren la semana que lo contiene, así que `from` es siempre un lunes y `to`, el domingo siguiente. **Con cualquier otro nombre el rango es un dato del autor**, porque un turno dura 8 días, o 10, o 14, y nada lo deduce: el agente le pregunta hasta qué día va el ciclo y abre con ese rango. Decidir el rango es del autor; abrir un ciclo con un rango dado es determinista. Con `cycle_name: turno, descanso`, un turno del martes 11 al martes 18 de agosto y el descanso que le sigue, del miércoles 19 al lunes 24, son dos ciclos:

```markdown
---
type: Logbook
status: draft
cycle: turno
from: 2026-08-11
to: 2026-08-18
---
```

Hoy `process cycle` solo abre la semana. `cycle_name`, `cycle:` y el rango dado entran con lo que dice [`../TODO.md`](../TODO.md), "Ciclos con nombre, config y libro de estilo".

```markdown
---
type: Logbook
status: draft
cycle: semana
from: 2026-08-24
to: 2026-08-30
---

# Plan

![[planes/plan-2026-08-25-turno.md]]

# Actividad diaria

> [!todo] Pendientes de esta semana
> - [personal](ambitos/personal/personal.md) - comprar una maleta

## Martes 25 de agosto

> [!todo] Pendientes del día
> - [arriendo-depto-centro](ambitos/arriendo-depto-centro/arriendo-depto-centro.md) - avisar de los GGCC al arrendatario

- 09:12 - [ambito](ruta) **clasificacion**: cuerpo
- 14:30 - [ambito](ruta) **clasificacion**: cuerpo

## Miércoles 26 de agosto

> [!todo] Pendientes del día
> - [personal](ambitos/personal/personal.md) - pagar la sesión con el psicólogo
```

Lo que va entre el encabezado del día y el primer registro es la **región propagada**, y su dueño es `tuku regenerate todo`. También lo es el callout de la semana, bajo `# Actividad diaria` y antes del primer día ([`pendientes.md`](pendientes.md)). Se distingue sin marca: los registros empiezan por `- HH:MM - `.

**No tiene resumen.** El resumen se genera al cerrar, así que no existe mientras el ciclo está abierto.

## `bitacoras/bitacora-<desde>-<hasta>-<ciclo>.md`, el ciclo cerrado

```markdown
---
type: Logbook
status: stable
cycle: semana
from: 2026-08-24
to: 2026-08-30
---

# Plan

(texto del plan, aplanado)

# Actividad diaria

## Martes 25 de agosto
(pendientes de ese día, aplanados)
- 09:12 - [ambito](ruta) **clasificacion**: cuerpo

# Resumen del ciclo

[Resumen del ciclo](../reportes/resumen-2026-08-25-turno.md)
```

## Qué cambia al cerrar

| Bloque | Abierto | Cerrado |
| --- | --- | --- |
| Plan | transclusión desde `planes/` | texto aplanado |
| Pendientes del día y de la semana | propagados desde `PENDIENTES.md` | ya son texto, no cambian |
| Registros | canónicos | sin cambios |
| Resumen | no existe | enlace a `reportes/` |

Aplanar no contradice la fuente única. La fuente única evita que dos copias **vivas** diverjan, y al cerrar nada sigue vivo: lo que queda es un snapshot. Lo que sí se rompería es el principio 1, porque un archivo lleno de `![[...]]` no se lee con un editor básico ni dentro de veinte años.

Los pendientes del día ya no necesitan aplanarse, y esa es una simplificación que trajo la propagación: llegaron como texto, así que al cerrar el ciclo no hay nada que hacer con ellos. Lo único que se aplana es el plan.

El resumen es la excepción y va como enlace: es un documento de decisión completo, demasiado grande para copiarlo, y un enlace markdown sí se lee en texto plano.

**El plan, transclusión mientras el ciclo vive y texto al cerrarlo. Los pendientes, texto desde el principio. El resumen, siempre enlace.**

## Abrir un ciclo

De los comandos de esta sección y de las siguientes, hoy existen `tuku process cycle`, `tuku doctor cycle` y `tuku regenerate todo`. Los demás (`todo promote`, `cadence …`, `capacity calc`, `cycle extract`, `cycle close`, `transclusion flatten`, `plan …`) son diseño y entran con el epic 006. Hoy `process cycle` hace los pasos 1 y 2, y el pendiente de revisar la bitácora anterior.

En este orden:

1. Instanciar `reglas/plantilla/AHORA.md`, con `from` y `to` del ciclo y `status: draft` → `process cycle`
2. Sembrar los días con `## Día DD de mes` → `process cycle`
3. Rodar y promover pendientes: lo del horizonte del ciclo en curso que no tenga fecha rueda al del ciclo nuevo, y el horizonte siguiente promueve → `todo promote`
4. Colectar cadencias desde el árbol y emitir lo que corresponda → `cadence collect`, `cadence resolve`, `cadence inject`
5. Generar el plan en `planes/` y transcluirlo → `capacity calc` lo alimenta, leyendo los `CAPACIDAD.md` del árbol
6. Propagar los pendientes a cada día → `regenerate todo`

Idempotencia: abrir dos veces no duplica días, ni pendientes, ni emisiones.

### El primer día se revisa la bitácora anterior

Un ciclo que sigue a otro cerrado abre con el pendiente `revisar la bitácora anterior`, con vencimiento el primer día: aparece en el callout de ese día y en `PENDIENTES.md` con su fecha. Revisar lo vivido antes de planificar lo que viene es lo que fuerza el aprendizaje, y por eso el comando lo abre y no queda a la memoria del autor.

Lo abre `process cycle` cuando crea el ciclo y `bitacoras/` tiene una bitácora. El primer ciclo de un vault no tiene nada que revisar y no lo trae. Es un pendiente como cualquiera: se cierra con `tuku todo close`, y abrir el ciclo otra vez no lo duplica. Si no se puede abrir, el ciclo queda abierto y el motivo sale como aviso.

### La estructura del ciclo sale de una plantilla

`process cycle` no construye el ciclo: **instancia `reglas/plantilla/AHORA.md`**, sustituyendo las fechas del frontmatter y de los encabezados de los días. Ante la omisión de fecha de apertura, toma por defecto la fecha actual (**HOY**) evaluada en la zona horaria `TZ` de `reglas/config.tuku.md` para determinar el rango: con `semana`, la semana que contiene esa fecha; con otro nombre de `cycle_name`, el rango que se le pasó, que el comando exige. Genera un encabezado de día por cada fecha entre `from` y `to`, así que un turno de 8 días trae 8 y uno de 14, 14. La plantilla es del autor y vive en su vault, así que qué secciones trae un ciclo recién abierto se cambia editándola y no tocando el comando.

### Un ciclo abierto con registros no se pisa

Abrir un ciclo cuya fecha cae fuera del que ya está abierto **se rechaza** si ese ciclo tiene registros escritos. Archivar es una consecuencia mayor y nadie la aprobó (principio 3 de [`../docs/principios.md`](../docs/principios.md)): sobreescribir `AHORA.md` haría desaparecer registros sin dejar rastro en `bitacoras/`. El rechazo nombra el archivo destino con las fechas ya calculadas, para que cerrarlo sea copiar la línea.

Un ciclo abierto **sin registros sí se regenera**, porque no hay nada que perder. Y ante una fecha de otro ciclo se falla en vez de archivar solo, porque el caso frecuente es un dedazo y no el lunes nuevo: fallar es barato y deshacer un cierre no.

**Un ciclo no se abre hacia atrás.** Una fecha anterior al `from` del ciclo abierto se rechaza siempre, tenga o no registros: con `AHORA.md` en la semana del 24 de agosto, `tuku process cycle --at 2026-07-06` rechaza y nombra el ciclo abierto. Lo vivido en una semana ya cerrada se agrega a mano en su bitácora de `bitacoras/`.

## Cerrar un ciclo

En este orden:

1. Generar el resumen en `reportes/`, que necesita el plan y los registros todavía vivos → `cycle extract` lo alimenta
2. Aplanar el plan → `transclusion flatten`
3. Dejar el enlace al resumen → `cycle close`
4. Mover a `bitacoras/bitacora-DESDE-HASTA.md` y pasar el frontmatter a `status: stable` → `cycle close`
5. Dejar `AHORA.md` limpio para el ciclo siguiente → `cycle close`

**El orden importa**: aplanar antes de generar el resumen lo deja sin de dónde leer.

`status: stable` es lo que declara que el archivo dejó de tocarse. Mientras siga en `draft` es un ciclo abierto viviendo en el lugar equivocado, y eso lo reportará `tuku doctor cycle` cuando exista `bitacoras/` (epic 006); hoy solo revisa `AHORA.md`.

Idempotencia: cerrar dos veces no vuelve a mover ni a duplicar.

## Planes

Estructura del plan:

- **Intención del ciclo**: lista corta, cada punto es un ámbito y su acción principal
- **No entra, y por qué**: la razón es parte del plan, no un comentario
- **Restricciones y contexto**: lo que acota el ciclo antes de empezar
- **Señales a vigilar**: qué observar durante el ciclo sin que sea tarea

Calcular la capacidad antes de planificar → `capacity calc`:

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

**Los días que no cuentan siguen en el ciclo.** El ejemplo de arriba cuenta de lunes a viernes, pero `AHORA.md` trae un encabezado por cada fecha del rango, sábado y domingo incluidos. Un día que `Días que cuentan` no nombra no aporta capacidad al plan: se puede registrar en él, no se planifica. El plan lo trata como descanso, no como un hueco sin dueño.

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

Cerrado porque es lo que permite que el comando sume sin interpretar, y corto porque un quinto escalón obliga al autor a deliberar sobre la diferencia entre dos etiquetas parecidas, que es exactamente el trabajo que el sistema le está quitando. Las variantes de redacción (*"casi entero"*, *"casi completo"*) las normaliza el linter, igual que hace con las clasificaciones.

Lo que sale de sumar no es un número de horas: es cuánto cabe en el ciclo, en la misma escala. El plan se dimensiona contra eso.

`Cuándo` depende del ciclo, igual que el trigger de una cadencia: *"los días de turno"* no se resuelve con un almanaque, pero sí con el nombre: el ciclo que declara `cycle: turno` es el que cobra ese costo. El cálculo de capacidad hereda esa dependencia y sus dos trampas conocidas (ver [`cadencias.md`](cadencias.md)).

`Por qué` cumple aquí el mismo papel que `Historia` en una cadencia. Un costo fijo sin razón escrita es lo primero que el autor recorta cuando quiere que el ciclo le quepa, y es exactamente lo que no debe recortar.

**La capacidad no se registra en la bitácora.** Declararla es escribir una regla, no ocurrió como hecho. Cambiarla sí es una decisión y el autor puede registrarla como tal, pero eso es un registro más, no el mecanismo.

Trae al plan:

- Pendientes heredados del ciclo anterior → `todo promote`
- Cadencias que caen dentro del ciclo → `cadence resolve`
- Qué quedó abierto y sin cerrar en el ciclo anterior → `cycle extract`

El plan se propone al autor y no se escribe sin su aprobación. Mover algo a "No entra" pospone sus pendientes y silencia sus alertas de ausencia → `plan exclude`.

Registrar cuánto corrigió el autor el plan propuesto → `plan delta`. Sin correcciones también es información: dice que la propuesta estuvo bien calibrada.

## Resumen del ciclo

Al cerrar, se genera en `reportes/` y se deja solo el enlace en la bitácora → `cycle extract`.

Estructura del resumen:

- **Resumen ejecutivo**: tema dominante del ciclo, qué se logró, dónde está el foco urgente
- **Veredicto por intención**: cumplida, parcial, en riesgo o sin avance, cada una con su acción siguiente
- **Desglose por ámbito**: estado, pendientes que siguen abiertos, actividad realizada
- **Emergente**: lo que ocurrió sin estar en el plan
- **Momentum y señales**: pocos logros que cambian la trayectoria, y señales que merecen atención más allá del ciclo

El veredicto sale de comparar plan contra ejecución, no de resumir la actividad.

## No entra

- **Juzgar la calidad de la prosa** del plan o el resumen.
- **Decidir cuánto dura un ciclo que no es `semana`.** Lo dice el autor y el agente se lo pregunta al cambiar de ciclo. El estado cero arranca en `semana` y los nombres verdaderos emergen después; esa regla de arranque vive en [`../devel/epics.md`](../devel/epics.md) (estrategia de pruebas, estado cero).
