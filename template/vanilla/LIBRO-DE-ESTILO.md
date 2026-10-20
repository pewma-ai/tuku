---
type: Style Guide
---

# Libro de estilo

> Cada capítulo se basta solo para su tarea: antes de escribir algo, se lee su capítulo y nada más, una vez por sesión. Si un capítulo depende de otro, lo dice en «Lee también». Un agente lo lee con `tuku context style --chapter NOMBRE`, y todo el libro con `tuku context style`.

## Propósito del vault

Aquí se registra lo que el autor cuenta, se ordena en archivos Markdown y eso permite recordar, priorizar y tomar decisiones. El autor dicta o escribe; los comandos `tuku` escriben los archivos y hacen cumplir lo determinista; el agente decide qué comando corre. Este libro dice solo lo que un comando no puede verificar.

## Autor

El vault se escribe en primera persona, en nombre del autor. Cuando su nombre aparece en un dictado, se refiere a él y no a un tercero. Lo que se anota sobre otra persona describe lo observado y no generaliza: «Patricia responde por la tarde», y no «hay que escribirle por la tarde».

![El autor](reglas/autor.user.md)

## Registro

Un registro es una línea de la bitácora (`AHORA.md` mientras el ciclo está abierto): `- HH:MM - [ámbito](ruta) clasificación: cuerpo`. Debe cumplir:
1. **Un comando por registro.** Una frase del autor puede dar varios registros: un comando por cada uno, y nunca dos para un mismo hecho.
2. **El hecho, no la conversación.** Lo dirigido a quien escucha («recuérdame», «anota», «guárdame») queda fuera.
3. **Autocontenido.** Se va a leer en años, sin el resto del día. Las personas se nombran con su rol la primera vez y «el otro día» se convierte en una fecha.
4. **Precisión.** No se agrega información inferida.
5. **El día fuera del ciclo.** Si hoy cae fuera del ciclo abierto, el registro va al último día del ciclo que ya tiene registros, con ese día explícito en `--at`. Un ciclo que quedó atrás no es motivo para cerrarlo: eso lo decide el autor.
6. **Una nota nombrada se enlaza.** `tuku context` ofrece las últimas notas de cada tipo enlazable con su título y sus `aliases`. La primera mención de una va como enlace en el `--body`, con el texto que dijo el autor: `llamé a [don Rodolfo](notas/rodolfo-cifuentes.md)`. Si el nombre calza con dos notas, se pregunta; si con ninguna, no se enlaza ni se inventan rutas.

> [!example] Ejemplos tuku
> ```bash
> tuku entry create --body "entregué 40 cuadernos" --scope colegio-los-robles  # sin --at: hoy y ahora. Sin --scope: el por defecto.
> tuku entry create --body "**señal**: la administradora responde tarde" --at "2026-08-11 09:12"
> ```

### Clasificaciones

Las clasificaciones son la clase de cada registro. Es opcional: un registro sin clasificación está bien escrito. Si se usa una desconocida, se acepta y `tuku` pregunta para formalizarla después. `**pendiente**` y `(Hecho)` están reservadas: las escriben `tuku todo open` y `tuku todo close`, y `entry create` las rechaza.

### Clasificaciones del autor

Estas son las clasificaciones regularmente usadas por el autor, modificar esta tabla si es necesario.

![Clasificaciones](reglas/clasificaciones.user.md)

## Pendiente

Un pendiente es un compromiso abierto: un registro con `**pendiente**` y una fila en la tabla de `PENDIENTES.md`. `tuku todo open` lo abre y `tuku todo close` lo cierra. Debe cumplir:
1. **Un comando abre y otro cierra.** Escriben el registro y la fila, y dejan constancia en la bitácora: no se suma un `entry create` ni se edita `PENDIENTES.md` a mano.
2. **En infinitivo y sin mayúscula inicial.** «pagar la sesión con el psicólogo», y no «Pagar la sesión» ni «hay que pagar la sesión».
3. **El cierre repite el texto.** `todo close` encuentra la fila por su detalle, palabra por palabra: de eso depende que cerrarlo funcione sin que nadie interprete nada.
4. **Dos fechas distintas.** `--at` es cuándo se prometió y nunca es un día futuro. `--due` es cuándo vence, con la hora si el autor la dijo («el viernes a las nueve»).
5. **Postergar es deliberado.** Sin `--due`, nace en el primer horizonte; con `--horizon`, en el que se diga. Lo que se pospone ciclo tras ciclo no era un pendiente sino una nota.

> [!example] Ejemplos tuku
> ```bash
> tuku todo open --body "pagar la sesión con el psicólogo"  # nace en el primer horizonte. Sin --scope: el por defecto.
> tuku todo open --body "pagar el arriendo" --due "2026-08-14 09:00" --scope personal
> tuku todo open --body "renovar el seguro" --horizon "próxima semana"
> tuku todo close "pagar la sesión con el psicólogo"  # repite el texto tal cual. Sin --at: hoy y ahora.
> ```

