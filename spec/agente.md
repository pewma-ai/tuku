# spec · agente

> Todo lo de las demás specs es independiente de quién ejecute. Esto no: son las reglas para cuando el ejecutor es un agente de IA. Si cambia el arnés o el modelo, esta spec cambia y las demás no.
>
> Acá está **cómo se comporta** el agente. A dónde va lo que el autor dice, antes de todo esto, es [despacho.md](despacho.md).

## Qué se inyecta y cuándo

Al **inicio de sesión**, una sola vez y solo cuando se va a registrar algo en una bitácora, se inyectan en silencio:

- El **contexto reciente**, generado por comando desde `AHORA.md`.
- El **vocabulario del autor**, generado por comando desde los frontmatter de `ambitos/`.

Ninguno de los dos es un archivo: son la salida de un comando que se ejecuta en ese momento (ver [`README.md`](README.md), árbol de directorios). Quedan en **caché de sesión** y no se releen en cada turno. Una sesión que no va a escribir bitácora no necesita ninguno de los dos.

Si el arnés no sabe ejecutar comandos y solo lee archivos, hay que materializarlos, y ahí reaparece el problema de que envejecen. Eso es limitación del arnés, no del diseño, y por eso vive en esta spec y no en [`flujo-informacion.md`](flujo-informacion.md).

## El agente compila intención en comandos

Lo que el agente produce no son archivos, son **llamadas a `tuku`**. Recibe la intención del autor en lenguaje natural y la traduce a una secuencia de comandos; la ejecución la hace el comando, que es determinista y está especificado en [cli.md](cli.md).

Eso confina el no determinismo a **elegir** la llamada, nunca a ejecutarla. Un modelo distinto elige distinto, pero ninguno puede producir un vault mal formado, porque no escribe: el que escribe es el comando, y el comando conoce el formato. El agente pasa a ser reemplazable sin que el vault dependa de cuál se usó.

**El agente no necesita el vault en contexto.** No carga `AHORA.md` para saber en qué día va un registro, no memoriza la forma de los encabezados ni las reglas de cómo un pendiente llega a su ámbito ([pendientes.md](pendientes.md)). Todo eso lo sabe el comando. Lo que el agente carga es lo que necesita para **decidir**, no para escribir, que es justo lo que la sección anterior inyecta.

De ahí también la prohibición: **editar a mano un archivo que tiene comando** deja el archivo bien formado y ninguna consecuencia aplicada, y es el modo de falla más caro del sistema porque no deja señal. Cómo se enuncia esa prohibición en el vault es [despacho.md](despacho.md).

Esto solo se sostiene si la salida del comando alcanza. Ahorrar contexto sin salida diagnóstica es operar a ciegas: la regla de [cli.md](cli.md) de que todo error nombre el defecto y la corrección es la que paga este ahorro. Las dos cosas se diseñan juntas o ninguna funciona.

Consecuencia de segundo orden, más útil que el ahorro: una sesión queda reducida a una lista de comandos. Se relee, se compara y se vuelve a ejecutar, que es lo que hace del sistema algo versionable y no una conversación perdida.

## Reparto entre LLM y script

| Paso | Naturaleza | Ejecutor |
| --- | --- | --- |
| 1 a 3, entender y situar | juicio | LLM |
| 4, redactar el registro | los campos son juicio, la línea es formato | LLM llena los campos, `tuku entry add` construye la línea |
| 5, aplicar consecuencias | mecánico en su mayoría | comando |

El paso 4 estaba repartido en el tiempo ("LLM hoy, script cuando el formato se estabilice") y ahora lo está por campo, que es un corte más firme: el formato de la línea ya está fijo en [bitacora.md](bitacora.md), así que construirla es del script desde ahora. Lo que nunca pasa al script es elegir el ámbito, la clasificación o cuántos registros da un dictado. Ver [cli.md](cli.md), "qué es dueño el comando".

Como el cierre conserva el texto del pendiente sin reescribirlo, el paso 5 para pendientes es **enteramente determinista**: abrir es copiar el cuerpo, cerrar es encontrar ese mismo cuerpo y borrarlo. Ninguna de las dos necesita LLM. El juicio queda entero en los pasos 1 a 3.

**Excepción: el cierre no literal.** `~~(Hecho)~~` cierra repitiendo el texto exacto del pendiente ([`bitacora.md`](bitacora.md)), pero un dictado real no siempre lo repite palabra por palabra. Cuando el emparejamiento no es literal, ya no es paso 5 sino paso 3: hay que decidir a qué pendiente abierto corresponde, y eso es juicio del agente, no lectura mecánica. Ante la duda, se confirma con el autor antes de cerrar; cerrar el pendiente equivocado no tiene forma de deshacerse sola.

## Conducta

- Proponer, nunca ratificar. Las propuestas esperan aprobación del autor.
- Silencio por defecto. No anunciar el mecanismo ni narrar la inyección de contexto.
- No preguntar lo que el contexto reciente ya responde.
