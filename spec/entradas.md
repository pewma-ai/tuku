# spec/entradas.md — Entradas y bitácoras

> Define el almacén canónico de entradas y las bitácoras como proyecciones. Reemplaza al
> modelo anterior, donde la bitácora de cada ciclo era un archivo canónico.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §3.
> Ver también [`spec/tarea.md`](tarea.md) y [`spec/artefactos-ciclo.md`](artefactos-ciclo.md).

---

## 1. Definiciones

**Entrada** — Un hecho fechado que pertenece a una entidad y lleva una clasificación. Es la
unidad de registro y una de las dos fuentes crudas del sistema. **Inmutable**: no cambia de
fecha ni de contenido; una corrección se escribe como entrada nueva.

**Bitácora** — Cualquier proyección de entradas. La *bitácora del ciclo* filtra por rango de
fechas; la *bitácora de una entidad* filtra por pertenencia. Ninguna de las dos es un
almacén: son dos vistas del mismo conjunto.

> Un hecho ocurre a la vez en un momento y sobre una entidad. Guardarlo bajo el ciclo sería
> tan arbitrario como guardarlo bajo la entidad. Se guarda una vez, por tiempo absoluto, y
> ambas dimensiones se obtienen por filtro.

---

## 2. Almacén

```
entradas/
├── 2026-08.md          # mes en curso — superficie de escritura
├── 2026-07.md
└── 2025/
    ├── 2025-12.md
    └── …
```

**Partición por mes.** El mes es una unidad de tiempo absoluta que ninguna cadencia puede
redefinir. Particionar por ciclo ataría los datos históricos a una configuración que el
usuario puede cambiar —de turnos a semanas ISO, por ejemplo— y dejaría archivos que ya no
corresponden a ningún ciclo vigente. Con volúmenes reales observados (~55 entradas en 8
días de alta intensidad) un mes queda en 150–250 líneas: cómodo en Obsidian y con diffs
limpios.

**Archivado por año.** Los meses cerrados se mueven a subdirectorio del año. Es la misma
regla que rige `tareas/`. No hay archivo mutable de entradas porque las entradas no mutan.

### 2.1 Front matter

```yaml
---
id: ent-2026-08
type: entradas
period: 2026-08
created: 2026-08-01
modified: 2026-08-04
---
```

### 2.2 Estructura interna

Encabezados por día en formato ISO más nombre del día:

```markdown
## 2026-08-04, Martes
- [sw-responsible](../entidades/trabajo/sw-responsible.md) **Hito:** Instalación validada en el ambiente de pruebas.
- (09:30) [colaboraciones](../entidades/trabajo/colaboraciones.md) Reunión por continuación de tesis.
- Compra de insumos para la casa.

## 2026-08-05, Miércoles
- …
```

La fecha ISO en el encabezado hace la entrada autodescriptiva sin repetirla en cada línea.

**Siembra de días.** La apertura de un ciclo escribe en el mes en curso los encabezados de
los días de su rango, incluidos los que quedarán vacíos. El usuario abre el archivo del mes
y encuentra sus días listos. Los encabezados son canónicos, no derivados: nada los reescribe.

Un mes puede contener días de más de un ciclo, y días que no pertenecen a ningún ciclo
declarado. Ninguna de las dos situaciones es un error.

---

## 3. Gramática de la entrada

```
- [(HH:MM)] [<entidad>](<ruta>)[ **<Clasificación>:**] <texto>
```

Todo lo que va entre corchetes en esta gramática es opcional, incluida la entidad.

Ejemplos válidos:

```markdown
- [sw-responsible](../entidades/trabajo/sw-responsible.md) Solucionado el problema de sincronía.
- (09:30) [colaboraciones](../entidades/trabajo/colaboraciones.md) Reunión con estudiantes.
- [pds](../entidades/trabajo/pds.md) **Hito:** Reporte de volumetría generado.
- **Señal:** El primer día de descanso exige desconexión total; la energía vuelve al segundo.
```

### 3.1 Referencia a entidad

Enlace Markdown estándar: el **texto** es el `id` de la entidad y es lo que el motor lee; la
**ruta** existe para que Obsidian navegue y la mantiene un janitor. Si la entidad se mueve,
se reescribe la ruta y el `id` no cambia (ADR 0001).

Una entrada **puede no tener entidad**. Ocurre de forma natural y frecuente en ciclos de
descanso, donde buena parte de lo registrado es vida personal. Queda como `sin-clasificar` y
el agente puede proponer entidad después. El sistema **no exige** clasificar al escribir:
forzarlo rompería el único momento que debe ser sin fricción.

