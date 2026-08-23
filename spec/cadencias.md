# spec · cadencias y ciclos

> Lo que aquí se especifica es aquello sobre lo que hay experiencia de campo. La **estrategia** en sentido amplio —objetivos, recursos, capacidad, planes de largo alcance— queda fuera del alcance actual: no se ha logrado generalizar a todos los casos de uso. Ver `brief.md` §4.

## Ciclo

El período que el autor está viviendo. **Por defecto, la semana.**

| Momento | Artefacto | Contenido |
|---|---|---|
| Apertura | **Intención** | Qué corresponde hacer, dado el estado real: pendientes de este ciclo, gatillados por ausencia, y lo que el autor decide sumar |
| Cierre | **Reporte** | Qué ocurrió: resultados, aprendizajes, lo que queda abierto |

**El reporte es la memoria.** Nadie relee diez años de entradas sueltas: lo que se conserva de un período largo es su relato, no su detalle, y ese relato se escribe mientras se recuerda. La pregunta por 2016 se responde leyendo lo que se escribió al cerrar 2016. El detalle crudo no se borra nunca.

Los ciclos anidan: el cierre de las semanas de un mes es el insumo del reporte mensual, y así hacia arriba.

## Cadencias

Reglas que hacen aparecer una tarea cuando corresponde, sin que nadie se acuerde.

| Disparador | Ejemplo |
|---|---|
| Calendario | Pagar los impuestos el día 1 |
| Hecho de bitácora | Vendí lápices → ofrecer reposición en tres meses |
| Completitud de un pendiente | Cerrada la instalación → agendar seguimiento |
| Prácticas de una entidad | Todo cliente nuevo hereda las cadencias de su tipo |
| **Ausencia de actividad** | Un cliente sin contacto hace cuatro semanas; un proyecto detenido |

La cadencia por ausencia es la más valiosa: nadie recuerda aquello que dejó de hacer, y ningún cuaderno lo tiene.

## Cadencias de sistema

Vienen propuestas de fábrica y son editables:

- **Apertura de ciclo** — genera la intención.
- **Cierre de ciclo** — genera el reporte.
- **Higiene** — pasadas de janitor sobre el corpus.

Su existencia garantiza que el primer cierre de ciclo ocurra solo, aunque el autor no haya configurado nada.

## Implementación

El motor de cadencias es **determinista**: scripts leyendo frontmatter, sin LLM. Una cadencia declarada meses atrás debe producir su tarea en el ciclo correcto sin que ningún modelo haya tenido que acordarse (criterio de éxito 6).

Los agentes intervienen en la apertura y el cierre —donde hace falta juicio para redactar la intención y sintetizar el reporte—, no en el disparo.

## Decisión abierta

¿Las alertas sobre pendientes críticos son un janitor propio, o son simplemente cómo se implementa una cadencia? Si comparten propósito, hay una fusión disponible.
