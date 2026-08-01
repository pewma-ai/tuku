# spec/tarea.md — Tareas

> Define el backlog canónico, la gramática de una tarea y su ciclo de vida.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §3 y §6.
> Ver también [`spec/bitacora.md`](bitacora.md) y [`spec/cadencia.md`](cadencia.md).

---

## 1. Definición

**Tarea** — Compromiso de acción con estado, pertenencia a una entidad y temporalidad. Nace
de una entidad y se ejecuta dentro de un ciclo: es el segundo punto de cruce entre los ejes
del sistema.

**Las tareas se escriben en un solo lugar.** Toda aparición en una bitácora o en una página
de entidad es proyección. Esto corrige el fallo estructural del sistema anterior, donde una
tarea vivía duplicada en varias bitácoras y se copiaba a mano.

---

## 2. Los archivos

```
tareas/
├── abiertas.md        # mutable, pequeño
└── tareas-2026.md     # completadas del año, inmutable
```

Una tarea completada permanece en `abiertas.md` durante un período configurable
(`task_archive_delay`, por defecto 7 días) y luego se mueve al archivo del año de su
completitud. El conjunto mutable se mantiene pequeño: importa para los diffs de Git, para la
velocidad de los janitors y para los merges.

Front matter de ambos archivos:

```yaml
---
id: tareas-abiertas          # o tareas-2026
type: tareas
created: 2026-03-01
modified: 2026-08-01
---
```

---

## 3. Gramática

Una tarea ocupa una línea, opcionalmente seguida de líneas de detalle indentadas:

```
- [ ] [(<fecha>)] [<entidad>](<ruta>) <texto> ^<id>
      <!-- tuku: created=… cycles=… deps=… blocks=… -->
      > <descripción extendida>
```

Ejemplo:

```markdown
- [ ] (2026-08-11) [deputy](../entidades/VIGENTES/deputy.md) Asistir a e-Connect training en Vitacura ^t-2026-0143
      <!-- tuku: created=2026-07-20 cycles=1 -->
- [ ] (next:descanso) [colaboraciones](../entidades/VIGENTES/colaboraciones.md) Enviar correo de postulación conjunta ^t-2026-0087
      <!-- tuku: created=2026-05-13 cycles=6 deps=t-2026-0090 -->
      > Requiere acuerdo previo sobre autoría y reparto de horas.
```

### 3.1 Reparto de propiedad por línea

| Parte | Quién la escribe |
|---|---|
| Línea de la tarea | humano o agente |
| Comentario `<!-- tuku: … -->` | **janitor**, nunca a mano |
| Cita `>` de descripción extendida | agente o humano |

El comentario HTML es invisible en Obsidian y en cualquier renderizador, de modo que la
lista se lee limpia mientras el motor conserva la trazabilidad. Es la aplicación literal de
"un archivo, un dueño" a nivel de línea.

### 3.2 Por qué línea y no tabla

Una tabla Markdown se lee bien pero se edita mal a mano, produce diffs ruidosos por
realineación de columnas y rompe el hábito de escribir una tarea como una viñeta. **La tabla
sigue existiendo: como proyección**, en la página de entidad o en la interfaz. Canónico ≠
vista, también aquí.

### 3.3 Identidad

`^t-YYYY-NNNN` al final de la línea. Es un *block id* nativo de Obsidian, así que sirve como
ancla de enlace real, y a la vez es el `id` estable de la tarea (ADR 0001). Lo asigna el
motor en el alta; no cambia nunca, ni al mover la tarea al archivo del año.

### 3.4 Estado

| Marca | Estado |
|---|---|
| `- [ ]` | abierta |
| `- [x]` | completada |

Al completarse, el janitor agrega `completed=` al comentario. No hay estado "en curso": si
hace falta expresarlo, es una entrada de bitácora, no un estado de tarea.

Una tarea **cancelada** se marca `- [x]` con `cancelled=true` en el comentario y una razón
en la descripción extendida. Cancelar no es completar, y el cierre de ciclo debe poder
distinguirlas.

---

## 4. Gramática temporal

Cuatro modalidades. La cuarta es la más usada en la práctica y la que más exige del motor.

| Modalidad | Forma canónica | Ejemplos de entrada |
|---|---|---|
| **Precisa** | `(2026-08-11)` · `(2026-08-11 12:45)` | "11 ago", "el 11 a las 12:45" |
| **Rango** | `(2026-08-11/2026-08-14)` | "del 11 al 14 de agosto" |
| **Difusa** | `(~2026-08)` · `(~2s)` | "en agosto", "en dos semanas" |
| **Relativa a ciclo** | `(next:turno)` · `(next:descanso)` · `(next)` | "próximo turno", "siguiente descanso" |
| **Sin fecha** | se omite el paréntesis | |

### 4.1 Relativa a ciclo

`(next:<tipo>)` resuelve al **próximo ciclo de ese tipo** según el calendario que producen
las cadencias. Requiere que el motor sepa proyectar ciclos futuros, no solo generar el
actual: es una capacidad del motor de cadencias, no azúcar sintáctico.

