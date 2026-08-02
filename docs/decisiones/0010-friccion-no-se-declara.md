# ADR 0010 — La fricción no se declara; se descubre en el cierre

## Contexto

El sistema registra eventos con una clasificación: `Hito`, `Decisión`, `Señal`, `msg`. Una
quinta clasificación obvia sería `Fricción` o `Desviación`: marcar en el momento en que algo
sale mal.

Tener una clasificación de fricción tiene ventajas claras. Las desviaciones quedarían
marcadas explícitamente en el log, el cierre podría filtrarlas de forma determinista sin
juicio del agente, y los informes anuales podrían mostrar la frecuencia de fricciones por
entidad.

## Decisión

**No existe una clasificación `fricción`**. Las desviaciones no se etiquetan al escribir:
se descubren en el cierre contrastando el plan con la actividad registrada.

El cierre evalúa entidad por entidad: para cada una, contrasta lo que se esperaba —según su
`alineamiento`, su descripción inferida y sus cadencias— con lo que efectivamente ocurrió
—según sus entradas y el estado de sus tareas—. Lo que no encaja es la desviación, sin que
nadie haya tenido que nombrarlo como tal.

Esta decisión viene de la evidencia: en 8 ciclos del corpus real, las clasificaciones `Hito`
y `Decisión` aparecen 59 y 22 veces respectivamente; `Fricción` aparece 0 veces. La fricción
no se etiqueta mientras se trabaja; se ve solo en retrospectiva.

## Consecuencias

**A favor.**

- El usuario no tiene que etiquetar sus propios fracasos en el momento en que ocurren, cuando
  hay menos distancia para evaluarlos y más urgencia de resolverlos.
- La clasificación de fricción en tiempo real habría requerido un juicio —¿esto es una
  desviación o una decisión?— que a menudo no está disponible en el momento.
- El contraste retrospectivo es más rico: puede detectar fricciones que el usuario no habría
  reconocido como tales porque las resolvió al vuelo.

**En contra, y aceptado.**

- El cierre depende del juicio del agente para detectar la desviación, no de un filtro
  determinista. Esto lo hace familia semántica, no derivación pura
  (`docs/arquitectura.md` §5).
- Una fricción que no dejó huella en las entradas —algo que salió mal pero no se registró—
  es invisible para el sistema. El hábito de registro es parte del contrato de uso.

## Estado

`aceptado`
