# spec

> **Qué es este directorio.** Qué hace el sistema, con nombres de archivo, formatos e invariantes. Es la única capa que puede nombrar rutas y herramientas, y la única que cambia cuando cambia el layout. Los otros dos documentos del marco: [`../docs/brief.md`](../docs/brief.md) dice qué problema resuelve y para quién, y [`../docs/principios.md`](../docs/principios.md) da el criterio para decidir lo que aún no está escrito.

> Especificaciones normativas de TUKU. Se justifican por referencia a [`../docs/principios.md`](../docs/principios.md) y [`../docs/brief.md`](../docs/brief.md). Lo que aquí se afirma es normativo para el motor: el código no inventa reglas, implementa lo que dice este directorio. Cuando código y spec discrepan, el defecto está en el código, salvo que la spec no se derive de [`../docs/principios.md`](../docs/principios.md), en cuyo caso el defecto está en la spec.

Este directorio reemplaza al contenido normativo que antes vivía mezclado dentro del plan de fases. La especificación de "qué hace el sistema" vive aquí; el orden y estado de implementación vive en [`../devel/epics.md`](../devel/epics.md).

## Normativo no quiere decir definitivo

Estas specs se van a corregir con el uso. Están escritas desde lo que ya se probó, y cada experimento sobre el sistema real puede mover lo que aquí dice. Eso es el método, no una deuda.

Las dos escalas de tiempo no se contradicen:

- **Dentro de un epic**, la spec manda sobre el código. Si al implementar aparece un caso que la spec no cubre, no se decide en el código: se escribe primero aquí.
- **Entre epics**, el experimento manda sobre la spec. Lo que el uso demuestre distinto se corrige en este directorio, y esa corrección es un resultado del epic, no un fallo.

Corolario: una spec que lleva mucho sin tocarse no está madura necesariamente. Puede ser que esa parte todavía no se haya usado.

## Orden de lectura

Igual que las fases de implementación, se lee de lo que no depende de nada a lo que compone todo lo anterior.

| # | Documento | Qué especifica |
| --- | --- | --- |
| 1 | [vault.md](vault.md) | El vault como conjunto: el árbol, qué es de TUKU y qué del autor, el frontmatter, la configuración y dónde viven los comandos |
| 2 | [markdown.md](markdown.md) | Cómo se escribe todo archivo: el dialecto (CommonMark, GFM y tres extensiones de Obsidian), quién lo lee, los datos de máquina en estructura visible y los enlaces |
| 3 | [flujo-informacion.md](flujo-informacion.md) | El marco: el camino del autor desde una intención hasta los comandos que escriben, las familias de entrada, las entidades subordinadas que mantienen el corpus y la ambigüedad |
| 4 | [bitacora.md](bitacora.md) | El registro: formato de línea, ontología cerrada (`**pendiente**`, `(Hecho)`, `**cadencia**`) y abierta, reglas de redacción |
| 5 | [pendientes.md](pendientes.md) | `PENDIENTES.md`: tabla única, escalera de horizontes, y cómo llega cada vista (propagación y transclusión) |
| 6 | [ambitos.md](ambitos.md) | El árbol de ámbitos: los tres roles, qué carga cada directorio, qué prevalece y qué se acumula, archivado |
| 7 | [cadencias.md](cadencias.md) | `CADENCIAS.md`: ciclo de vida de una cadencia, qué puede emitir, el trigger que conoce el tipo de ciclo, idempotencia |
| 8 | [notas.md](notas.md) | El zettelkasten, las notas tipadas y el procedimiento de destilado |
| 9 | [ciclo.md](ciclo.md) | `AHORA.md`, su frontmatter, apertura y cierre, qué se aplana y qué queda siempre como enlace |
| 10 | [cli.md](cli.md) | El contrato del comando `tuku`: la gramática de sustantivo, verbo y parámetro, qué garantiza, códigos de salida, forma de la salida. Independiente de quién invoque |
| 11 | [tuku.md](tuku.md) | La superficie del CLI: la firma de cada comando y qué archivos lee y escribe, con lo pendiente marcado |
| 12 | [agente.md](agente.md) | Lo que cambia cuando el ejecutor es un agente de IA y no una persona con el flujo a mano |
| 13 | [despacho.md](despacho.md) | El `AGENTS.md` de la raíz: a dónde va lo que el autor dice, la tabla de despacho y la cascada por directorio |

