---
type: Style Guide
---

# Libro de estilo

> Las reglas de escritura del autor. Este archivo es suyo: empieza con lo mínimo y crece cuando el uso revele una regla que valga la pena fijar.

Cómo funciona el sistema no se explica aquí, está en `AGENTS.md`. Aquí va solo el vocabulario que elige el autor.

## El autor

**Nombre del autor:** por declarar. El instalador lo pregunta al crear el vault; si se deja en blanco, el autor lo escribe aquí cuando quiera.

El sistema escribe en primera persona y esa primera persona es el autor. Cuando su nombre aparece en un dictado, se refiere a él y no a un tercero.

## Los tres encabezados que siguen son contrato

Las automatizaciones leen las tablas que siguen buscando estos encabezados exactos. Las **filas** se agregan, se quitan o se cambian cuando haga falta. Si se renombra un **encabezado**, las automatizaciones dejan de encontrar el vocabulario.

Las tres marcas con efecto mecánico (`**pendiente**`, `~~(Hecho)~~` y `**cadencia**`) no son vocabulario del autor: son de TUKU y están descritas en `AGENTS.md`. No van en estas tablas ni se renombran, y conviene no usar esas palabras para nombrar otra cosa.

### Clasificaciones

De qué clase es cada registro. Nadie las valida en forma estricta: si se usa una que no está en la tabla, se acepta y se formaliza después.

| Clasificación | Qué significa |
| --- | --- |
| `progreso` | Avance concreto en algo que estaba en curso. |
| `decisión` | Una elección tomada, con su razón. |
| `fricción` | Algo que costó ejecutar o que bloqueó al autor. |
| `señal` | Un patrón o un hecho externo que merece atención más allá de hoy. |
| `nota` | Un hecho que no calza en las anteriores. |

La distinción que más se usa es `señal` contra `fricción`: la señal es algo que se observa, la fricción es algo que pesó. Sin esa distinción, todo lo desagradable termina siendo fricción.

### Horizontes

Los plazos a los que puede estar asignado un pendiente dentro de la tabla de `PENDIENTES.md`.

| Horizonte | Qué agrupa |
| --- | --- |
| `esta semana` | Lo comprometido para la semana en curso. |
| `próxima semana` | Lo que va a la semana siguiente. |
| `fin de mes` | Lo que debe estar antes de que termine el mes. |

Un pendiente nace por defecto en el ciclo en curso (`esta semana`), o se posterga a un escalón siguiente. Cuando tiene un día exacto asignado, pasa a `con fecha`, que es un horizonte del sistema.

Se escriben tal como van en la columna **Horizonte** de `PENDIENTES.md`, con espacios: es el mismo texto en los dos sitios, y el comando también acepta la forma con guion (`esta-semana`).

Estos tres nombres son del autor: si el ritmo no es la semana sino el turno, la quincena o la temporada, se renombran en esta tabla y el sistema sigue funcionando igual. La escalera es la que importa, no cómo se llame cada escalón.

### Tipos de nota

Las notas pueden ser libres. Algunas, sobre cosas que se repiten, conviene que sigan una plantilla.

| Tipo | Para qué | Cuidado |
| --- | --- | --- |
| `persona` | Trabajar mejor con alguien con quien el autor trata seguido. | Se escribe solo lo que se le mostraría a esa persona. |

Empieza con uno. Los demás aparecen cuando algo se repite lo suficiente como para merecer página propia.

## Las plantillas viven en `reglas/`

Lo que TUKU genera se genera desde una plantilla, y las plantillas son del autor: están en `reglas/plantilla/` y se editan como cualquier otro archivo del vault.

`reglas/plantilla/AHORA.md` es la del ciclo: su frontmatter y los siete encabezados de día. Dónde termina el ciclo lo dice `to`, no hace falta marcarlo en el cuerpo. `tuku cycle lint` revisa ese frontmatter.

## Cadencias

Una cadencia es algo que vuelve: se declara una vez y emite un pendiente con fecha cada vez que toca. Sin cadencias TUKU registra lo que le cuentas, pero no te avisa de nada.

