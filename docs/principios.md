# Principios

> Normativos. Cualquier decisión que los contradiga obliga a un ADR. Este archivo debe estar siempre en el contexto de quien implementa.

## Diseño

| # | Principio | Implicancia |
|---|---|---|
| P1 | **La arquitectura Markdown manda** | La estructura de archivos ES el diseño. Interfaz, motor, agentes y despliegue se subordinan al texto plano. Si una interfaz necesita lógica propia para que los archivos tengan sentido, la arquitectura está mal. |
| P2 | **Texto plano sin parser propietario** | Legible e interpretable sin ejecutar software específico. Imprimible sin pérdida semántica. Horizonte: veinte años. |
| P3 | **Simplicidad del frontmatter** | Sin tipos ambiguos ni anidamiento profundo. |
| P4 | **Determinismo primero, agencia al final** | Lo mecánico se resuelve con scripts. El LLM entra solo donde hace falta juicio. |
| P5 | **El autor gobierna, el agente propone** | Ninguna convención se ratifica sin aprobación explícita. |
| P6 | **Trazabilidad de autoría** | Todo texto es atribuible a quien lo pensó y a quien lo redactó. |
| P7 | **Sin vendor lock de LLM** | Funciona con cualquier modelo sobre un umbral mínimo de inteligencia. |
| P8 | **Degradación gradual** | Si cae el servidor, los agentes o el canal móvil, el sistema sigue usable a mano. |

## Cadena de descarga cognitiva

```
YAML  →  Janitor  →  Agente  →  Autor
```

El YAML configura al janitor; el janitor le quita carga mecánica al agente; el agente le quita carga operativa al autor. Al autor le queda lo irreductible: gobernar, ratificar, decidir.

Regla al elegir dónde implementar algo: bajar lo más posible en esta cadena.

## Leyes del agente

Jerárquicas, cada una subordinada a la anterior:

1. El agente no escribe ni ratifica una convención sin aprobación del autor.
2. El agente prefiere el camino determinista disponible antes que gastar inferencia propia.
3. El agente se cuida a sí mismo (silencio por defecto, sesiones acotadas, contexto mínimo pertinente) salvo que ello viole la primera o la segunda ley.

## Criterios de éxito

Primero, si le sirvió a alguien:

1. **Permanencia:** una persona que nunca fue ordenada sigue usándolo al tercer mes, y no porque se lo haya propuesto.
2. **Recuerdo:** abrir un ciclo le devuelve algo que había olvidado que se prometió. Es la promesa del nombre y el momento en que el producto se gana su lugar.
3. **Sin fricción:** contarle algo al sistema no cuesta más que anotarlo en un papel. Si cuesta más, el autor lo anota en el papel y tiene razón.

Después, si el diseño está bien hecho:

4. **Reconstrucción:** borrar todo lo derivado y volver a construirlo desde lo que el autor escribió devuelve el mismo sistema. Lo que producen los janitors debe volver **idéntico**; lo que redactan los agentes, **equivalente en sentido**. Si algo que debía ser idéntico solo resulta equivalente, hay juicio del agente donde correspondía una regla.
5. **Operación manual:** una persona ejecuta un ciclo completo (apertura, registro, cierre) siguiendo solo lo escrito en Markdown, sin agentes, y el resultado es válido.
6. **Memoria fuera del modelo:** una cadencia declarada meses atrás produce su tarea en el ciclo correcto sin que ningún LLM haya tenido que acordarse.
7. **Una regla, dos lectores:** lo escrito en un `AGENTS.md` lo puede seguir igual un agente que el autor un domingo por la tarde. Si hay que traducirlo para uno de los dos, está mal escrito. (Esto exige legibilidad del derivado, no identidad con el libro de estilo: ver `spec/coherencia.md`.)
8. **Frugalidad:** una sesión normal de registro no invoca ningún modelo caro. El juicio, que se paga, aparece en la apertura, en el cierre y cuando el autor lo pide.

El criterio 4 es el test operativo del proyecto: ver `corpus-regresion/contrato-de-regeneracion.md`.