Un `warning` en la salida es una alerta y no un fallo: el comando procedió.

### Horizontes

Los horizontes son los plazos de `PENDIENTES.md`, del más cercano al más lejano. El primero es el ciclo en curso y se reconoce por su posición, no por su texto; `con fecha` es del sistema. Se escriben con espacios, y el comando también acepta guion (`esta-semana`).

### Horizontes del autor

![Horizontes](reglas/pendientes.user.md)

## Ciclo

El ciclo en curso es `AHORA.md`; los cerrados están en `bitacoras/`. `tuku process cycle` abre el siguiente, y cerrar el ciclo lo decide el autor, no el agente. Los ciclos y su orden están en la tabla del autor: el siguiente es el que sigue en ella. Con el nombre `semana` el rango es de lunes a domingo; con cualquier otro hay que decir hasta qué día va.

> [!example] Ejemplos tuku
> ```bash
> tuku process cycle --from 2026-08-17
> tuku process cycle --from 2026-08-11 --to 2026-08-18 --name turno
> ```

### Ciclos del autor

![Ciclo](reglas/ciclo.user.md)

## Ámbito

Un ámbito es un frente de actividad con identidad propia: una carpeta en `ambitos/` con su página. Las keywords son las palabras que lo nombran en un dictado, y un hecho que nombra una keyword es de ese ámbito aunque parezca no tener relación. Un ámbito puede vivir dentro de otro. Se crea cuando el autor lo pide, o cuando TUKU ve que algo aparece seguido sin página y lo propone: solo se crea con el sí del autor.

> [!example] Ejemplos tuku
> ```bash
> tuku scope create colegio-los-robles --keyword don-rodolfo,lr
> tuku scope create clientes-nuevos --parent negocio
> tuku scope update colegio-los-robles --keyword cuadernos
> ```

## Capacidad

La capacidad del autor vive en `ambitos/personal/CAPACIDAD.md` y se lee siempre al crear un ciclo nuevo, para estimar cuánto tiempo tiene. Si el autor lo considera necesario, un ámbito puede tener además su propio `CAPACIDAD.md`, con lo que cuesta sostener ese frente.

![Capacidad](ambitos/personal/CAPACIDAD.md)

## Nota

Una nota es un archivo de `notas/` sobre algo que no pertenece a un día. `tuku note create` la escribe. Debe cumplir:
1. **Solo si el autor la pide.** Lo que parezca merecer nota se propone y espera el sí.
2. **Deja una entrada en la bitácora**, con el enlace a la nota. La escribe el mismo `note create`: no se suma un `entry create`.
3. **Cierra con `## Ver además`**, donde cada enlace dice para qué conecta.
4. **Un tipo enlazable se enlaza al nombrarlo.** Si la columna `Enlazable` del tipo dice `sí`, `tuku context` ofrece sus últimas notas (hasta `context_note_limit`), y se enlazan como dice el capítulo Registro; dentro de una nota, la ruta es relativa a `notas/`. Una nota de un tipo no enlazable existe, pero nadie la enlaza sola.
5. **Una persona sigue una plantilla** (`--subtype persona`): el nombre completo como título; quién es y de dónde se conoce; los hechos, cada uno con la fecha del registro que lo sostiene; las inferencias aparte y marcadas como tales. Solo se infiere lo que sirve para trabajar mejor con ella. Los otros nombres con que se la nombra van en `aliases`.

> [!example] Ejemplos tuku
> ```bash
> tuku note create "Reunión con Viana" --body "Quedamos en revisar la cotización." --scope negocio
> tuku note create "Patricia Lillo" --subtype persona --body-file patricia.md --scope liceo-tecnico-andes
> ```

Lee también: Uso de Markdown y Formato OKF.

### Tipos de nota

![Tipos de nota](reglas/notas.user.md)

## Cadencia

Una cadencia es algo que vuelve: se declara una vez y genera un pendiente con fecha cada vez que toca. Se evalúan al cambiar de ciclo: al crear una semana, o el ciclo propio del autor, cada cadencia que cae en ese rango se convierte en un pendiente. No hay comando para declararla; se escribe en un `CADENCIAS.md`. Se leen en cascada: las de `ambitos/CADENCIAS.md` valen para todos los ámbitos, y las del `CADENCIAS.md` de un ámbito, solo dentro de él.

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
| `Texto` | máquina | El cuerpo literal del pendiente, en infinitivo. Solo si emite un pendiente |
| `Procedimiento` | persona | Cómo se ve el resultado cuando está hecho, no los pasos |
| `Historia` | persona | Lo aprendido, fechado. Por qué la cadencia quedó así |

