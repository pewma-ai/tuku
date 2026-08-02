# spec/cadencia.md — Cadencias

> Define la regla que produce artefactos en el tiempo: su gramática, de dónde se hereda,
> cómo dispara y cuándo muere.
> Depende de [`spec/entidad.md`](entidad.md) y [`spec/artefactos-ciclo.md`](artefactos-ciclo.md).

---

## 1. Definición

**Cadencia** — Regla declarativa que produce artefactos en el tiempo: tareas, ciclos o
alertas.

Es la pieza central del sistema y la que hace verdadera la promesa del nombre. Absorbe lo que
en otros sistemas son *rituales* cableados: **abrir y cerrar un ciclo son cadencias**,
editables y desactivables como cualquier otra regla. No hay comportamiento temporal
privilegiado en el código.

**El motor de cadencias es determinista.** Python leyendo front matter, sin red, sin API, sin
créditos. El agente **escribe** una cadencia cuando el usuario habla y la **interpreta** al
abrir un ciclo, pero nunca es quien la recuerda (P3).

---

## 2. Gramática

```yaml
- id: cad-cliente-reposicion
  descripcion: Ofrecer reposición tres meses después de una venta
  trigger:
    type: event                 # calendar | event | absence | completion
    on: venta                   # clasificación o marcador en la entrada
    delta: 3M
  emit:
    kind: tarea                 # tarea | ciclo | alerta
    text: "Contactar a {entidad} para ofrecer reposición"
    due: "+0d"
  enabled: true
```

| Campo | Obligatorio | Notas |
|---|---|---|
| `id` | sí | único en el perfil |
| `descripcion` | sí | en lenguaje natural; el agente la usa para explicar por qué existe algo |
| `trigger` | sí | §4 |
| `emit` | sí | §5 |
| `enabled` | no | `true` por defecto; desactivar no es borrar |

`descripcion` es obligatoria porque una regla que nadie puede explicar es una regla que nadie
se atreve a borrar.

---

## 3. Dónde viven y de dónde se heredan

Una cadencia se hereda por **dos vías independientes**:

**La cadena de padres** — sistema → ámbito → niveles → entidad.
Aquí caen las cadencias personales del usuario y las institucionales: "el día 1, pagar
cuentas" en `personal/`, "reunión de líderes cada mes" en `trabajo/`.

**El tipo** — ortogonal a la cadena.
Aquí caen las que describen la naturaleza de la cosa: "todo cliente se contacta a los tres
meses de una venta".

| Nivel | Archivo |
|---|---|
| Sistema | sembradas por `tuku init` en `estrategia/cadencias.md` |
| Ámbito / nivel | zona `cadencias` de la página homónima |
| Entidad | zona `cadencias` de la entidad |
| Tipo | `tipos/<ámbito>/<tipo>.md` |

Las cadencias del usuario viven en su ámbito `personal/`, no sueltas: son suyas, no del
sistema.

### 3.1 Precedencia

```
entidad  >  tipo  >  ancestro más cercano  >  …  >  ámbito  >  sistema
```

La entidad concreta gana sobre todo. El tipo gana sobre los ancestros porque describe la naturaleza de la cosa, no su ubicación. Entre ancestros, el más cercano gana.

**Cualquier nivel puede silenciar lo heredado** declarando el mismo `id` con `enabled: false`. Silenciar es explícito y visible; no hay herencia que desaparezca sin dejar rastro.

**Colector.** Antes de evaluar, un janitor combina todas las cadencias aplicables —sistema, ámbito, niveles, tipo, entidad— en un único conjunto resuelto, sobrescribiendo por `id` de cadencia según precedencia (§3.1). El resultado se cachea en `.tuku/cache/cadencias-resueltas.yaml`: no versionado, siempre reconstruible. **La autoridad última la tiene el archivo de la propia entidad**: si define una cadencia con el mismo `id` que algo heredado, gana ella, sin excepción.

### 3.2 El archivo de tipo

Las cadencias van **dentro de un comentario HTML**, no en bloque visible. Lo visible es una proyección en lenguaje natural derivada de ese comentario — mismo patrón que los metadatos de tarea, pero invertido: ahí el comentario es metadata y lo visible es la fuente; aquí el comentario **es** la fuente y lo visible es la proyección.

