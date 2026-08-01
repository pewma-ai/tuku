# spec/bitacora.md — Bitácora y entradas

> Define el archivo de bitácora de un ciclo y la gramática de sus entradas.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §3 y §7.
> Ver también [`spec/tarea.md`](tarea.md) y [`spec/artefactos-ciclo.md`](artefactos-ciclo.md).

---

## 1. Definiciones

**Entrada** — Un hecho fechado que pertenece a una entidad y lleva una clasificación. Es la
unidad de registro. **Inmutable**: una entrada nunca cambia de fecha ni de contenido; una
corrección se escribe como entrada nueva.

**Bitácora** — El archivo de un ciclo donde se escriben las entradas de cada día. Es
**canónico** para sus entradas: es el único lugar donde se escriben. La bitácora de una
entidad no es un archivo: es una proyección de estas entradas filtrada por pertenencia.

---

## 2. El archivo

### 2.1 Nombre

```
ciclos/bitacora_YYYY-MM-DD_<tipo>.md
```

`YYYY-MM-DD` es el primer día del ciclo. `<tipo>` es el tipo de ciclo declarado en la
cadencia que lo generó (`turno`, `descanso`, `semana`, `sprint`…), en minúsculas y sin
espacios. Ejemplos reales: `bitacora_2026-06-30_turno.md`, `bitacora_2026-06-17_descanso.md`.

### 2.2 Front matter

```yaml
---
id: bit-2026-06-30-turno      # estable, independiente del path
type: bitacora
created: 2026-06-30
modified: 2026-07-07
cycle_type: turno
cycle_start: 2026-06-30
cycle_end: 2026-07-07
status: open                  # open | closed
---
```

`status: closed` lo escribe el cierre de ciclo. Una bitácora cerrada es inmutable: los
janitors no la reescriben y el motor rechaza entradas nuevas con fecha dentro de ella
(§6.2).

### 2.3 Estructura

La bitácora contiene **una sola zona canónica** y las derivadas que se declaren:

```markdown
<!-- tuku:derived id=tareas-del-ciclo hash=… -->
…renderizado de las tareas vigentes del ciclo…
<!-- /tuku:derived -->

# Actividad diaria

## Martes 30 de Junio
- …entradas…

## Miércoles 1 de Julio
- …entradas…
```

- `# Actividad diaria` y sus subsecciones por día son **canónicas**. El usuario escribe
  aquí; ningún janitor las reescribe.
- Todo lo demás es derivado y va marcado según `spec/perfil.md`. El bloque de tareas se
  renderiza aquí por conveniencia y es **borrable sin pérdida**.
- El plan y la retrospectiva **no viven en este archivo**: son `plan_*` y `resultados_*`
  (un archivo, un dueño).

### 2.4 Encabezado de día

```
## <Día de la semana> <D> de <Mes>
```

En español, con inicial mayúscula, sin año. El motor lo resuelve contra `cycle_start`. Los
días se siembran completos en la apertura del ciclo, incluidos los que quedarán vacíos.

---

## 3. Gramática de la entrada

```
- [(HH:MM)] [<entidad>](<ruta>)[ **<Clasificación>:**] <texto>
```

Todo entre corchetes cuadrados en esta gramática es opcional salvo el enlace de entidad.

Ejemplos válidos:

```markdown
- [sw-responsible](../entidades/VIGENTES/sw-responsible.md) Solucionado problema con Delirium en el VLTI.
- (09:30) [colaboraciones](../entidades/VIGENTES/colaboraciones.md) Reunión con estudiantes por continuación de tesis.
- [pds](../entidades/VIGENTES/pds.md) **Hito:** Conexión exitosa a Elasticsearch y reporte de volumetría generado.
- **Señal:** El primer día de descanso exige desconexión total; la energía intelectual vuelve el segundo día.
```

### 3.1 Referencia a entidad

Es un enlace Markdown estándar: el **texto** es el `id` de la entidad y es lo que el motor
lee; la **ruta** existe para que Obsidian navegue y la mantiene un janitor. Si la entidad se
mueve, se reescribe la ruta y el `id` no cambia (ADR 0001).

Una entrada **puede no tener entidad**. Ocurre de forma natural y frecuente en ciclos de
descanso, donde buena parte de lo registrado es vida personal. Esas entradas quedan como
`sin-clasificar` y el agente puede proponer entidad después; el sistema **no exige** una
decisión de clasificación en el momento de escribir. Forzarla rompería el único momento del
sistema que debe ser sin fricción.

### 3.2 Clasificación

Conjunto por defecto, extensible en `.tuku/config.yaml`:

| Clasificación | Significado |
|---|---|
| `Hito` | Cambio de estado relevante: completado, validado, entregado, escalado |
| `Decisión` | Resolución que fija rumbo |
| `Señal` | Información a considerar, sin acción inmediata |
| `msg` | Registro corriente, sin clasificar (es el caso por defecto y no se escribe) |

