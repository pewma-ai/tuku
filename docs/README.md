# TUKU — documentación de diseño

Sistema de gestión personal en archivos Markdown, operado por agentes y gobernado por su autor. Implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal.

Este repositorio contiene el diseño del **software**. El libro de cada autor —bitácora, notas, pendientes, su libro de estilo— vive en un repositorio distinto, propio de esa persona.

| Documento                                | Qué contiene                                                                              | Estabilidad                       |
| ---------------------------------------- | ----------------------------------------------------------------------------------------- | --------------------------------- |
| [`brief.md`](brief.md)                   | Qué es, para quién, el problema, el marco conceptual                                      | Alta — cambia poco                |
| [`principios.md`](principios.md)         | Principios normativos, cadena de descarga cognitiva, leyes del agente, criterios de éxito | Alta                              |
| [`spec/`](spec/README.md)                | Una especificación por primitiva y por convención transversal                             | Baja — muta con la implementación |
| [`agentes.md`](agentes.md)               | Ecosistema multi-agente, canal único, economía de contexto                                | Media                             |
| [`plantillas/`](plantillas/)             | Libro de estilo por defecto y demás plantillas que TUKU instala en el repo del autor      | Media                             |
| [`corpus-regresion/`](corpus-regresion/) | Contrato de regeneración: qué debe reproducir TUKU y con qué criterio de igualdad         | Alta                              |
| [`decisiones/`](decisiones/)             | ADRs                                                                                      | Aditiva                           |

**Cómo usarlo.** `brief.md` y `principios.md` son la referencia: si una decisión no se deriva de ellos, o están incompletos o la decisión está equivocada — en ambos casos corresponde un ADR. `spec/` puede mutar libremente mientras el contrato de regeneración se siga cumpliendo.