Una línea de `Historia` con fecha, explicando qué salió mal, evita que una cadencia se simplifique por parecer arbitraria. Lee también: Uso de Markdown.

## Proceso

Un proceso es un procedimiento con nombre, escrito por el autor en `procesos/` («corre el cierre de mes»). `tuku process` los lista, y cuando el autor nombra uno, el agente lo lee y hace lo que dice. TUKU no trae ninguno propio.

## Estructura del vault

MAYÚSCULAS es de TUKU y minúsculas es del autor. `AHORA.md`, `PENDIENTES.md`, `bitacoras/`, `ambitos/` y `notas/` los escribe el autor, y nada los sobreescribe sin su aprobación; todo lo demás se regenera desde ellos. En `reglas/`, lo que termina en `.user.md` es del autor y TUKU nunca lo toca.

| Archivo | Qué guarda |
| --- | --- |
| `AHORA.md` | El ciclo en curso: aquí se escriben los registros del día |
| `PENDIENTES.md` | Todo lo que está abierto |
| `LIBRO-DE-ESTILO.md` | Estas convenciones, con las preferencias del autor incluidas |
| `ambitos/` | Los frentes de la vida del autor, uno por carpeta |
| `notas/` | Ideas que no pertenecen a un día |
| `procesos/` | Los procedimientos con nombre del autor |
| `reglas/` | Las preferencias del autor (`*.user.md`), la configuración y las skills (`skills/`) |
| `bitacoras/` | Los ciclos cerrados. Aparece al cerrar el primero |

Los archivos `.user.md` son la memoria del autor: cuando dice cómo prefiere que se haga algo, el agente lo condensa ahí. Las reglas de cada uno están en su frontmatter.

## Formato OKF

[OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) es un formato abierto de Google para que personas y agentes compartan conocimiento: Markdown con un bloque YAML arriba, un concepto por archivo, sin herramientas obligatorias. TUKU lo usa porque un vault en OKF lo entiende algo que nunca oyó hablar de TUKU.

Un campo es obligatorio, `type`, y dice qué clase de archivo es. Los nombres van en inglés. Se declara en todo archivo que guarde conocimiento; los `AGENTS.md` y los `SKILL.md` quedan fuera. Los `type` de TUKU son el contrato con OKF y no se renombran; uno propio del autor no puede repetir uno de estos.

| `type` | Qué archivo | Se reconoce por |
| --- | --- | --- |
| `Logbook` | `AHORA.md` y todo lo de `bitacoras/` | Registros fechados, en orden de hora |
| `Todo` | `PENDIENTES.md` | Lo abierto, agrupado por horizonte |
| `Derived` | `ambitos/PENDIENTES-AMBITOS.md` | Archivos generados automáticamente desde fuentes canónicas |
| `Scope` | Los archivos de `ambitos/` | Un frente de la vida del autor |
| `Note` | Los archivos de `notas/` | Algo que no pertenece a un día |
| `Cadence` | Los `CADENCIAS.md` | Lo que vuelve |
| `Capacity` | Los `CAPACIDAD.md` | Lo que rinde un día, y lo que se va antes |
| `Config` | `reglas/config.tuku.md` | Lo que las automatizaciones necesitan saber |
| `Style Guide` | `LIBRO-DE-ESTILO.md` y los `reglas/*.user.md` | Las convenciones del vault y lo que el autor decide |

Un `Logbook` lleva además `status` (`draft` mientras el ciclo está abierto, `stable` cuando se archiva), y `from`, `to` y `cycle`. Un `.user.md` lleva `editable: true`, `modified_time` (`null` hasta que se cambia) y `rules`.

### Tipos OKF propios

![Tipos propios](reglas/types.user.md)

## Configuración

Los valores que las automatizaciones necesitan saber de este vault.

![Configuración](reglas/config.tuku.md)

## Uso de Markdown

TUKU escribe CommonMark con las tablas y el tachado de GFM, y tres extensiones de Obsidian: el callout (`> [!todo] Título`), la transclusión (`![[archivo.md#^ancla]]`) y el ancla de bloque (`^ancla`). Lo que más se equivoca:
1. **Un párrafo es una sola línea.** El editor la ajusta; un salto manual a mitad de párrafo lo rompe en dos.
2. **Una línea en blanco** antes y después de una lista, una tabla o un bloque de código.
3. **Enlace relativo, no wikilink.** `[texto](ruta/relativa.md)`, con la ruta relativa al archivo que lo contiene. La transclusión es el único wikilink admitido.
4. **Un `|` dentro de una celda se escribe `\|`.**
5. **Lo que lee una máquina está a la vista:** un campo `**Campo:** valor`, una tabla o un encabezado, sin comentarios HTML con significado.
