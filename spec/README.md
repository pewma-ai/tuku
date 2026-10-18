# spec

Qué hace el sistema, con nombres de archivo, formatos e invariantes. Es la única capa que nombra rutas y herramientas, y la única que cambia cuando cambia el layout. Los otros dos documentos del marco: [`../docs/brief.md`](../docs/brief.md) dice qué problema resuelve y para quién, y [`../docs/principios.md`](../docs/principios.md) da el criterio para lo que aún no está escrito.

Lo que se afirma aquí es normativo: el código implementa lo que dice este directorio y no inventa reglas. Si código y spec discrepan, el defecto está en el código, salvo que la spec no se derive de los principios, y entonces está en la spec. El orden y el estado de la implementación viven en [`../devel/epics.md`](../devel/epics.md).

## Normativo no quiere decir definitivo

Cada experimento sobre el sistema real puede mover lo que dice una spec. Eso es el método, no una deuda.

- **Dentro de un epic**, la spec manda sobre el código. Un caso que la spec no cubre se escribe primero aquí y después se implementa.
- **Entre epics**, el experimento manda sobre la spec. Lo que el uso demuestre distinto se corrige aquí, y esa corrección es un resultado del epic.

Una spec que lleva mucho sin tocarse puede estar sin usar, no madura.

## Orden de lectura

De lo que no depende de nada a lo que compone todo lo anterior.

| # | Documento | Qué especifica |
| --- | --- | --- |
| 1 | [vault.md](vault.md) | El árbol del vault, qué es de TUKU y qué del autor, el frontmatter y la configuración |
| 2 | [markdown.md](markdown.md) | El dialecto de todo archivo, los datos de máquina en estructura visible y los enlaces |
| 3 | [flujo-informacion.md](flujo-informacion.md) | Del dictado del autor a los comandos que escriben, las entidades subordinadas y la ambigüedad |
| 4 | [bitacora.md](bitacora.md) | El registro: formato de línea, ontología (`**pendiente**`, `(Hecho)`, `**cadencia**`) y redacción |
| 5 | [pendientes.md](pendientes.md) | `PENDIENTES.md`: tabla única, horizontes y cómo llega cada vista |
| 6 | [ambitos.md](ambitos.md) | El árbol de ámbitos: roles, keywords, qué prevalece y qué se acumula |
| 7 | [cadencias.md](cadencias.md) | `CADENCIAS.md`: ciclo de vida, qué emite una cadencia y su trigger |
| 8 | [notas.md](notas.md) | El zettelkasten, las notas tipadas y el destilado |
| 9 | [ciclo.md](ciclo.md) | `AHORA.md`: frontmatter, apertura, cierre y planes |
| 10 | [cli.md](cli.md) | El contrato de `tuku`: gramática, garantías, códigos de salida y forma de la salida |
| 11 | [tuku.md](tuku.md) | La firma de cada comando y qué archivos lee y escribe, con lo pendiente marcado |
| 12 | [agente.md](agente.md) | Qué cambia cuando quien ejecuta es un agente de IA |
| 13 | [despacho.md](despacho.md) | El `AGENTS.md` de la raíz: los dos modos, la tabla de despacho y los límites |

## Fuera de alcance

Cada spec declara su propio "no entra". Del directorio entero quedan fuera:

- **El código de los comandos.** Aquí va su contrato; la implementación vive en el paquete `tuku`.
- **El orden de implementación y las pruebas**, que son de [`../devel/epics.md`](../devel/epics.md).
- **El criterio de las decisiones del autor** (archivar una rama, aprobar una propuesta). Se especifica la mecánica que las rodea.

## Decisiones abiertas

Es la única lista de lo que el diseño no decide todavía.

- **Cadencias por evento y no por fecha.** La cadencia de cierre dice `Cuándo: viernes, semanal`, pero lo que la gatilla es que el ciclo termine, y el viernes no significa nada si el ciclo pasa a ser quincenal. Propuesta: `Cuándo` acepta dos gramáticas, distinguidas por la primera palabra (`al ` es evento, lo demás calendario); los eventos son un vocabulario cerrado en `reglas/eventos.md` que `tuku doctor` verifica, porque cada uno es código que mira el vault; y un evento de varios días emite una sola vez reusando la idempotencia del pendiente. Lo decide el epic 006.
- **Por dónde se comunican el autor y las entidades subordinadas.** [flujo-informacion.md](flujo-informacion.md) dice qué devuelve cada entidad (alerta, reporte, propuesta) y que la respuesta del autor entra como una entrada más, pero no por dónde viaja nada:
  - **De la entidad al autor:** un archivo del vault, un mensaje en el canal de conversación, o ambos.
  - **Del autor a la entidad:** cómo responde a una propuesta («sí, abre la página de Carla») y cómo encarga algo («repórtame el avance del mes»), sin que cada rol invente su forma.
  - **Entre entidades:** si una puede pedirle algo a otra o todas hablan solo con el vault.
  - **Las preguntas de una ambigüedad:** quién las plantea y si va en la misma respuesta o más tarde.
- **Archivar una nota.** `tuku note archive TÍTULO` solo avisa que no está implementado, y [notas.md](notas.md) no dice adónde va la nota ni qué pasa con sus links. Propuesta: `status: deprecated` de OKF ([`../devel/okf-v2.md`](../devel/okf-v2.md)) en el frontmatter; la nota queda en `notas/`, ningún link se rompe y `tuku context` deja de ofrecerla. Lo decide el epic 006.
- **Cómo se suman las magnitudes de la capacidad.** Dónde vive está decidido ([ambitos.md](ambitos.md)); falta qué queda de un día al restarle `casi todo el día` y `un rato`, y cómo se combinan dos costos el mismo día. Lo decide el epic 006 con casos reales.
