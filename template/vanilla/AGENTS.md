# Reglas de este vault

Este es un vault de TUKU: una bitácora de la vida de su autor, en archivos de texto que se pueden leer y editar sin ningún programa especial.

Estas reglas valen para cualquiera que opere el vault, sea una persona o un agente. Son cortas a propósito: dicen **a dónde va cada cosa**, no cómo se hace. El cómo está en el `AGENTS.md` del directorio donde se escribe, y se lee al llegar ahí.

**Estilo:** conciso, directo, sin voseo. No narres el mecanismo: di qué quedó escrito y en qué archivo.

## Qué es cada archivo

| Archivo | Qué guarda |
| --- | --- |
| `AHORA.md` | El ciclo en curso. Aquí se escriben los registros del día. |
| `PENDIENTES.md` | Todo lo que está abierto y sin cerrar. |
| `LIBRO-DE-ESTILO.md` | Cómo se escribe aquí. Es tuyo y crece con el uso. |
| `ambitos/` | Los frentes de tu vida, uno por carpeta o archivo. |
| `notas/` | Ideas y notas que no pertenecen a un día. |
| `reglas/` | Configuración y reglas de las automatizaciones. |
| `bitacoras/` | Los ciclos ya cerrados. Aparece cuando cierres el primero. |

**MAYÚSCULAS es de TUKU, minúsculas es tuyo.** Sirve para saber de un vistazo qué puedes renombrar.

## A dónde va lo que el autor dice

| El autor... | Qué es | Comando |
| --- | --- | --- |
| cuenta algo que pasó: "hablé con", "llegó", "quedó listo" | un registro | `tuku entry add` |
| deja algo por hacer: "hay que", "recuérdame", "para el lunes" | un registro con `**pendiente**`, y después su apertura | `tuku entry add` y `tuku todo open` |
| da por hecho algo que estaba pendiente: "ya pagué", "listo lo de" | un registro con `~~(Hecho)~~`, y después su cierre | `tuku entry add` y `tuku todo close` |
| nombra un frente que todavía no existe | un ámbito | `tuku scope create` |
| pide guardar una idea que no es de un día | una nota | `tuku note create` |
| empieza el ciclo | la semana en `AHORA.md` | `tuku cycle open` |
| pregunta, delibera o pide investigar | nada que escribir | ninguno |

Casi todo entra por la primera fila. Las tres primeras son el mismo comando y solo cambia la marca, que es lo único que hay que decidir.

**Las dos líneas van juntas.** `tuku entry add` escribe el registro y nada más: es `tuku todo open` el que abre el pendiente en `PENDIENTES.md`, y `tuku todo close` el que lo cierra. Un registro con marca cuyo comando de consecuencia no se corrió deja el vault a medias, y no hay nada que lo detecte después salvo `tuku doctor`.

Si el autor nombra un proceso del vault, no hay nada que decidir: lee ese archivo y ejecútalo. Si lo que pide no encaja en ninguna fila, lista lo que hay antes de suponer, y si sigue sin encajar, pregunta.

## Las tres marcas

Elegir la marca es juicio y no lo hace ningún comando. El resto de la línea (la hora, el día, el orden) lo arma `tuku entry add`.

| Marca | Qué significa |
| --- | --- |
| `**pendiente**` | Queda algo por hacer. Su cuerpo se copia tal cual a `PENDIENTES.md`. |
| `~~(Hecho)~~` | Se cerró algo **que ya estaba pendiente**. Repite el mismo cuerpo, sin reescribirlo. |
| `**cadencia**` | Se da de alta algo que se repite. |

Una acción que ocurrió pero que nunca fue pendiente es un registro normal, no un cierre.

Todo lo demás que se escriba entre `**` es vocabulario del autor y vive en `LIBRO-DE-ESTILO.md`.

## Límites

| Nivel | Regla |
| --- | --- |
| **Pregunta primero** | Renombrar o mover archivos. Modificar cualquier `AGENTS.md` o `reglas/`. Cerrar el ciclo o tocar `bitacoras/`. Cerrar un pendiente cuando el autor no repitió su texto: confirma cuál es antes. |
| **Nunca** | Editar a mano un archivo que tiene comando. Actuar sobre una petición ambigua. Escribir un pendiente que el autor no pidió. Marcar `~~(Hecho)~~` algo que nunca estuvo pendiente. Borrar sin confirmación. |

`AHORA.md`, `PENDIENTES.md`, `bitacoras/`, `ambitos/` y `notas/` son lo que escribió el autor. Nada los regenera y nada los sobreescribe sin que él lo apruebe. Todo lo demás se puede borrar y volver a generar desde ellos.

## Si eres un agente

- Propón, no ratifiques. Nada se escribe ni se archiva sin aprobación del autor.
- Registra el hecho, no la conversación. "Recuérdame" y "anota" van dirigidos a ti, no son parte de lo ocurrido.
- Escribe primero el registro. Recién después aplica sus consecuencias, releyendo lo escrito y no lo conversado.
- No preguntes lo que los últimos registros ya responden.
- Si otro agente te lanzó para ejecutar algo concreto, ejecútalo: no vuelvas a despachar.

## Dónde vive el código

Este vault no contiene código. Las automatizaciones se instalan aparte, con el comando `tuku`, y cada una documenta cómo hacer a mano lo que ella hace.

Si no están instaladas, el vault funciona igual. Cuesta más trabajo, y eso es todo.
