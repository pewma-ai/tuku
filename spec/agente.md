# spec · agente

> Todo lo de las demás specs es independiente de quién ejecute. Esto no: son las reglas para cuando el ejecutor es un agente de IA. Si cambia el arnés o el modelo, esta spec cambia y las demás no.

## Qué se inyecta y cuándo

Al **inicio de sesión**, una sola vez y solo cuando se va a registrar algo en una bitácora, se inyectan en silencio:

- El **contexto reciente**, generado por janitor desde `AHORA.md`.
- El **vocabulario del autor**, generado por janitor desde los frontmatter de `ambitos/`.

Ninguno de los dos es un archivo: son la salida de un janitor que se ejecuta en ese momento (ver [`README.md`](README.md), árbol de directorios). Quedan en **caché de sesión** y no se releen en cada turno. Una sesión que no va a escribir bitácora no necesita ninguno de los dos.

Si el arnés no sabe ejecutar comandos y solo lee archivos, hay que materializarlos, y ahí reaparece el problema de que envejecen. Eso es limitación del arnés, no del diseño, y por eso vive en esta spec y no en [`flujo-informacion.md`](flujo-informacion.md).

## Carga diferida de reglas

Las reglas de cada consecuencia no viajan en el contexto base. Se abre `reglas/<consecuencia>.tuku.md` solo cuando el paso 3 del flujo (ver [`flujo-informacion.md`](flujo-informacion.md)) detectó que esa consecuencia aplica. Una entrada sin consecuencias termina en el paso 4 sin haber cargado nada extra.

Esto es lo que hace que la lista de consecuencias pueda crecer sin encarecer cada sesión: se paga solo por la que se usa.

## Reparto entre LLM y script

| Paso | Naturaleza | Ejecutor |
| --- | --- | --- |
| 1 a 3, entender y situar | juicio | LLM |
| 4, redactar la entrada | formato | LLM hoy, script cuando el formato se estabilice |
| 5, aplicar consecuencias | mecánico en su mayoría | janitor |

Como el cierre conserva el texto del pendiente sin reescribirlo, el paso 5 para pendientes es **enteramente determinista**: abrir es copiar el cuerpo, cerrar es encontrar ese mismo cuerpo y borrarlo. Ninguna de las dos necesita LLM. El juicio queda entero en los pasos 1 a 3.

**Excepción: el cierre no literal.** `~~(Hecho)~~` cierra repitiendo el texto exacto del pendiente ([`bitacora.md`](bitacora.md)), pero un dictado real no siempre lo repite palabra por palabra. Cuando el emparejamiento no es literal, ya no es paso 5 sino paso 3: hay que decidir a qué pendiente abierto corresponde, y eso es juicio del agente, no lectura mecánica. Ante la duda, se confirma con el autor antes de cerrar; cerrar el pendiente equivocado no tiene forma de deshacerse sola.

## Conducta

- Proponer, nunca ratificar. Las propuestas esperan aprobación del autor.
- Silencio por defecto. No anunciar el mecanismo ni narrar la inyección de contexto.
- No preguntar lo que el contexto reciente ya responde.