### 3.2 Clasificación

Conjunto por defecto, extensible en `.tuku/config.yaml`:

| Clasificación | Significado |
|---|---|
| `Hito` | Cambio de estado relevante: completado, validado, entregado, escalado |
| `Decisión` | Resolución que fija rumbo |
| `Señal` | Información a considerar, sin acción inmediata |
| `msg` | Registro corriente; es el caso por defecto y no se escribe |

**No existe clasificación de fricción.** Las desviaciones no se etiquetan al escribir: se
deducen en el cierre contrastando el plan con la actividad. Sigue el uso real observado
—`Hito` 59, `Decisión` 22, `Señal` 8, fricción 0— y evita pedirle al usuario que rotule sus
propios fracasos mientras trabaja.

### 3.3 Entradas multilínea

Una entrada puede continuar en líneas indentadas: sublistas, acuerdos numerados, bloques de
código. Todo lo indentado pertenece a esa entrada y viaja con ella en las proyecciones.

---

## 4. Escritura por agente

El usuario dicta o escribe en lenguaje natural; **el agente normaliza a la forma canónica**.
Resolver "avancé en el paper" al `id` correcto es trabajo del agente usando el tesauro vivo.

La forma escrita es formal y estable; la entrada es libre. **El parser nunca interpreta
sinónimos, el agente sí.**

---

## 5. Proyecciones

Ambas bitácoras son derivaciones declaradas, con el mismo origen y distinto filtro:

```yaml
- target: "entidades/{ruta}/{entidad}.md#bitacora-entidad"
  sources: ["entradas/**/*.md"]
  filter: "entidad == {entidad}"
  build: "bitacora_entidad"

- target: "ciclos/resultados_{fecha}_{tipo}.md#bitacora-ciclo"
  sources: ["entradas/**/*.md"]
  filter: "fecha in [cycle_start, cycle_end]"
  build: "bitacora_ciclo"
```

### 5.1 Bitácora de entidad: agrupada, no cronológica

El uso real muestra que la bitácora de una entidad no se lee bien como lista cronológica.
La proyección agrupa en dos ejes —**mes** y luego **clasificación**— y omite los grupos
vacíos:

```markdown
### Julio 2026
**Hitos:**
- **2026-07-02:** Alta del proyecto de chequeo de posición.
**Decisiones:**
- **2026-07-06:** Delegar la migración de conexión a otro colega.
```

Las entradas `msg` no aparecen en esta proyección salvo que se configure lo contrario: la
página de una entidad es un resumen de lo relevante, no un volcado.

Reformular el texto para lectura continua es una regla de familia semántica (agente), no de
derivación. Sin agente disponible, la proyección se genera literal.

---

## 6. Invariantes

| # | Regla | Garante |
|---|---|---|
| E1 | Front matter válido con `type: entradas` y `period` coincidente con el nombre | janitor |
| E2 | Todo encabezado de día cae dentro del mes del archivo | janitor |
| E3 | Los días están en orden ascendente y no se repiten | janitor |
| E4 | Toda referencia de entidad resuelve a una entidad existente | janitor |
| E5 | Toda clasificación pertenece al conjunto de `config.yaml` | janitor |
| E6 | Un archivo de un mes ya archivado no se modifica | janitor |
| E7 | Toda sección de un compuesto está marcada como canónica o derivada | janitor |

### 6.1 Corrección de entradas

Una entrada escrita **no se edita para corregir un hecho**: se escribe una entrada nueva que
lo corrige, en el día en que se advierte el error. Esto preserva la auditoría y hace posible
el replay. Corregir ortografía o redacción sí es edición directa y no rompe nada.

### 6.2 Entradas retroactivas

Registrar un hecho de una fecha pasada se hace escribiéndolo bajo el día que corresponde, si
ese mes sigue abierto. Si el mes ya fue archivado, la entrada se escribe en el día actual con
mención explícita de la fecha real en el texto. **No se reabre un mes archivado.**

---

## 7. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | ¿La entrada lleva `id` propio? Hoy se identifica por archivo + día + posición. Un `id` permitiría que una tarea apunte a la entrada que la originó, a costa de ruido visual al escribir |
| 2 | Umbral y criterio para invocar reformulación semántica en la bitácora de entidad |
| 3 | Si las entradas `msg` deben aparecer en la bitácora de entidad bajo alguna condición |