Viven en archivos `CADENCIAS.md`, uno por carpeta, y **se leen en cascada**: las de una carpeta valen para todo lo que cuelga de ella. Las de `ambitos/CADENCIAS.md` valen para todos los ámbitos; las de `ambitos/personal/CADENCIAS.md` valen solo dentro de ese ámbito. No hay que declarar el alcance dentro de la cadencia, lo dice la carpeta donde está escrita.

Cada cadencia es un encabezado `##` con tres campos de máquina y dos de persona:

```markdown
## Gastos comunes del arriendo

**Cuándo:** día exacto 10, mensual
**Emite:** pendiente con fecha
**Texto:** pagar y enviar comprobante de gastos comunes a [[carmen-navarro]]

### Procedimiento
Pagado en el portal, con el comprobante enviado por WhatsApp el mismo día.

### Historia
- 2026-08-09: dos veces quedó sin enviar el comprobante y hubo cobro duplicado.
```

| Campo | Para quién | Qué hace |
| --- | --- | --- |
| `Cuándo` | máquina | La condición que dispara |
| `Emite` | máquina | Qué produce: un pendiente con fecha, un reporte, el propio `AHORA.md` |
| `Texto` | máquina | El cuerpo literal del pendiente, se inyecta sin redactar nada. Solo si emite un pendiente |
| `Procedimiento` | persona | Cómo se ve el resultado cuando está hecho, no los pasos |
| `Historia` | persona | Lo aprendido, fechado. Por qué la cadencia quedó así |

Lo más común es emitir un pendiente con fecha, que aparece en el día que le toca de `AHORA.md`. No es lo único: las cadencias del ciclo emiten el archivo del ciclo, y ya vendrán reportes y otras cosas. La lista de destinos no está cerrada. `Texto` solo tiene sentido cuando lo que se emite es un pendiente.

`Historia` es lo que evita que una cadencia se simplifique por parecer arbitraria: una línea con fecha explicando qué salió mal vale más que la regla sola.

Escribe una cadencia la próxima vez que te acuerdes de algo tarde. Eso es lo que se declara acá: pagos que vuelven cada mes, controles de salud anuales, permisos y seguros por renovar, fechas que se lamentan después y no antes.

## OKF

**Qué es.** [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) es un formato abierto de Google para que personas y agentes compartan conocimiento: markdown con un bloque YAML arriba, un concepto por archivo, sin herramientas obligatorias. TUKU lo usa porque describe lo que ya hacía, y porque un vault en OKF lo entiende algo que nunca oyó hablar de TUKU.

**Cómo.** Un campo es obligatorio, `type`, y dice qué clase de archivo es. Los nombres van en inglés, como los comandos `tuku`, porque son superficie experta: quien los edita ya sabe lo que hace. Lo que escribe el autor sigue siendo el cuerpo, en castellano.

**Cuándo.** En todo archivo del vault que guarde conocimiento. Los `AGENTS.md` quedan fuera: son reglas de operación, no conocimiento.

![Tipos de archivo](reglas/types.md)

Un `Logbook` lleva además `status`, que vale `draft` mientras el ciclo está abierto y `stable` cuando se archiva y deja de tocarse, y `from` y `to`, el rango de fechas que cubre. `AHORA.md` y una bitácora cerrada son el mismo `type`: lo que los distingue es `status`.

## Cómo escribe el autor

Cuatro reglas de partida. Se cambian si la forma de escribir del autor es otra, salvo la última, de la que dependen las automatizaciones.

1. **Se registra el hecho, no la conversación.** Fuera el rodeo y lo dirigido a quien escucha. Una sola frase puede dar varios registros.
2. **El registro se sostiene solo.** Se va a leer en años, sin el resto del día. Las personas se nombran con su rol la primera vez y "el otro día" se convierte en una fecha.
3. **No se agrega lo que no se dijo.** Lo que un hecho sugiere se propone, no se da por hecho.
4. **El pendiente va en infinitivo y su cierre repite el mismo texto.** De esto depende que cerrar un pendiente funcione sin que nadie tenga que interpretar nada. El campo `Texto` de una cadencia se escribe igual, porque es el pendiente que esa cadencia va a emitir.
