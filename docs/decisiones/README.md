# Decisiones de arquitectura (ADR)

> `docs/decisiones/README.md` · Índice del historial de decisiones cerradas. Cómo se escribe
> un ADR: [`INSTRUCCIONES.md`](INSTRUCCIONES.md). El porqué general vive en
> [`../brief.md`](../brief.md) y [`../principios.md`](../principios.md); el qué exacto de
> cada formato, en [`../../spec/`](../../spec/).

---

| # | Decisión | Cierra la alternativa | Estado |
|---|---|---|---|
| [0001](0001-id-estable.md) | Identidad estable independiente del path | Identidad por path, con un janitor que reescribe las referencias en cada movimiento | `aceptado` |
| [0002](0002-motor-fuera-del-perfil.md) | El motor nunca se vendoriza en el perfil | Copiar el código dentro del repositorio de datos para reproducibilidad y descubribilidad | `aceptado` |
| [0003](0003-version-de-esquema.md) | Versionado de esquema y migraciones | No versionar; versionar por versión del motor; migrar implícitamente al vuelo | `aceptado` |
| [0004](0004-canonico-no-es-vista.md) | Cada dato se escribe una sola vez en un lugar canónico | Mantener copias sincronizadas a mano en múltiples lugares | `aceptado` |
| [0005](0005-derivadas-no-readonly.md) | Las zonas derivadas no se hacen read-only; se detecta divergencia por hash | Hacer archivos o zonas read-only a nivel de sistema de archivos (`chmod 444`) | `aceptado` |
| [0006](0006-regla-muere-emitido-sobrevive.md) | La regla muere con su portador; lo emitido sobrevive siempre | Consistencia total: borrar la regla borra también sus consecuencias | `aceptado` |
| [0007](0007-plan-es-calendario.md) | El conjunto de archivos `plan_*` es el calendario del usuario | Calcular el calendario futuro desde las reglas de cadencia, sin archivos explícitos | `aceptado` |
| [0008](0008-parent-derivado-del-path.md) | `parent` se deriva del path, no se declara | Declarar `parent` en el front matter para que la jerarquía sea explícita e independiente de la ruta | `aceptado` |
| [0009](0009-type-string-libre.md) | `type` es string libre; el sistema indexa, no valida | Catálogo cerrado de tipos con validación | `aceptado` |
| [0010](0010-friccion-no-se-declara.md) | La fricción no se declara; se descubre en el cierre | Clasificación `fricción` en las entradas, para filtrar desviaciones de forma determinista | `aceptado` |
| [0011](0011-proceso-sin-almacenamiento.md) | Un proceso no agrega primitiva de almacenamiento | Entidad efímera por instancia (opción A) o tarea con estados extendidos (opción B) | `aceptado` |
| [0012](0012-blockuntil-causa-unica.md) | `blocked_until` en entidad carga dos causas bajo un campo | Separar en `paused_reason` para distinguir espera de terceros vs. decisión propia | `aceptado` |
| [0013](0013-cadencias-en-comentario.md) | Las cadencias viven en comentario HTML dentro del archivo de entidad | Archivos YAML separados por entidad o en un directorio `cadencias/` | `aceptado` |
| [0014](0014-formato-posicional-tareas.md) | Las tareas usan formato posicional con metadatos del motor en comentario | Tabla Markdown con todas las columnas visibles | `aceptado` |
| [0015](0015-tuku-log-no-versionado.md) | `tuku.log` vive en el perfil sin versionar | Log versionado en Git junto al resto del perfil | `aceptado` |
| [0016](0016-atomos-diferidos.md) | Promoción de secciones a átomos: diferida hasta evidencia de necesidad | Implementar transclusión desde el principio para secciones que puedan crecer | `aceptado` |

---

> **Nota:** La decisión **0002 obliga a 0003**: si el motor evoluciona por separado de los datos, el contrato entre ambos tiene que estar versionado explícitamente.
