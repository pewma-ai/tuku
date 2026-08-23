## Transclusión editable

Obsidian nativo **no** permite editar un `![[embed]]` desde el documento que lo transcluye: es solo lectura, y el ícono de hover únicamente abre el archivo de origen. Notion sí lo hace (synced blocks), porque su unidad de almacenamiento es el bloque con ID, no el archivo.

### Embed Editor

https://github.com/xmisio72/obsidian-embed-editor -- synced blocks estilo Notion. MIT License.

- Click en una transclusión y se abre un panel flotante para editar el origen. Al guardar, empalma el texto en el rango exacto de líneas del archivo fuente y refresca el embed.
- Cubre los tres tipos: `![[nota]]`, `![[nota#encabezado]]` y `![[nota#^blockid]]`.
- **Riesgo:** solo 2 commits en el repo, instalación manual en `.obsidian/plugins/`, no aparece en el store oficial. Es prueba de concepto, no algo para apoyar el sistema encima.
- Tensión con P2: la editabilidad pasaría a depender de un plugin comunitario. El `.md` sigue siendo válido, así que el daño está acotado a perder la comodidad, no los datos.

### Anclas de bloque

El `^id` al final de una línea es Markdown válido, se lee sin ninguna app y funciona en los dos visores que uso: Obsidian y Quartz 5 (vía su plugin `ObsidianFlavoredMarkdown`, que soporta `[[Page#^block-id]]`).

Es la correspondencia (archivo + rango) que necesitaría cualquier escritura de vuelta, sea del plugin o de un componedor propio de TUKU. El camino existe sin romper el texto plano.

### Quartz 5 no edita

Es un generador de sitios estáticos: produce HTML de lectura, sin backend. Los roles no compiten: Obsidian es donde se escribe, Quartz es donde se lee lo publicado. La transclusión editable se juega entera en Obsidian.

- Ver [[Herramientas para TUKU#Quartz5]]
- Prueba en `playground/RESULTADO-transclusion.md` (2026-08-23)
