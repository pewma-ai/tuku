# spec · corpus

Convenciones transversales del repositorio del autor.

## Formato

Markdown con frontmatter YAML simple (P3). Se usan las convenciones de Obsidian —wikilinks, transclusión— asumiendo el acoplamiento: degradan a texto legible sin la aplicación, pero no son Markdown estándar. El libro de estilo declara cuáles se admiten.

## Enlaces y transclusión

- `[[nota]]` — referencia. Acoplamiento débil.
- `![[nota]]` — **transclusión**. Acoplamiento fuerte: el contenido de A altera lo que se percibe en B sin que B se haya tocado.

La transclusión existe para no duplicar: trocitos de papel reutilizables para componer documentos. Se usa siempre que un mismo texto deba aparecer en dos lugares.

1. El libro de estilo declara la granularidad admitida (archivo, sección, bloque).
2. Pesa más que un wikilink en el grafo de vecindad (`coherencia.md`).
3. Un **componedor** determinista resuelve las transclusiones y arma el archivo temporal compuesto, con profundidad limitada para evitar ciclos. Los agentes se reservan para *interpretar* el compuesto, nunca para construirlo.

## Diagramas y assets

**Mermaid** es el formato preferente: es texto dentro del `.md`, el archivo se autocontiene.

Los **assets binarios** rompen la autocontención por definición: no son diffables ni legibles por un agente de texto sin visión/OCR, y dependen de rutas que pueden romperse. Requieren carpeta dedicada y regla propia de referencia rota. Prioridad menor, pendiente de diseño.

## Autoría y procedencia

Todo texto pertenece a una categoría explícita:

| Categoría | Idea | Redacción |
|---|---|---|
| Del autor | autor | autor |
| **Dictado** | autor | IA |
| Inferido por IA | IA | IA |
| Corregido | autor (al editar) | mixta |

*Dictado* es el caso habitual en la bitácora: el autor da ideas generales y un agente redacta. La idea es suya, la prosa no.

Toda inferencia externa —contexto organizacional tomado del conocimiento general del modelo— se marca con **modelo y fecha**: dentro de veinte años debe poder distinguirse la opinión de un LLM de 2026 de una observación del autor.

**La marca no es permanente.** Cuando el autor edita a mano una línea marcada como IA, la etiqueta queda desactualizada. Un janitor lo detecta y reclasifica, para que la marca siga siendo confiable y no sea un fósil de la primera versión del párrafo.

**El autor no se percata de nada de esto.** La autoría la manejan los janitors. La única excepción conocida es operar largo tiempo solo con un editor de texto, sin janitors corriendo (P8): en ese escenario las marcas se desactualizan hasta la siguiente pasada.

## Índice de consulta

A escala de miles de archivos, `grep` deja de alcanzar. Se admite un índice SQLite/FTS **reconstruible desde los `.md` y nunca autoritativo**: borrarlo entero no pierde información.