```markdown
---
id: cliente
type: tipo
ambito: pewma
---
# Cliente

<!-- tuku:editable id=plantilla -->
Campos sugeridos: contacto, última compra, volumen.
<!-- /tuku:editable -->

<!-- tuku:cadencias
- id: cad-cliente-reposicion
  descripcion: Ofrecer reposición tres meses después de una venta
  trigger: { type: event, on: venta, delta: 3M }
  emit: { kind: tarea, text: "Contactar a {entidad} para ofrecer reposición" }
-->
<!-- tuku:derived id=cadencias-legibles hash=a1b2c3 -->
**Cadencias de este tipo**
- Cada venta registrada dispara, tres meses después, una tarea para ofrecer reposición.
<!-- /tuku:derived -->
```

Un tipo es *plantilla de front matter + lista de cadencias*, declarado en Markdown. No hay editor de esquemas, ni validación fuerte, ni UI de configuración (P6). El usuario define tipos conversando; el agente los escribe.

Al vivir dentro de un ámbito, un tipo es **autocontenido y compartible**: otro perfil puede instalar el tipo `cliente` sin importar nada más.

---

## 4. Formas de disparo

### 4.1 Absoluta (`calendar`)

Función del calendario.

```yaml
trigger: { type: calendar, rule: "monthly:1" }
trigger: { type: calendar, rule: "yearly:04-30" }
trigger: { type: calendar, rule: "every:14d", from: 2026-03-04 }
```

Es la que produce el momento de mayor valor del producto: abrir el ciclo y encontrar lo que se había olvidado.

### 4.2 Relativa a evento (`event`)

Se dispara por algo registrado en una entidad, más un desfase.

```yaml
trigger: { type: event, on: venta, delta: 3M }
```

`on` referencia un **marcador** (`spec/entradas.md` §3.4), no una clasificación. Es lo que permite que la cadencia dispare con esta conversación individual específica y no con cualquier Hito de la entidad.

### 4.3 Por ausencia (`absence`)

Se dispara porque **no** pasó nada.

```yaml
trigger: { type: absence, window: 4w }
emit:   { kind: alerta, text: "Sin actividad en más de {window}" }
```

Barata de calcular: el índice de entradas por entidad ya da `última actividad`. Es el
complemento exacto del recordatorio: nadie recuerda lo que dejó de hacer.

**Requiere silenciador.** Dispara siempre, de forma determinista, y el `status` de la entidad
la silencia (`spec/entidad.md` §5). Si no distinguiera entre pausa deliberada, bloqueo
externo y abandono real, produciría ruido semanal, el usuario aprendería a ignorar el bloque
completo, y ahí muere la confianza en el sistema entero.

### 4.4 Por completitud (`completion`)

Se dispara al cerrarse una tarea.

```yaml
trigger: { type: completion, task_matches: "entrega informe" }
```

Es la forma general de lo que `blocks` hace tarea-a-tarea (`spec/tarea.md` §5).

---

## 5. Qué se emite

| `kind` | Produce | Notas |
|---|---|---|
| `tarea` | entrada en `tareas/tareas.md` | con `origin=<id de la cadencia>` |
| `ciclo` | archivo `plan_*` sembrado | es como se generan los ciclos regulares |
| `alerta` | zona derivada en la página del nivel | efímera: desaparece cuando la condición cesa |
| `proceso` | instancia de un proceso sobre una entidad | emite el grupo completo de tareas (`spec/proceso.md`) |

**Notificación (`notify`).** `emit` acepta `notify: window | immediate`. Con `window` (por defecto), la notificación se difiere hasta la próxima franja declarada en `estrategia/capacidad.md` (`notify_window`). **La emisión de la tarea o proceso es inmediata siempre**; lo que se difiere es el aviso. Una tarea nunca se retrasa por una preferencia de notificación.

Diferencia importante: **tarea, proceso y ciclo son objetos canónicos que persisten; la alerta es derivada.** Una alerta no se completa ni se arrastra — se apaga sola cuando deja de aplicar.

### 5.1 Emisión de ciclos

```yaml
- id: cad-ciclo-turno
  trigger: { type: calendar, rule: "every:14d", from: 2026-03-03 }
  emit:
    kind: ciclo
    cycle_type: turno
    duration: 8d
```

La cadencia **propone** el ciclo y siembra su `plan_*`; el archivo de plan es la verdad
(`spec/artefactos-ciclo.md` §2.2). Si el usuario declara un ciclo excepcional a mano, ese
plan existe igual y las fechas relativas se re-resuelven contra él. **Romper la cadencia es
el mecanismo normal, no una excepción.**

