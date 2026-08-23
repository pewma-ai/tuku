# spec/nota.md — Notas

> Define la primitiva del eje deliberativo: qué es una nota, cómo se clasifica, cómo se
> enlaza y cómo se indexa.
> Depende de [`docs/arquitectura.md`](../docs/arquitectura.md) §3 y [`spec/entidad.md`](entidad.md).
> Ver también [`spec/entradas.md`](entradas.md) y [`spec/frontmatter.md`](frontmatter.md).

---

## 1. Definición

**Nota** — Documento del eje deliberativo: una idea desarrollada o una conclusión
sedimentada. Responde **por qué así**, mientras la entrada responde *qué pasó* y la tarea
*qué falta*.

No es temporal —no pertenece a un ciclo— y **puede** pertenecer a una entidad sin estar
obligada a ello. Es el único artefacto del sistema que se justifica por su contenido y no por
su posición en el tiempo o en la jerarquía.

**La destilación ocurre al escribir.** No hay ritual de destilación, ni bandeja de entrada,
ni revisión periódica obligatoria: una nota se escribe cuando hay algo que vale la pena
sedimentar, y su calidad es responsabilidad de quien la escribe.

### 1.1 Qué la distingue de una entrada

Una entrada es un **hecho fechado e inmutable**; una nota es un **contenido en desarrollo y
mutable**. Corregir una entrada exige escribir otra (`spec/entradas.md` §6.1); corregir una
nota es editarla. Esa diferencia es la razón de que sean dos primitivas y no una.

### 1.2 Por qué existe como spec

El eje deliberativo tenía volumen real en el sistema predecesor —181 notas, ontología propia,
janitor de índice y reglas de enlace— antes de tener especificación. Esta spec **transcribe
una práctica probada**; no inventa un formato.

---

## 2. El almacén

```
notas/
├── notas.md                    # índice — derivado, nunca editado a mano
├── curva-del-dolor.md
├── manual-para-zettelkasten.md
└── ARCHIVADO/
    └── borrador-paper-v2.md
```

**Plano, sin jerarquía.** Las notas no se organizan por carpetas: se organizan por `topic`,
por pertenencia a entidad y por enlaces entre ellas. Una jerarquía de directorios obligaría a
elegir un solo eje de clasificación, y el valor de una nota suele estar justamente en que
cruza varios.

`ARCHIVADO/` es la excepción y existe para sacar del índice activo lo que ya no se consulta
sin borrarlo. Es un directorio, no un `lifecycle`, porque a diferencia de una entidad una nota
archivada no tiene proyecciones ni cadencias que dependan de su estado.

---

## 3. Front matter

```yaml
---
id: curva-del-dolor
type: nota
topic: concepto              # string libre, indexado (§3.2)
entidad: sw-responsible      # opcional; id de entidad, no ruta
summary: "Métrica de fricción operativa que gatilla la automatización."
created: 2026-04-22
modified: 2026-06-11
---
```

| Campo | Obligatorio | Notas |
|---|---|---|
| `id` | sí | estable, único en el perfil (ADR 0001) |
| `type` | sí | siempre `nota` |
| `topic` | no | string libre; categoría temática |
| `entidad` | no | `id` de una entidad; ausente si es transversal |
| `summary` | **sí** | ver §3.1 |
| `created` / `modified` | sí | ISO |

**`entidad` se declara, no se deriva.** Es la diferencia con el resto del sistema, donde el
path lleva la jerarquía (`spec/entidad.md` §2.3): como `notas/` es plano, no hay path del que
derivar. Se declara un solo valor: una nota que sirve a tres entidades no pertenece a
ninguna — es transversal, y omitir el campo es la respuesta correcta.

### 3.1 `summary` es obligatorio

Una línea que **agrega contexto no implícito en el título**. Máximo 10 palabras.

| | Ejemplo |
|---|---|
| ✅ | `[Teoría de sistemas de Kahneman]` → `"Análisis del modelo rápido/lento aplicado a la gestión."` |
| ❌ | `[Teoría de sistemas de Kahneman]` → `"Nota sobre la teoría de sistemas de Kahneman."` |

El antipatrón es siempre el mismo: reformular el título. Un `summary` que repite el título
ocupa espacio en el índice sin aportar información, y hace que el índice deje de servir para
decidir qué abrir.

**Un stub —menos de 10 líneas de contenido— lleva `summary: ""`.** El vacío es un estado
válido y declarado, no un olvido: dice "esta nota existe como ancla de enlace, todavía no
tiene contenido". Distinguirlo de un olvido es lo que permite al janitor reportar summaries
faltantes sin ruido.

