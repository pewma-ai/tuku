# Contrato de regeneración

> Este es el spec ejecutable del proyecto. Mientras `spec/` muta, esto es lo que dice si una iteración avanzó o retrocedió.

## Qué es

Seis meses de corpus real, escrito a mano bajo el sistema anterior, sirven de corpus de regresión. TUKU debe poder **reparsearlo y regenerar lo que se construyó**, sin haberlo visto como plantilla.

El plan de implementación avanza por casos de uso, cada uno cerrando cuando su fila de la tabla pasa.

## Criterio de igualdad

Del criterio de éxito 4:

| Produce | Debe volver | Si falla |
|---|---|---|
| Janitor | **Idéntico** — byte a byte, salvo timestamps de generación | Hay un bug, o hay juicio de agente donde correspondía una regla |
| Agente | **Equivalente en sentido** — evaluado por un tercer modelo o por el autor | Hay ambigüedad en el libro de estilo, o falta contexto |

Si algo que debía ser idéntico solo resulta equivalente, la regla está en el brazo equivocado de `spec/coherencia.md`.

## Tabla de regeneración

Completar archivo por archivo antes de empezar a implementar. Sin esta tabla no hay forma de saber si una iteración mejoró.

| # | Artefacto del corpus | Se regenera desde | Criterio | Caso de uso | Estado |
|---|---|---|---|---|---|
| 1 | `PENDIENTES.md` | Bitácora completa | Idéntico | Proyección de pendientes | ☐ |
| 2 | Resúmenes semanales | Bitácora de la semana | Equivalente | Cierre de ciclo | ☐ |
| 3 | Vocabulario (ámbitos, áreas) | Bitácora completa | Idéntico | Extracción determinista | ☐ |
| 4 | Páginas de entidad | Bitácora + prácticas | Equivalente | Siembra de entidades | ☐ |
| 5 | Cadencias activas | Frontmatter + `tuku.yaml` | Idéntico | Motor de cadencias | ☐ |
| 6 | Vistas por proyecto | `PENDIENTES.md` + bitácora | Idéntico | Notas de estructura | ☐ |
| 7 | Marcas de autoría | Historial git + heurística | Idéntico | Janitor de procedencia | ☐ |
| … | (completar con el corpus real a la vista) | | | | ☐ |

## Corpus de regresión del parser

Un subconjunto congelado del corpus, con casos límite deliberados: viñetas malformadas, tipos desconocidos, wikilinks rotos, transclusiones circulares, entradas sin hora.

**Todo cambio al parser corre contra este subconjunto antes de aceptarse**, sea propio o descargado desde upstream. Un error de parser no queda contenido en una nota: corrompe la lectura de años de archivos.

## Nota sobre el corpus

El corpus histórico es de un solo autor y de un solo perfil de uso. Regenerarlo bien es condición necesaria, no suficiente: prueba que el sistema funciona para el caso del desarrollador que opera por terminal, que explícitamente **no** es el centro del diseño (`brief.md` §2). El segundo corpus de prueba debería venir de un autor distinto.