`(next)` sin tipo significa el próximo ciclo, sea cual sea.

Esta modalidad domina el uso real —32 postergaciones a "próximo/siguiente turno" y 6 a
"siguiente descanso" frente a unas 30 fechas absolutas repartidas— porque corresponde a cómo
se piensa el trabajo cuando la vida se organiza por ciclos y no por calendario.

### 4.2 Difusa

Una fecha difusa **no se compara contra `today`**: se reevalúa. El motor la considera
vigente para el ciclo actual cuando el ciclo intersecta su ventana, y la marca para
reevaluación cuando la ventana se agota sin que la tarea se cierre.

### 4.3 Sinónimos

El parser **no interpreta sinónimos**. "Próximo turno", "siguiente turno" y "el turno que
viene" son entradas equivalentes que el **agente** normaliza a `(next:turno)` al escribir.
La forma escrita es formal; la forma hablada es libre.

---

## 5. Relaciones

| Campo | Significado |
|---|---|
| `deps=t-…,t-…` | esta tarea está bloqueada hasta que aquellas se completen |
| `blocks=t-…` | al completarse **esta**, se activan aquellas |

El grafo resultante debe ser **acíclico**; se valida al arrancar, igual que el grafo de
derivaciones. Una tarea con `deps` sin resolver no se propone en el plan del ciclo, pero sí
aparece en la vista de bloqueadas.

`blocks` es la forma tarea-a-tarea del disparo por completitud; su forma general
—completar una tarea activa una **cadencia**— se especifica en `spec/cadencia.md`.

---

## 6. Arrastre

`cycles=N` cuenta cuántos ciclos ha atravesado la tarea sin cerrarse. Lo incrementa el
janitor en cada apertura de ciclo y **se muestra en las proyecciones** a partir de un umbral
configurable (`carryover_warn`, por defecto 3), con un marcador visible: `⟳6`.

Esto no es estadística: es el mecanismo que impide que una tarea eternamente postergada
desaparezca sin ser confrontada. En el corpus real hay una tarea que atravesó seis ciclos y
terminó reapareciendo como "señal estratégica" en vez de como pendiente incumplido. Un
contador visible hace imposible esa fuga.

`cycles` es también insumo directo de la sección Desviaciones del informe de cierre.

---

## 7. Ciclo de vida

```
alta ──► abierta ──► completada ──► archivada (tareas-YYYY.md)
                └──► cancelada ──► archivada
```

| Momento | Qué ocurre |
|---|---|
| **Alta** | El motor asigna `id` y `created`. La entidad es obligatoria salvo que quede `sin-clasificar` |
| **Apertura de ciclo** | Se incrementa `cycles` de las abiertas; las vigentes se proyectan al ciclo |
| **Completitud** | Se marca `- [x]`, se agrega `completed=`; se activan las tareas de `blocks` |
| **Archivado** | Tras `task_archive_delay`, se mueve al archivo del año conservando su `id` |

**Dónde se marca completada.** En el archivo canónico, o en cualquier proyección: si el
usuario marca `- [x]` en el bloque renderizado de la bitácora, el janitor recoge la marca,
la propaga al canónico y regenera la proyección. La escritura es natural; la consistencia es
mecánica.

---

## 8. Proyecciones

| Proyección | Filtro |
|---|---|
| Tareas del ciclo, en la bitácora | vigentes para `[cycle_start, cycle_end]` |
| Tareas de la entidad, en su página | `entidad == {entidad}` y abiertas |
| Postergadas | fecha posterior al ciclo actual |
| Bloqueadas | `deps` sin resolver |

Todas son derivadas: regenerables, idempotentes, borrables sin pérdida.

---

## 9. Invariantes

| # | Regla | Garante |
|---|---|---|
| T1 | Todo `id` es único en el perfil y no se reutiliza | janitor |
| T2 | Toda tarea abierta tiene entidad, o está marcada `sin-clasificar` | janitor |
| T3 | Toda referencia de entidad resuelve | janitor |
| T4 | El grafo de `deps`/`blocks` es acíclico | janitor, al arrancar |
| T5 | Una tarea completada tiene `completed=` con fecha ≥ `created` | janitor |
| T6 | Ninguna tarea aparece en dos archivos canónicos a la vez | janitor |
| T7 | El estado en las proyecciones coincide con el canónico | janitor de build |
| T8 | Una fecha canónica pertenece a una de las modalidades de §4 | janitor |

---

## 10. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | `effortTime` por tarea y su estimación aprendida del historial. Diferida hasta tener experiencia de uso; sin ella el cruce con capacidad es cualitativo |
| 2 | Si la tarea puede apuntar a la entrada de bitácora que la originó (depende de la decisión abierta 1 de `spec/bitacora.md`) |
| 3 | Umbral y forma de presentación del arrastre: si `⟳6` basta o hace falta escalarlo a una alerta |
