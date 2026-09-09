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
| deja algo por hacer: "hay que", "recuérdame", "para el lunes" | un registro con `**pendiente**` | `tuku entry add` |
| da por hecho algo que estaba pendiente: "ya pagué", "listo lo de" | un registro con `~~(Hecho)~~` | `tuku entry add` |
| nombra un frente que todavía no existe | un ámbito | `tuku scope create` |
| pide guardar una idea que no es de un día | una nota | `tuku note create` |
| empieza el ciclo | la semana en `AHORA.md` | `tuku cycle open` |
| pregunta, delibera o pide investigar | nada que escribir | ninguno |

Casi todo entra por la primera fila. Las tres primeras son el mismo comando y solo cambia la marca, que es lo único que hay que decidir.

**Un registro es un comando, y sus consecuencias son parte de escribirlo.** `tuku entry add` deja la línea en `AHORA.md`, actualiza las páginas de ámbito y, si la línea lleva marca, aplica lo que esa marca declara: `**pendiente**` abre el pendiente en `PENDIENTES.md` y `~~(Hecho)~~` lo cierra. No hay una segunda llamada que recordar.

Le pasas los campos, no la línea; el formato lo arma él:

```
tuku entry add --day 2026-08-11 --hour 14:20 --scope personal \
  --body "**pendiente**: avisar de los gastos comunes a la administradora"
```

Sin `--day` es hoy, sin `--hour` es ahora, y un pendiente nace en el primer escalón de `### Horizontes` del libro de estilo. Para uno que va a otro escalón o lleva fecha, `--horizon` y `--when`.

Si el autor nombra un proceso del vault, no hay nada que decidir: lee ese archivo y ejecútalo. Si lo que pide no encaja en ninguna fila, lista lo que hay antes de suponer, y si sigue sin encajar, pregunta.

## El ámbito

Cada registro dice a qué frente pertenece. Va en `--scope`, sin corchetes.

Usa uno que exista en `ambitos/`. Si ninguno calza, es `personal`, que siempre está. Y si el autor nombra un frente que todavía no existe, escríbelo en el cuerpo en palabras y sigue: el día que se cree, las menciones anteriores se vuelven enlaces solas.

## Las tres marcas

Elegir la marca es lo único que es juicio. Va al principio de `--body`, y el resto de la línea (la hora, el día, el ámbito, el orden) lo arma `tuku entry add`.

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
- Un hecho, un comando. Si te descubres corriendo dos para un mismo hecho, revisa la tabla: casi siempre el segundo ya lo hizo el primero.
- No preguntes lo que los últimos registros ya responden.
- Si otro agente te lanzó para ejecutar algo concreto, ejecútalo: no vuelvas a despachar.

## Dónde vive el código

Este vault no contiene código. Las automatizaciones se instalan aparte, con el comando `tuku`, y cada una documenta cómo hacer a mano lo que ella hace.

Si no están instaladas, el vault funciona igual. Cuesta más trabajo, y eso es todo.
