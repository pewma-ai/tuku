# Libro de estilo

> Las reglas de escritura del autor. Este archivo es suyo: empieza con lo mínimo y crece cuando el uso revele una regla que valga la pena fijar.

Cómo funciona el sistema no se explica aquí, está en `AGENTS.md`. Aquí va solo el vocabulario que elige el autor.

## El autor

**Nombre del autor:** por declarar. El instalador lo pregunta al crear el vault; si se deja en blanco, el autor lo escribe aquí cuando quiera.

El sistema escribe en primera persona y esa primera persona es el autor. Cuando su nombre aparece en un dictado, se refiere a él y no a un tercero.

## Los tres encabezados de abajo son contrato

Las automatizaciones leen las tablas que siguen buscando estos encabezados exactos. Las **filas** se agregan, se quitan o se cambian cuando haga falta. Si se renombra un **encabezado**, las automatizaciones dejan de encontrar el vocabulario.

### Clasificaciones

De qué clase es cada entrada. Nadie las valida en forma estricta: si se usa una que no está en la tabla, se acepta y se formaliza después.

| Clasificación | Qué significa |
| --- | --- |
| `progreso` | Avance concreto en algo que estaba en curso. |
| `decisión` | Una elección tomada, con su razón. |
| `fricción` | Algo que costó ejecutar o que bloqueó al autor. |
| `señal` | Un patrón o un hecho externo que merece atención más allá de hoy. |
| `nota` | Un hecho que no calza en las anteriores. |

La distinción que más se usa es `señal` contra `fricción`: la señal es algo que se observa, la fricción es algo que pesó. Sin esa distinción, todo lo desagradable termina siendo fricción.

### Horizontes

Los plazos a los que puede estar asignado un pendiente. Son los cinco callouts permanentes de `PENDIENTES.md`.

| Horizonte | Qué agrupa |
| --- | --- |
| `atrasados` | Lo que tenía fecha y ya venció. |
| `sin-fecha` | Lo abierto que todavía no tiene plazo. |
| `esta-semana` | Lo comprometido para la semana en curso. |
| `proxima-semana` | Lo que va a la semana siguiente. |
| `fin-de-mes` | Lo que debe estar antes de que termine el mes. |

Un pendiente va bajando de escalón a medida que se concreta: primero sin fecha, después un horizonte, después un día exacto.

Estos nombres son del autor, no de TUKU: los horizontes salen de esta tabla y de los anclas de `PENDIENTES.md`. Si el ritmo no es la semana sino el turno, la quincena o la temporada, se renombran en los dos lugares y el sistema sigue funcionando igual. La escalera es la que importa, no cómo se llame cada escalón.

### Tipos de nota

Las notas pueden ser libres. Algunas, sobre cosas que se repiten, conviene que sigan una plantilla.

| Tipo | Para qué | Cuidado |
| --- | --- | --- |
| `persona` | Trabajar mejor con alguien con quien el autor trata seguido. | Se escribe solo lo que se le mostraría a esa persona. |

Empieza con uno. Los demás aparecen cuando algo se repite lo suficiente como para merecer página propia.

## Cómo escribe el autor

Cuatro reglas de partida. Se cambian si la forma de escribir del autor es otra, salvo la última, de la que dependen las automatizaciones.

1. **Se registra el hecho, no la conversación.** Fuera el rodeo y lo dirigido a quien escucha. Una sola frase puede dar varias entradas.
2. **La entrada se sostiene sola.** Se va a leer en años, sin el resto del día. Las personas se nombran con su rol la primera vez y "el otro día" se convierte en una fecha.
3. **No se agrega lo que no se dijo.** Lo que un hecho sugiere se propone, no se da por hecho.
4. **El pendiente va en infinitivo y su cierre repite el mismo texto.** De esto depende que cerrar un pendiente funcione sin que nadie tenga que interpretar nada.