**Por qué es obligatorio.** Es el mismo argumento del brief §3.5 aplicado al eje
deliberativo: un corpus de notas solo es consultable si se puede decidir qué leer sin leerlo.
El `summary` es a la nota lo que el informe de cierre es al ciclo — la superficie por la que
un humano o un agente encuentra lo que busca.

### 3.2 `topic` es string libre, indexado

`topic` no se valida contra un catálogo cerrado (P6). El janitor de índice **deriva** los
valores en uso y los agrupa; el agente, al escribir una nota nueva, prefiere un `topic`
existente y propone uno nuevo solo cuando ninguno encaja.

> **Cambio deliberado respecto del sistema predecesor**, donde `topic` era whitelist estricta
> ("NEVER invent values"). Esa regla resolvía un problema real —evitar que el agente
> multiplicara categorías sinónimas— pero lo resolvía prohibiendo, y P6 no admite catálogos
> cerrados. La solución equivalente sin violar el principio: **el índice hace visibles los
> valores en uso**, y lo visible se reutiliza solo. Si aun así proliferan sinónimos, es un
> problema de sembrado del agente (P4), no de validación.

---

## 4. Estructura del cuerpo

```markdown
---
…front matter…
---
# Curva del Dolor

Cuerpo libre. Sin estructura impuesta: prosa, listas, tablas, diagramas.

----
## Ver Además

* [MaC](mac.md) — para ubicar el marco de trabajo que la origina.
* [Agente IA](agente-ia.md) — para entender la delegación mecánica que la reduce.
```

Fuera de `## Ver Además`, **el cuerpo no tiene estructura obligatoria**. Es el artefacto más
libre del sistema, y debe seguir siéndolo: imponerle secciones sería convertir el pensamiento
en formulario.

### 4.1 `## Ver Además` — el enlace lleva su razón

Notas de más de 10 líneas llevan al final una sección `## Ver Además`, precedida de `----`,
con **hasta 5 enlaces**:

```
* [<título>](<ruta>) — para <verbo> <razón>.
```

La frase debe responder una pregunta concreta: **"¿por qué haría clic el lector de *esta*
nota?"**. Empieza con `para` + verbo.

| | Ejemplo |
|---|---|
| ✅ | `* [LLM OS](llm-os.md) — para entender la arquitectura base.` |
| ❌ | `* [LLM OS](llm-os.md) — paradigma operativo del procesador.` |

El caso incorrecto describe el *destino*; el correcto describe el *viaje*. Es la diferencia
entre un grafo y una guía: un enlace sin razón es topología, y la topología se puede calcular
sola; la razón es información que solo tiene quien escribió la nota.

El límite de cinco es deliberado. Una nota que enlaza a quince no está relacionada con quince
cosas: está mal delimitada.

### 4.2 Enlaces: Markdown estándar

Se usa `[texto](ruta.md)`. **No se usan wikilinks `[[…]]`** salvo dentro de bloques de
código, por la misma razón que rige todo el sistema: el perfil debe ser legible en cualquier
renderizador, no solo en Obsidian (P1).

> El sistema predecesor declaraba esta misma regla y aun así acumuló 135 wikilinks: la regla
> existía pero nada la verificaba. Aquí la garantiza un janitor (O5), que es la diferencia
> entre una convención y un invariante.

---

## 5. El índice

`notas/notas.md` es **derivado puro**: se regenera desde el front matter de las notas y no se
edita nunca a mano.

```markdown
---
id: notas-indice
type: indice
summary: "Índice maestro de notas del perfil."
---
<!-- tuku:derived id=indice-notas hash=… -->
**Últimas 20 modificadas:** [Curva del Dolor](curva-del-dolor.md), …

## concepto
- [Curva del Dolor](curva-del-dolor.md)
  Métrica de fricción operativa que gatilla la automatización. — *2026-04-22*

## Sin topic
- …
<!-- /tuku:derived -->
```

- Agrupado por `topic`, más un grupo `Sin topic` al final.
- Cada entrada muestra título, `summary` y `created`.
- Encabezado con las últimas modificadas: es la vista más usada en la práctica.

Se declara como cualquier otra derivación (`docs/arquitectura.md` §4):

```yaml
- target: "notas/notas.md#indice-notas"
  sources: ["notas/*.md"]
  build: "indice_notas"
```

