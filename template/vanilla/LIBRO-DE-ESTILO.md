---
type: Style Guide
---

# Libro de estilo

> Cómo opera TUKU en este vault, entidad por entidad. Es de TUKU: viene del repositorio y se reemplaza al actualizarlo, así que no se edita. Lo que decide el autor vive en `reglas/` y cada capítulo lo transcluye al final. Un agente lo lee con `tuku context style`.

## Para qué sirve

TUKU registra lo que el autor cuenta, lo ordena en archivos Markdown y le recuerda lo que prometió. El autor dicta o escribe; los comandos `tuku` escriben los archivos; el agente decide qué comando corre. Este libro dice qué hace `tuku` con cada cosa, y lo que cambia de un autor a otro está en `reglas/`.

## Cómo escribe el autor

El sistema escribe en primera persona y esa primera persona es el autor. Cuando su nombre aparece en un dictado, se refiere a él y no a un tercero. Las observaciones sobre una persona se redactan como descripción y nunca como norma. Este libro se redacta en tercera persona, para que sirva igual al autor, a un secretario y a un agente.

![El autor](reglas/autor.md)

![El lenguaje](reglas/lenguaje.md)

## Registro

Un registro es una línea de la bitácora, que es `AHORA.md` mientras el ciclo está abierto: `- HH:MM - [ámbito](ruta) clasificación: cuerpo`. `tuku entry create` la escribe en el día que toca, y si no se le dice el día ni la hora usa HOY y el momento actual. La clasificación es opcional y del autor.

Tres marcas tienen efecto mecánico y son de TUKU: `**pendiente**`, `(Hecho)` y `**cadencia**`. No son vocabulario del autor, no van en sus tablas ni se renombran, y conviene no usar esas palabras para nombrar otra cosa.

![Registro](reglas/bitacora.md)

## Pendiente

Un registro con `**pendiente**` abre una fila en la tabla de `PENDIENTES.md`, ordenada por horizonte y por fecha de vencimiento. `tuku todo open` lo abre y `tuku todo close` lo cierra, y ambos dejan constancia en la bitácora. El pendiente va en infinitivo y su cierre repite el mismo texto: de eso depende que cerrarlo funcione sin que nadie interprete nada.

Un pendiente nace en el primer horizonte, o en el que se le indique. Con un día exacto pasa a `con fecha`, que es un horizonte del sistema. Lo que venció y sigue abierto sale como atrasado en `tuku context todo`.

![Pendiente](reglas/pendientes.md)

## Ciclo

El ciclo en curso es `AHORA.md`; los cerrados están en `bitacoras/`. `tuku process cycle` abre el siguiente a partir de `reglas/plantilla/AHORA.md`, sin hoyos ni solapes con el anterior, y el nombre del nuevo avanza por la lista `cycle_name` de la configuración. Con el nombre `semana` el rango es de lunes a domingo y se deduce; con cualquier otro hay que decir hasta qué día va.

![Ciclo](reglas/ciclo.md)

## Ámbito

Un ámbito es un frente de actividad con identidad propia: una carpeta en `ambitos/` con su página. `tuku scope create` lo crea, y `tuku context scope` lista cada uno con su ruta y sus keywords, que son las palabras que lo nombran en un dictado. Cada registro y cada pendiente apunta a un ámbito; si no se dice otro, es el de `scope_default`.

![Ámbito](reglas/ambitos.md)

## Nota

Una nota es un archivo de `notas/` sobre algo que no pertenece a un día. `tuku note create` la escribe y deja constancia en la bitácora; con `--subtype` sigue la plantilla de ese tipo. Cada nota cierra con `## Ver además`, donde cada enlace dice para qué conecta. `tuku context note` ofrece al agente las últimas notas de cada tipo enlazable, para que enlace la primera mención al registrar.

![Nota](reglas/notas.md)

## Cadencia

Una cadencia es algo que vuelve: se declara una vez y emite un pendiente con fecha cada vez que toca. Sin cadencias TUKU registra lo que le cuentas, pero no te avisa de nada.

Viven en archivos `CADENCIAS.md`, que se crean en la carpeta donde se declara la primera, y **se leen en cascada**: las de una carpeta valen para todo lo que cuelga de ella. Las de `ambitos/CADENCIAS.md` valen para todos los ámbitos; las del `CADENCIAS.md` de un ámbito valen solo dentro de él. La carpeta donde está escrita dice el alcance. `tuku context cadence` las junta todas, cada una con el `CADENCIAS.md` de donde viene.

Cada cadencia es un encabezado `##` con tres campos de máquina y dos de persona:

```markdown
## Gastos comunes del arriendo

**Cuándo:** día exacto 10, mensual
**Emite:** pendiente con fecha
**Texto:** pagar y enviar comprobante de gastos comunes a [carmen-navarro](../../notas/carmen-navarro.md)

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

`Texto` se escribe como cualquier pendiente: en infinitivo, porque es el pendiente que esa cadencia va a emitir. `Historia` evita que una cadencia se simplifique por parecer arbitraria: una línea con fecha explicando qué salió mal vale más que la regla sola. Escribe una cadencia la próxima vez que te acuerdes de algo tarde.

![Cadencia](reglas/cadencias.md)

## Tipos de archivo

**Qué es.** [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) es un formato abierto de Google para que personas y agentes compartan conocimiento: markdown con un bloque YAML arriba, un concepto por archivo, sin herramientas obligatorias. TUKU lo usa porque describe lo que ya hacía, y porque un vault en OKF lo entiende algo que nunca oyó hablar de TUKU.

**Cómo.** Un campo es obligatorio, `type`, y dice qué clase de archivo es. Los nombres van en inglés, como los comandos `tuku`, porque son superficie experta. Lo que escribe el autor sigue siendo el cuerpo, en castellano. Se declara en todo archivo que guarde conocimiento; los `AGENTS.md` quedan fuera porque son reglas de operación.

> [!warning] Estos nombres no son del autor
> Son el contrato con OKF. Renombrar uno rompe los comandos y deja el vault ilegible para cualquier herramienta que hable OKF. Los tipos propios del autor van en la tabla de abajo, y un nombre no puede repetir uno de esta.

| `type` | Qué archivo | Se reconoce por |
| --- | --- | --- |
| `Logbook` | `AHORA.md` y todo lo de `bitacoras/` | Registros fechados, en orden de hora |
| `Todo` | `PENDIENTES.md` | Lo abierto, agrupado por horizonte |
| `Derived` | `ambitos/PENDIENTES-AMBITOS.md` | Archivos generados automáticamente desde fuentes canónicas |
| `Scope` | Los archivos de `ambitos/` | Un frente de la vida del autor |
| `Note` | Los archivos de `notas/` | Algo que no pertenece a un día |
| `Cadence` | Los `CADENCIAS.md` | Lo que vuelve |
| `Capacity` | Los `CAPACIDAD.md` | Lo que rinde un día, y lo que se va antes |
| `Config` | Los archivos de `reglas/` | Lo que las automatizaciones necesitan saber |
| `Style Guide` | `LIBRO-DE-ESTILO.md` | Cómo opera TUKU, entidad por entidad |

Un `Logbook` lleva además `status`, que vale `draft` mientras el ciclo está abierto y `stable` cuando se archiva y deja de tocarse, y `from`, `to` y `cycle`, el rango de fechas que cubre y el nombre del ciclo. `AHORA.md` y una bitácora cerrada son el mismo `type`: lo que los distingue es `status`.

![Tipos propios](reglas/types.md)
