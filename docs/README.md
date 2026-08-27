# TUKU — Documentación de Diseño

Sistema de gestión personal en archivos Markdown, operado por agentes y gobernado por su autor. Implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal.

Este directorio contiene el diseño canónico del **software**. El libro del autor —bitácoras, notas, pendientes, cadencias, ámbitos y su propio libro de estilo— vive en su repositorio personal.

| Documento | Qué contiene | Estabilidad |
|---|---|---|
| [`brief.md`](brief.md) | Qué es, para quién, marco conceptual y funcionamiento en tres niveles | Alta — cambia poco |
| [`principios.md`](principios.md) | Principios normativos de diseño, descarga cognitiva, conjunto canónico y jerarquía determinista | Alta — marco rector |
| [`libro-de-estilo.md`](libro-de-estilo.md) | Reglas canónicas de escritura, flujo de información, anatomía de archivos, ciclos y matriz janitor/agente | Alta — referencia viva |

---

### Cómo usar esta documentación:

- **`brief.md` y `principios.md`** definen la visión, el alcance, las primitivas canónicas y las invariantes del diseño.
- **`libro-de-estilo.md`** es la referencia viva y operativa de cómo interactúan humanos, agentes y janitors con los archivos Markdown del vault.
- Cualquier implementación de código, janitor o agente en TUKU debe ser estrictamente consistente con estos documentos y con la especificación técnica en [`devel/que_implementar.md`](../devel/que_implementar.md).
