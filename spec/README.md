# spec

> Especificaciones del modelo. Se justifican por referencia a `../docs/brief.md` y `../docs/principios.md`. Lo que aquí se afirma es normativo; lo que se contradiga con esos dos documentos es un error de este directorio, no de ellos.

Estas specs se van a ir corrigiendo con el uso. Las escribo desde lo que ya probé, y cada experimento que haga sobre el sistema real puede mover lo que aquí está escrito: eso es el método, no una deuda. Un spec que lleva meses sin tocarse no está maduro necesariamente, puede ser que esa parte no se haya usado todavía.

## Orden de lectura

Los specs se leen en el orden en que las cosas se derivan unas de otras:

| #   | Documento                      | Qué especifica                                                                                           |
| --- | ------------------------------ | -------------------------------------------------------------------------------------------------------- |
| 1   | [bitacora.md](spec/bitacora.md)     | La primitiva única: eventos fechados con hora, inmutables, y el formato de viñeta del que todo se extrae |
| 2   | [pendientes.md](pendientes.md) | Doble fuente (bitácora de origen, `PENDIENTES.md` operativo), ciclo de vida y emparejamiento semántico   |
| 3   | [notas.md](notas.md)           | Las tres clases de nota, la convención de MAYÚSCULAS para inducción, y el criterio de "ver además"       |
| 4   | [entidades.md](entidades.md)   | El objeto de trabajo, los tipos que define cada autor, y las prácticas heredadas por tipo                |
| 5   | [cadencias.md](cadencias.md)   | El ciclo (apertura, cierre) y las reglas que hacen aparecer tareas, incluida la disparada por ausencia   |
| 6   | [corpus.md](corpus.md)         | Convenciones transversales: formato, transclusión, diagramas, marcas de autoría y procedencia            |
| 7   | [coherencia.md](coherencia.md) | El libro de estilo como única edición humana, sus derivados, y qué es un janitor                         |

Los primeros cinco describen **qué hay en el repositorio del autor**. Los dos últimos, **cómo se mantiene coherente**.

## Qué está fuera de alcance

La estrategia en sentido amplio (objetivos, recursos, capacidad, planes de largo alcance) no está especificada: no se ha logrado generalizar a todos los casos de uso. Lo que sí se sostiene con experiencia de campo es el ciclo y sus cadencias. Ver `../docs/brief.md` §4.

Las **reglas de tratamiento** de tareas (prioridad, tipos, encadenamiento, criterios de vencimiento) están pendientes de un documento propio. `pendientes.md` cubre solo el modelo.

Los **assets binarios** rompen la autocontención por definición y requieren regla propia de referencia rota. Prioridad menor, pendiente de diseño (`corpus.md`).

## Decisiones abiertas

Cada una vive en su spec y se cierra con un ADR:

- ¿Las alertas sobre pendientes críticos son un janitor propio, o son cómo se implementa una cadencia? (`cadencias.md`)
- ¿Un janitor descargado desde upstream se aplica solo, o pasa por la misma regresión que un cambio local? (`coherencia.md`)
- ¿Es "janitor" el nombre de todo el motor determinista, o de una parte? Hoy se usa como sinónimo del motor completo. (`coherencia.md`)

## El test operativo

Borrar todo lo derivado y reconstruirlo desde lo que el autor escribió debe devolver el mismo sistema: idéntico lo que producen los janitors, equivalente en sentido lo que redactan los agentes. Es el criterio de éxito 4 y el test del proyecto entero.

El corpus de regresión que lo ejecuta (`../corpus-regresion/`, con su contrato de regeneración) está referenciado por `coherencia.md` pero aún no existe en el repositorio.
