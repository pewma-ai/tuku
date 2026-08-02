# spec/ — Cómo leer las especificaciones

Este directorio contiene el **qué exacto** de cada formato: nombres de archivo, campos de
front matter, gramáticas, invariantes. El **porqué** vive en [`../docs/`](../docs/) y el
**cómo** del código en [`../src/`](../src/).

Una spec es el contrato entre los datos y el motor. Cuando el código y la spec discrepan, el
defecto está en el código — salvo que la spec no pueda derivarse de
[`../docs/arquitectura.md`](../docs/arquitectura.md), en cuyo caso el defecto está aquí.

---

## Orden de lectura

Cada spec declara en su cabecera de qué depende. El orden que sigue respeta esas dependencias:

| # | Documento | Define | Estado |
|---|---|---|---|
| 1 | [`entidad.md`](entidad.md) | Entidades, ámbitos, jerarquía, zonas editables y derivadas, `status` | completa |
| 2 | [`entradas.md`](entradas.md) | El almacén canónico de entradas y las bitácoras como proyecciones | completa |
| 3 | [`tarea.md`](tarea.md) | El backlog canónico, la gramática temporal y el arrastre | completa |
| 4 | [`cadencia.md`](cadencia.md) | La regla que produce artefactos en el tiempo: herencia, disparos, emisión | completa |
| 5 | [`artefactos-ciclo.md`](artefactos-ciclo.md) | `plan_*`, `resultados_*` e informes por audiencia | completa |
| — | [`frontmatter.md`](frontmatter.md) | Los campos mínimos, transversales a todo tipo de archivo | **pendiente** |
| — | [`perfil.md`](perfil.md) | El layout del perfil y el contrato con el motor: `.tuku/config.yaml` | **pendiente** |

Lectura mínima para escribir código del motor: **entidad → entradas → tarea**. Son las tres
primitivas; el resto se construye sobre ellas.

`entidad.md` va primero porque casi todo lo demás la referencia: una entrada pertenece a una
entidad, una tarea nace de una entidad, una cadencia se hereda por su cadena de padres.

Las dos pendientes son transversales y hoy están dispersas: los campos de front matter
aparecen repartidos entre las cinco specs completas, y el formato real de `.tuku/config.yaml`
solo existe como fragmentos ilustrativos en `arquitectura.md` §4 y en las specs que lo
mencionan. **`perfil.md` es lo que bloquea la implementación**: el grafo de derivaciones y
los janitors dependen de ese formato.

---

## Anatomía de una spec

| Parte | Contiene |
|---|---|
| **Cabecera** | Qué define, de qué depende, qué otras specs conviene tener a mano |
| **Definición** | El término, con la precisión del [glosario](../docs/glosario.md) |
| **Formato** | Nombres de archivo, front matter, gramática, ejemplos válidos |
| **Ciclo de vida** | Qué ocurre en el alta, la modificación, el archivado, la eliminación |
| **Invariantes** | Tabla numerada con prefijo por spec, y el garante de cada una |
| **Decisiones abiertas** | Lo que aún no se decide, numerado |

### Las invariantes llevan prefijo

Cada spec numera sus invariantes con una letra propia, de modo que una referencia sea
inequívoca desde cualquier lugar del repositorio:

| Prefijo | Spec |
|---|---|
| `N` | entidad |
| `E` | entradas |
| `T` | tarea |
| `K` | cadencia |
| `C` | artefactos de ciclo |

Toda invariante declara su **garante**: `janitor`, `janitor de build`, `motor`, o `test de
replay`. Es la aplicación directa de P3 —cada garantía tiene un costo conocido— y lo que
permite saber qué se verifica sin invocar ningún modelo.

### Los ejemplos son normativos

Los bloques de código de una spec no son ilustraciones: son casos que el parser debe
aceptar y el motor reproducir. Cuando entren los tests, salen de ahí.

---

## Convenciones

**Idioma.** La prosa en español. Los campos de front matter y los identificadores internos
en inglés (`lifecycle`, `cycle_start`, `enabled`). Las primitivas del dominio en español
—entrada, tarea, entidad, cadencia, ciclo— tanto aquí como en lo que ve el usuario.

**No dupliques.** Si un formato está definido en una spec, las demás lo enlazan con su
número de sección; no lo repiten. La duplicación en documentación se desincroniza igual que
en código.

**Canónico ≠ vista.** Toda spec distingue explícitamente qué es fuente de verdad y qué es
proyección recomputable ([`../docs/arquitectura.md`](../docs/arquitectura.md) §3). Si una
spec no lo deja claro para su artefacto, está incompleta.

**Las decisiones abiertas se numeran y se quedan.** Viven al final de cada spec hasta que se
cierran. Si al cerrarse descartan una alternativa viable, se convierten en un
[ADR](../docs/decisiones/) y se retiran de la lista.