### 5.2 Idempotencia

Una cadencia **no emite dos veces el mismo artefacto**. El motor registra el último disparo
por `id` de cadencia y ocurrencia, de modo que evaluar el mismo estado dos veces produce el
mismo resultado. Esto es lo que permite que el cron corra tan seguido como haga falta sin
duplicar nada.

---

## 6. Evaluación

**Cuándo se evalúa:**

- Al abrir un ciclo.
- En cada corrida del cron (`docs/arquitectura.md` §8).
- Tras un cambio que afecte sus fuentes, sobre el diff.

Sin el lazo periódico, las cadencias solo se evaluarían cuando el usuario aparece y el
sistema perdería su carácter proactivo — que es justamente lo que promete el nombre.

**Control de encadenamientos.** Las formas `event` y `completion` permiten cadenas. Aplican
dos límites, validados al arrancar y en ejecución:

- El grafo de cadencias encadenadas debe ser **acíclico**.
- Profundidad máxima de encadenamiento por evaluación (`max_chain_depth`, por defecto 5).

---

## 7. Ciclo de vida

| Evento | Qué ocurre |
|---|---|
| Se desactiva (`enabled: false`) | Deja de emitir. Nada de lo emitido cambia |
| Se borra | Igual, y se pierde la explicación del origen |
| Se archiva la entidad portadora | Sus cadencias se **pausan**; al reactivarla vuelven a emitir |
| Se borra la entidad portadora | Sus cadencias mueren |
| Se borra el tipo | Sus cadencias mueren. Las entidades de ese tipo siguen siendo válidas: `type` es string libre y solo pierden lo heredado |
| Se renombra el tipo | Las entidades apuntan a un tipo inexistente. El janitor lo detecta y **ofrece** reasignación masiva; no la hace solo |

### 7.1 La regla muere, lo emitido no

**Una cadencia es una regla y tiene el ciclo de vida de su portador. Una tarea emitida es un
objeto canónico independiente y sobrevive siempre.**

Si borrar un tipo borrara las tareas que sus cadencias generaron, borrar un tipo eliminaría
compromisos pendientes en silencio. En un sistema cuya promesa es recordar, ese es el peor
fallo posible.

Por eso `origin` es una referencia **blanda**: un `origin` colgante no viola ninguna
invariante. La tarea sigue siendo válida; el motor solo pierde la capacidad de explicar por
qué existe.

### 7.2 No se recuperan disparos perdidos

Al reactivar una entidad o una cadencia, se emite desde ese momento hacia adelante. No se
reconstruyen los disparos del período inactivo: una avalancha de tareas retroactivas es peor
que su ausencia.

---

## 8. Cadencias de sistema

`tuku init` siembra un conjunto mínimo, editable y desactivable. Resuelve parte del problema
del primer día —un perfil vacío ya tiene comportamiento— sin cerrar nada.

| Cadencia | Qué hace |
|---|---|
| `cad-ciclo` | Define y siembra el ciclo del usuario. Semanal por defecto |
| `cad-cierre` | Cierra el ciclo al llegar su última fecha |
| `cad-archivo` | Archiva tareas cerradas y meses de entradas vencidos |
| `cad-ausencia` | Ausencia genérica sobre entidades vigentes, ventana amplia |
| `cad-arrastre` | Alerta sobre tareas que superan el umbral de ciclos |

---

## 9. Invariantes

| # | Regla | Garante |
|---|---|---|
| K1 | `id` de cadencia único en el perfil | janitor |
| K2 | `trigger.type` pertenece a las cuatro formas de §4 | janitor |
| K3 | El grafo de encadenamientos es acíclico | janitor, al arrancar |
| K4 | Una cadencia no emite dos veces la misma ocurrencia | motor |
| K5 | Una cadencia de entidad archivada no emite | janitor |
| K6 | Toda cadencia tiene `descripcion` no vacía | janitor |
| K7 | Un `origin` colgante **no** es violación | — |
| K8 | La emisión de tareas y ciclos es determinista y reproducible | test de replay |
| K9 | El colector resuelve precedencia por sobrescritura simple sobre `id`; la entidad tiene la última palabra | janitor |

---

## 10. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | Sintaxis exacta de `rule` en disparos de calendario: ¿subconjunto propio o cron extendido? |
| 2 | Si una alerta puede escalar a tarea automáticamente tras N ciclos sin atención |
