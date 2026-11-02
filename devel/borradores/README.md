# borradores

Diseño que todavía se está pensando. Nada de aquí es norma: el uso real y los epics lo mueven, y cuando algo se estabiliza pasa al [libro de estilo](../../template/vanilla/LIBRO-DE-ESTILO.md) o a [`spec/tuku.md`](../../spec/tuku.md). Lo que dejó de ser spec está en [`../VAULT/spec-anterior/`](../VAULT/spec-anterior/README.md).

| Documento | Qué explora |
| --- | --- |
| [ciclo.md](ciclo.md) | Abrir y cerrar un ciclo, los planes y la capacidad (epic 006). El comportamiento de `AHORA.md` va a cambiar |
| [cadencias.md](cadencias.md) | `CADENCIAS.md`: ciclo de vida, qué emite una cadencia y su trigger |
| [flujo-informacion.md](flujo-informacion.md) | Del dictado a los comandos, las entidades subordinadas y la ambigüedad |

## Decisiones abiertas

Es la única lista de lo que el diseño no decide todavía.

- **Cadencias por evento y no por fecha.** La cadencia de cierre dice `Cuándo: viernes, semanal`, pero lo que la gatilla es que el ciclo termine, y el viernes no significa nada si el ciclo pasa a ser quincenal. Propuesta: `Cuándo` acepta dos gramáticas, distinguidas por la primera palabra (`al ` es evento, lo demás calendario); los eventos son un vocabulario cerrado en `reglas/eventos.md` que `tuku doctor` verifica, porque cada uno es código que mira el vault; y un evento de varios días emite una sola vez reusando la idempotencia del pendiente. Lo decide el epic 006.
- **Por dónde se comunican el autor y las entidades subordinadas.** [flujo-informacion.md](flujo-informacion.md) dice qué devuelve cada entidad (alerta, reporte, propuesta) y que la respuesta del autor entra como una entrada más, pero no por dónde viaja nada:
  - **De la entidad al autor:** un archivo del vault, un mensaje en el canal de conversación, o ambos.
  - **Del autor a la entidad:** cómo responde a una propuesta («sí, abre la página de Carla») y cómo encarga algo («repórtame el avance del mes»), sin que cada rol invente su forma.
  - **Entre entidades:** si una puede pedirle algo a otra o todas hablan solo con el vault.
  - **Las preguntas de una ambigüedad:** quién las plantea y si va en la misma respuesta o más tarde.
- **Archivar una nota.** `tuku note archive TÍTULO` solo avisa que no está implementado, y [notas.md](../VAULT/spec-anterior/notas.md) no dice adónde va la nota ni qué pasa con sus links. Propuesta: `status: deprecated` de OKF ([`../devel/okf-v2.md`](../okf-v2.md)) en el frontmatter; la nota queda en `notas/`, ningún link se rompe y `tuku context` deja de ofrecerla. Lo decide el epic 006.
- **Cómo se suman las magnitudes de la capacidad.** Dónde vive está decidido ([ambitos.md](../VAULT/spec-anterior/ambitos.md)); falta qué queda de un día al restarle `casi todo el día` y `un rato`, y cómo se combinan dos costos el mismo día. Lo decide el epic 006 con casos reales.