**No existe una clasificación de fricción.** Las desviaciones no se etiquetan al escribir:
se deducen en el cierre contrastando el plan con la actividad. Esta decisión sigue el uso
real observado —`Hito` 59 apariciones, `Decisión` 22, `Señal` 8, fricción 0— y evita pedirle
al usuario que rotule sus propios fracasos mientras trabaja.

La clasificación se escribe en negrita y con dos puntos, tal como ya se usa. Es el único
adorno tipográfico con significado.

### 3.3 Entradas multilínea

Una entrada puede continuar en líneas indentadas (sublistas, acuerdos numerados, bloques de
código). Todo lo indentado bajo una entrada pertenece a esa entrada y viaja con ella en las
proyecciones.

---

## 4. Escritura por agente

El usuario dicta o escribe en lenguaje natural; **el agente normaliza a la forma canónica**.
Resolver "avancé en ELIANA" al `id` correcto es trabajo del agente usando el tesauro vivo.

La forma escrita es formal y estable; la entrada es libre. Esta separación aplica a todo el
sistema: **el parser nunca interpreta sinónimos, el agente sí.**

---

## 5. Proyección a entidades

La sección de bitácora de una entidad se genera filtrando todas las entradas cuya
referencia de entidad coincida, ordenadas cronológicamente. Se declara en el grafo de
derivaciones:

```yaml
- target: "entidades/VIGENTES/{entidad}.md#bitacora-entidad"
  sources: ["ciclos/bitacora_*.md"]
  filter: "entidad == {entidad}"
  build: "proyeccion_entidad"
```

La proyección conserva fecha, clasificación y contenido, y **no** duplica la entrada: es
recomputable y borrable sin pérdida. Reformular el texto para lectura continua es una regla
de familia semántica (agente), no de derivación; si no hay agente disponible, la proyección
se genera literal.

---

## 6. Invariantes

| # | Regla | Garante |
|---|---|---|
| B1 | El front matter es válido y `type: bitacora` | janitor |
| B2 | `cycle_start` coincide con la fecha del nombre de archivo | janitor |
| B3 | Todo encabezado de día cae dentro de `[cycle_start, cycle_end]` | janitor |
| B4 | Toda referencia de entidad resuelve a una entidad existente | janitor |
| B5 | Toda clasificación pertenece al conjunto declarado en `config.yaml` | janitor |
| B6 | Una bitácora con `status: closed` no se modifica | janitor |
| B7 | Toda sección está marcada como canónica o derivada; no hay ambigüedad | janitor |

### 6.1 Corrección de entradas

Una entrada escrita no se edita para corregir un hecho: se escribe una entrada nueva que lo
corrige, en el día en que se advierte el error. Esto preserva la auditoría y hace posible el
replay. Corregir **ortografía o redacción** sí es edición directa y no rompe nada.

### 6.2 Entradas fuera de ciclo

Si se registra un hecho cuya fecha cae en un ciclo ya cerrado, la entrada se escribe en el
ciclo **abierto**, con mención explícita de la fecha real en el texto. No se reabre una
bitácora cerrada.

---

## 7. Ejemplo completo

```markdown
---
id: bit-2026-06-30-turno
type: bitacora
created: 2026-06-30
modified: 2026-07-07
cycle_type: turno
cycle_start: 2026-06-30
cycle_end: 2026-07-07
status: closed
---

<!-- tuku:derived id=tareas-del-ciclo hash=8f3a1c -->
**Tareas de este ciclo** · 2 vigentes
- [ ] (2026-07-08) [deputy](…) Asistir a e-Connect training en Vitacura `^t-2026-0143`
- [ ] (next:descanso) [colaboraciones](…) Enviar correo de postulación conjunta `^t-2026-0087` ⟳6
<!-- /tuku:derived -->

# Actividad diaria

## Martes 30 de Junio
- Inicio de turno. Subida al cerro.
- [deputy](../entidades/VIGENTES/deputy.md) Handover con el deputy saliente.
- [sw-responsible](../entidades/VIGENTES/sw-responsible.md) Handover sobre el instrumento interferométrico.
- [tesis-estudiante](../entidades/VIGENTES/tesis-estudiante.md) **Señal:** Tesis en riesgo por falta de contacto del tutor externo; evaluar plan B.

## Miércoles 1 de Julio
- (09:00) [coe](../entidades/VIGENTES/coe.md) Emergencia por fuga de nitrógeno.
- [pds](../entidades/VIGENTES/pds.md) **Hito:** Reporte de volumetría de índices generado.
- Compra de insumos para la casa.
```

---

## 8. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | ¿La entrada lleva `id` propio? Hoy se identifica por archivo + posición. Un `id` permitiría que una tarea apunte a la entrada que la originó, a costa de ruido visual en la escritura |
| 2 | Reformulación semántica de las proyecciones de entidad: cuándo se invoca al agente y con qué criterio de aceptación |
