# OKF, el Open Knowledge Format de Google

> Resumen del protocolo y qué conviene tomar de él para TUKU. Referencia externa, no normativa: lo que TUKU adopte se decide en un epic y se escribe en [`../spec/`](../spec/README.md).

**La versión vigente es v0.2**, publicada el 25 de julio de 2026.
## Qué es

Un directorio de archivos markdown con frontmatter YAML. Un concepto por archivo: los campos estructurados van en el frontmatter y todo lo demás en el cuerpo. No hay registro de esquemas, ni autoridad central, ni herramientas obligatorias. Si se puede `cat` un archivo, se puede leer OKF; si se puede clonar un repo, se puede publicar.

La coincidencia con TUKU es casi total, y no es casualidad: los dos apuestan a que el texto plano versionado es el formato correcto para que personas y agentes compartan conocimiento.

## Los campos

Un solo campo es obligatorio, `type`. El resto es opcional y las versiones son compatibles hacia atrás.

| Campo | Qué es |
| --- | --- |
| `type` | **Obligatorio.** Qué clase de concepto es el archivo. Sin vocabulario controlado: cada productor elige los suyos (`Metric`, `Playbook`, `Reference`, `API Endpoint`) |
| `title` | Nombre legible |
| `description` | Una frase |
| `resource` | URI o ruta del activo que el archivo describe |
| `tags` | Lista de etiquetas |

**Procedencia.** `sources` es una lista de objetos con `resource` obligatorio y `id`, `title`, `author`, `usage_count` y `last_modified` opcionales. `usage_window` acota el período con `from` y `to`.

**Confianza.** `generated` lleva `by` obligatorio y `at` opcional. `verified` es un objeto o una lista de ellos, con `by` y `at`.

**Ciclo de vida.** `status` vale `draft`, `stable` o `deprecated`, y por omisión es `stable`. `stale_after` es la fecha a partir de la cual el contenido se considera vencido.

**Actores.** Los campos `by` siguen una convención de tres formas: `<productor>/<versión>` para agentes (`reference_agent/gemini-2.5-pro`), `human:<id>` para personas y `process:<id>` para procesos automáticos. Del prefijo sale el nivel de confianza.

Existe además un tipo `Attested Computation` con campos propios (`runtime`, `parameters`, `computation`, `executor`, `attester`) para conocimiento que se verifica ejecutándolo. Fuera del alcance de TUKU.

## Qué conviene tomar

**`type` obligatorio en todo archivo con frontmatter.** Es el único requisito de OKF y el que abre la puerta a que un lector externo entienda un vault sin conocer TUKU. El vocabulario es libre, así que TUKU declara el suyo: `Cycle` para `AHORA.md` y las bitácoras, `Scope` para los ámbitos, `Note` para las notas, `Pending` para `PENDIENTES.md`, `Cadence` para los `CADENCIAS.md`, `Style Guide` para el libro de estilo.

**Los nombres de campo en inglés.** Igual que los comandos `tuku`, el frontmatter es superficie experta: quien lo edita ya sabe lo que hace. El cuerpo sigue en castellano, que es donde escribe el autor. Hoy `AHORA.md` usa `ciclo`, `desde` y `hasta`; el equivalente es `period`, `from` y `to`.

**`status` para la inmutabilidad de la bitácora.** `AHORA.md` abierto es `draft` y la bitácora archivada es `stable`. No es decoración: la spec de TUKU ya dice que los ciclos cerrados no se reescriben, y `status` lo declara en el archivo mismo en vez de dejarlo implícito en la carpeta donde está.

**`generated.by` y `verified.by` para el principio 3.** La convención de actores separa lo que escribió el autor (`human:<id>`) de lo que propuso un agente (`<agente>/<modelo>`) y de lo que emitió un comando (`process:tuku`). TUKU necesita esa distinción y hoy no la tiene escrita en ninguna parte. Es el campo con más valor de todo el protocolo para este proyecto.

**`sources` para lo derivado.** Un ámbito poblado y una nota destilada salen de registros concretos. `sources` dice de cuáles, y da el camino para reconstruir o auditar sin adivinar.

## Qué no conviene tomar

`resource` no aplica: los archivos de un vault no describen un activo externo, son el activo. `usage_count` y `usage_window` son señales de catálogo de datos. `Attested Computation` entero sobra.

`stale_after` en `AHORA.md` duplicaría lo que ya dice `to`. Dos fuentes para el mismo hecho es una de más.

## Lo que cuesta

Renombrar el frontmatter no es gratuito. Los nombres actuales están acoplados en tres lugares: la expresión regular de [`ahora.py`](../src/tuku/ahora.py), y las sustituciones de plantilla en [`cycle.py`](../src/tuku/cycle.py) e [`init.py`](../src/tuku/init.py). Además toca la plantilla del template y los fixtures de los escenarios que comparan byte a byte.

Es un cambio mecánico y acotado, pero rompe todo vault ya sembrado. Conviene hacerlo antes de que exista un vault real fuera de este repositorio, o nunca.

## Fuentes

- [Especificación de OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
- [Anuncio de v0.2 y las señales de confianza](https://cloud.google.com/blog/products/data-analytics/okf-v0-2-adds-trust-signals)
- [Anuncio original del formato](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