**El janitor hace el trabajo mecánico; el agente infiere el `summary`.** Esa división —
heredada literalmente del sistema predecesor, donde se descubrió usándolo — es P3 aplicado al
eje deliberativo: agrupar, ordenar y detectar faltantes es determinista y barato; redactar una
línea que capture el sentido de un documento es juicio y cuesta.

El janitor reporta las notas sin `summary` en vez de inventarlo. Sin agente disponible, el
índice se genera igual, con esas notas marcadas.

---

## 6. Proyección en la entidad

Una nota con `entidad` aparece en la página de esa entidad como zona derivada
`notas-entidad`: título y `summary`, nada más.

```yaml
- target: "entidades/{ruta}/{entidad}.md#notas-entidad"
  sources: ["notas/*.md"]
  filter: "entidad == {entidad}"
  build: "notas_entidad"
```

Es la única relación entre el eje deliberativo y el organizacional, y es **de una sola
dirección**: la nota declara su entidad; la entidad no lista sus notas de forma canónica.
Nada se copia; todo se proyecta.

---

## 7. Ciclo de vida

| Evento | Qué ocurre |
|---|---|
| **Alta** | Se asigna `id`, `created`, `summary` (vacío si es stub) |
| **Edición** | Directa. Se actualiza `modified` y se regenera el índice |
| **Stub** | Nota creada como ancla de enlace, con `summary: ""`. Es un estado válido, no un pendiente |
| **Archivar** | Se mueve a `notas/ARCHIVADO/`. Sale del índice activo; los enlaces se reescriben |
| **Eliminar** | Los enlaces entrantes quedan colgantes y el janitor los reporta (O4) |

**Una nota no expira ni arrastra.** No tiene `status`, no la tocan las cadencias, no aparece
en el cierre de ciclo. Es el artefacto más inerte del sistema, y eso es deliberado: el eje
deliberativo no tiene ritmo propio.

### 7.1 Los stubs son parte del método

Un stub —nota que existe solo para que un enlace resuelva— es legítimo y frecuente: en el
corpus del sistema predecesor, 37 de 181 notas pesaban menos de 1 KB. Marca un concepto que
merece existir antes de tener contenido. El sistema **no debe presionar para completarlos**:
un stub que sigue vacío un año es información válida sobre la importancia real de ese
concepto.

---

## 8. Qué NO es una nota

- **Una entrada de bitácora.** Si es un hecho fechado, es entrada (`spec/entradas.md`).
- **Una entidad.** Si necesita página, bitácora, cadencias y tareas propias, es entidad
  (`spec/entidad.md`). Si solo necesita ser leída y enlazada, es nota.
- **Un proceso.** Si describe pasos reutilizables que se instancian sobre casos, es proceso
  (`spec/proceso.md` §7).
- **Un informe.** `resultados_*` es sembrado, tiene formato fijo y audiencia declarada
  (`spec/artefactos-ciclo.md`). Una nota no tiene ninguna de las tres cosas.

---

## 9. Invariantes

| # | Regla | Garante |
|---|---|---|
| O1 | Front matter válido con `type: nota` y los campos obligatorios de §3 | janitor |
| O2 | `id` único en el perfil | janitor |
| O3 | Toda nota tiene `summary` presente (vacío solo si es stub) | janitor |
| O4 | Todo enlace interno resuelve a una nota o entidad existente | janitor |
| O5 | No hay wikilinks `[[…]]` fuera de bloques de código | janitor |
| O6 | `entidad`, si está presente, resuelve a una entidad existente | janitor |
| O7 | `## Ver Además` tiene como máximo 5 enlaces, y cada uno su razón | janitor (advertencia) |
| O8 | El índice coincide con el front matter de las notas en disco | janitor de build |

O7 es advertencia y no error: la forma de la razón es una convención de calidad, y bloquear
por ella castigaría al usuario en el único momento que debe ser sin fricción.

---

## 10. Decisiones abiertas

| # | Decisión |
|---|---|
| 1 | Si una nota puede declarar más de una `entidad`, o la transversalidad se expresa siempre omitiendo el campo |
| 2 | Si el índice debe agrupar además por `entidad`, o basta con la proyección de §6 |
| 3 | Si `ARCHIVADO/` debería ser `lifecycle: archivada` en front matter, por coherencia con `spec/entidad.md` §2.3 |
| 4 | Si el agente debe proponer notas a partir de entradas recurrentes —"esto lo has mencionado seis veces, ¿lo sedimentamos?"— o eso viola la inercia deliberada de §7 |
