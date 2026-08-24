# TUKU — documentación de diseño

Sistema de gestión personal en archivos Markdown, operado por agentes y gobernado por su autor. Implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal.

Este repositorio contiene el diseño del **software**. El libro de cada autor —bitácora, notas, pendientes, su propio libro de estilo y ámbitos— vive en su repositorio personal.

| Documento | Qué contiene | Estabilidad |
|---|---|---|
| [`brief.md`](docs/brief.md) | Qué es, para quién, marco conceptual y funcionamiento en tres niveles | Alta — cambia poco |
| [`principios.md`](principios.md) | Principios normativos de diseño, descarga cognitiva, primitivas y jerarquía determinista | Alta |
| [`libro-de-estilo.md`](libro-de-estilo.md) | Reglas de escritura, organización, formato de bitácora/pendientes/ámbitos y división janitor/agente | Alta — referencia canónica |

---

**Cómo usarlo:**
- `brief.md` y `principios.md` definen la visión, el alcance y las invariantes del diseño.
- `libro-de-estilo.md` es la referencia viva de cómo interactúan humanos, agentes y herramientas con los archivos Markdown.
- Cualquier cambio o decisión de diseño de software debe ser coherente con estos tres documentos.