## Qué está fuera de alcance

Cada spec declara su propio "no entra" en la sección correspondiente. A nivel de directorio:

- **Los comandos reales, en código.** Este directorio especifica su contrato (qué leen, qué escriben y cómo, y en [cli.md](cli.md) lo que vale para todos); la implementación vive fuera del vault, en el paquete que instala `uv tool install` o `pipx`, y su plan de construcción vive en [`../devel/epics.md`](../devel/epics.md).
- **El orden de implementación y la estrategia de pruebas.** Eso es [`../devel/epics.md`](../devel/epics.md), no este directorio: aquí se especifica qué hace el sistema, no en qué fase se construye ni cómo se verifica.
- **La deliberación con el autor** (archivar una rama, aprobar una propuesta). Se especifica la mecánica que la rodea, nunca el criterio para decidir.

## Decisiones abiertas

- **Cómo se especifica una cadencia que se gatilla por un evento y no por una fecha.** El caso que lo destapó es el cierre del ciclo: la cadencia sembrada dice `Cuándo: viernes, semanal`, pero lo que la gatilla es que el ciclo termine, y el viernes deja de significar nada si el ciclo pasa a ser quincenal. La fecha es un síntoma del evento. La propuesta sobre la mesa es que `Cuándo` acepte dos gramáticas distinguidas por la primera palabra (todo lo que empieza con `al ` es evento, lo demás es calendario), que los eventos sean vocabulario cerrado en un `reglas/eventos.md` verificable por `tuku doctor`, porque cada evento es código que mira el vault, y que un evento que dura varios días emita una sola vez reusando la idempotencia del pendiente en vez de llevar un registro de eventos vistos. Queda por decidir, y lo decide el epic 006, que es donde entran las cadencias.
- **Por dónde se comunican el autor y las entidades subordinadas.** [flujo-informacion.md](flujo-informacion.md) dice qué devuelve cada entidad (una alerta, un reporte, una propuesta) y que la respuesta del autor entra como una entrada más, pero no por dónde viaja nada de eso. Queda por decidir:
  - **De la entidad al autor.** Dónde aparece una alerta o una propuesta para que el autor la vea sin ir a buscarla: un archivo del vault, un mensaje en el canal de conversación, ambos.
  - **Del autor a la entidad.** Cómo responde a una propuesta («sí, abre la página de Carla») y cómo encarga algo a una entidad («repórtame el avance del mes»), sin que cada rol invente su propia forma.
  - **Entre entidades.** Si una entidad puede pedirle algo a otra (el análisis que le pide un dato al reporte) o todas hablan solo con el vault.
  - **Las preguntas de una ambigüedad.** Quién las plantea y cuándo: en la misma respuesta o más tarde, por una entidad.
- **Qué es archivar una nota.** `tuku note archive TÍTULO` existe solo como aviso de no implementado, y [notas.md](notas.md) no dice adónde va la nota ni qué pasa con los links que la apuntan. `archivado/` está pensado para ramas cerradas de `ambitos/` ([vault.md](vault.md)). La propuesta es `status: deprecated` de OKF en el frontmatter ([`../devel/okf-v2.md`](../devel/okf-v2.md)): la nota queda en `notas/`, ningún link se rompe, y `tuku context` y el enlace automático la dejan de ofrecer. Lo decide el epic 006, que es el que archiva notas.
- **Cómo se suman las magnitudes de la capacidad.** Dónde vive la capacidad está decidido ([ambitos.md](ambitos.md)), pero no qué queda de un día al restarle `casi todo el día` y `un rato`, ni cómo se combinan dos costos el mismo día. Lo decide el epic 006 con casos reales, que es donde entran los planes.
