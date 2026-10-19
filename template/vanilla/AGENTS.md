# Reglas de este vault

Un vault de TUKU: la bitácora de la vida de su autor, en archivos de texto que se leen y editan sin programas especiales.

Este archivo dice **a dónde va cada cosa**. El cómo está en el archivo que nombra la columna "Lee antes".

## Cómo te invocan

Mira cómo empieza el primer prompt de la sesión. Hay dos casos y no hay un tercero.

| El primer prompt... | Haces |
| --- | --- |
| empieza con `MAINTENANCE MODE`, en mayúsculas | No cargues nada más: ni `tuku context` ni ningún otro archivo. Sigue las instrucciones del prompt tal como están, sin despachar y sin preguntar. Lo que pide una decisión del autor queda sin escribir y va en tu respuesta final. Los Límites del final valen igual. |
| empieza con cualquier otra cosa | Es una interacción natural con el autor. Empieza con `tuku context` y despacha lo que dice con la tabla de abajo. |

`maintenance mode` en minúsculas, o la frase en medio del texto, no activa nada: es una interacción natural.

## Cómo trabajas con el autor

- **Al empezar, `tuku context`.** Trae los últimos días, los ámbitos con sus keywords, los pendientes abiertos, quién es el autor con su vocabulario y las últimas notas de cada tipo enlazable: con eso decides, sin abrir esos archivos. Cuando necesites el detalle de una entidad, `tuku context style --chapter Pendiente` (o `Registro`, `Nota`, `Ciclo`, `Ámbito`, `Cadencia`) trae el capítulo del libro con lo que el autor decidió.
- **Un pedido, un comando.** Ejecuta el comando de la fila con los campos que dio el autor. El comando valida, rechaza con la corrección y escribe todo lo derivado.
- **Si lo que dijo el autor puede querer decir dos cosas, pregunta.** No escribas hasta que conteste. «Quedamos al día con Fabina», con dos pendientes de Fabina abiertos: ¿es un registro, o cierra uno de los dos? «Le mandé el catálogo a la Paula», con dos Paulas: ¿a cuál? Una pregunta en una línea con las opciones; lo demás del dictado sigue su curso.
- **Atiende todo lo que el autor dijo, en su orden:** cada cosa que cuenta o pide es un comando o una respuesta. No termines con una sin atender.
- **Antes de registrar lo que el autor hizo, mira los pendientes de `tuku context`.** Si calza con un pendiente abierto es un cierre (`tuku todo close`); si calzan varios, pregunta cuál y no escribas nada (si la respuesta tampoco lo aclara, vuelve a preguntar: lo que solo el autor sabe no se busca en el vault); si ninguno, es un registro (`tuku entry create`). Fuera de eso no leas el vault: el comando conoce el formato, el día y el orden. Abre solo el archivo que la fila nombra en "Lee antes".
- **Enlaza las notas que el autor nombra.** `tuku context` lista, por cada tipo enlazable, sus últimas notas con su título y sus `aliases`. Si lo que dijo el autor nombra a una, escribe en el `--body` la primera mención como link a su ruta, con el texto que dijo el autor: `llamé a [don Rodolfo](notas/rodolfo-cifuentes.md)`. Dentro de una nota, la ruta es relativa a `notas/`: `(rodolfo-cifuentes.md)`. Si el nombre calza con dos notas, es una ambigüedad y se pregunta. Si ninguna calza, no enlazas: no inventes rutas. Los ámbitos no se enlazan en el cuerpo, los pone `--scope`.
- **Los comandos están en la tabla y en los ejemplos de abajo,** así que no consultes `-h` antes de ejecutar. Si uno rechaza, haz lo que su mensaje dice; solo si no basta, `tuku <comando> -h`.
- **No verifiques después.** El mensaje del comando dice qué quedó escrito. Cuando termina el último, respondes: no releas archivos ni explores el CLI.
- **Responde en una o dos frases:** qué quedó escrito, o la pregunta que falta; no cómo se hizo.

## Qué es cada archivo

| Archivo | Qué guarda |
| --- | --- |
| `AHORA.md` | El ciclo en curso. Aquí se escriben los registros del día. |
| `PENDIENTES.md` | Todo lo que está abierto. |
| `LIBRO-DE-ESTILO.md` | Cómo opera TUKU con cada entidad, con lo que decidió el autor en `reglas/`. Se lee con `tuku context style`. |
| `ambitos/` | Los frentes de la vida del autor, uno por carpeta. |
| `notas/` | Ideas que no pertenecen a un día. |
| `reglas/` | Reglas de las automatizaciones y configuración. |
| `bitacoras/` | Los ciclos cerrados. Aparece al cerrar el primero. |

MAYÚSCULAS es de TUKU, minúsculas es del autor.

## A dónde va lo que el autor dice

| El autor... | Lee antes | Comando |
| --- | --- | --- |
| cuenta algo que pasó: "hablé con", "llegó", "quedó listo" | nada; si el comando rechaza el día, `reglas/bitacora.tuku.md` | `tuku entry create` |
| deja algo por hacer: "hay que", "recuérdame", "para el lunes" | nada | `tuku todo open` |
| da por hecho algo que estaba pendiente: "ya pagué", "listo lo de" | nada | `tuku todo close` |
| nombra algo nuevo de lo que va a seguir hablando, un cliente, un proveedor, un proyecto: "ábrelo aparte" | `ambitos/AGENTS.md` | `tuku scope create` |
| dice que una cosa es parte de otra: "va dentro de" | `ambitos/AGENTS.md` | `tuku scope move` |
| dice con qué otras palabras nombra algo: "si te hablo de don Rodolfo, es Los Robles" | `ambitos/AGENTS.md` | `tuku scope update` |
| pide guardar una idea que no es de un día: "guárdame esto" | `reglas/notas.tuku.md` | `tuku note create` |
| empieza el ciclo: "empecemos la semana" | nada | `tuku process cycle` |
| corrige lo que quedó escrito: "no era eso, era el presupuesto" | nada | `tuku entry update` |
| dice que algo era de otro ámbito: "eso era de Los Robles" | nada | `tuku entry move` |
| cambia el nombre de un ámbito o de una nota: "cámbiale el nombre" | nada | `tuku scope rename`, `tuku note rename` |
| nombra un proceso del vault: "corre el cierre de mes" | ese proceso, en `procesos/` (`tuku process` los lista) | el que el proceso diga |
| pide algo que ninguna fila cubre | nada | se [reformula y se confirma](#lo-que-no-tiene-comando) |
| pregunta, delibera o pide investigar | nada | se responde |

```bash
tuku entry create --scope personal --body "revisé el contrato del arriendo" --at 10:30
tuku todo open --scope personal --body "renovar el seguro" --at 13:00
tuku todo open --scope personal --body "pagar el arriendo" --due "2026-08-14 09:00"
tuku todo close --at 16:45 "pagar el arriendo"
tuku scope create "casa de playa"
tuku note create "cómo se prorroga un arriendo" --scope personal --body "…" --at 21:15
tuku entry update --match "contrato" --body "revisé el contrato del arriendo con Carmen"
tuku entry move --match "Rodolfo" --scope colegio-los-robles
```

- **Los campos.** `--scope` es el nombre de una carpeta de `ambitos/` (`tuku context scope` las lista con sus keywords; si ninguno calza, `personal`). Un hecho que nombra una keyword es de ese ámbito aunque parezca no tener relación, y el cuerpo queda como lo dijo el autor. `--at "2026-08-11 09:12"` (o solo `09:12`) es cuándo pasó, cuándo prometió algo el autor o cuándo lo dio por hecho ("a la una, tengo que…", "a las siete, listo lo de…"), también en `todo open` y `todo close`; sin él el comando usa hoy y ahora, y en un día pasado sin hora el registro queda sin hora. `--due "2026-08-14 09:00"` es solo para cuándo vence un pendiente ("el viernes a las nueve", "mañana"), con la hora si el autor la dijo.
- **Corregir (`--match`).** En `entry update` y `entry move`, `--match` es un fragmento del cuerpo tal como está escrito, y el comando corrige el último registro que calza. Si el que se corrige es otro, pasa un fragmento más largo.
- **El cuerpo (`--body`).** Es el hecho, no la conversación: lo dirigido a ti ("recuérdame", "anota", "guárdame") se queda fuera, con todo lo que lo acompaña. No agregues lo que el autor no dijo. El pendiente va en infinitivo, sin mayúscula inicial ("pagar la sesión con el psicólogo"), y `todo close` repite ese texto sin reescribirlo. En `entry create` puede abrir con una clasificación: `**progreso**`, `**decisión**`, `**fricción**`, `**señal**` o `**nota**`.
- **Contarlo es pedirlo.** Si el autor cuenta algo, ejecuta el comando de su fila. No preguntes qué hacer con eso ni ofrezcas alternativas.
- **Lo tentativo espera.** Un compromiso con el día, la hora o la forma sin decidir ("quizás el jueves", "mejor el viernes", "todavía no sé") no se abre. Conversa con el autor y ejecuta `tuku todo open` cuando lo ratifique ("quedamos así"), con el último acuerdo y no con los anteriores.
- **"Lee antes" es lo único que abres antes de ejecutar.**
- **Un hecho, un comando.** El comando ya escribe su registro: `tuku todo open`, `tuku todo close`, `tuku note create` y `tuku scope create` lo dejan en la bitácora, así que no corras además `tuku entry create`.
- **Respeta el orden del dictado.** Cada hecho se registra en el vault tal como estaba en ese momento: un frente que el autor pide abrir más adelante no se crea antes.
- **Si un hallazgo nombra `tuku fix`, córrelo.** Si devuelve decisiones, plantéaselas al autor y espera su respuesta.

## Las tres marcas

Elegir la marca es lo único que es juicio. `**pendiente**` y `(Hecho)` los escriben `tuku todo open` y `tuku todo close`; las demás van al principio de `--body` de `tuku entry create`.

| Marca | Qué significa |
| --- | --- |
| `**pendiente**` | Queda algo por hacer: `tuku todo open`. |
| `(Hecho)` | Se cerró algo **que ya estaba pendiente**: `tuku todo close` con su cuerpo sin reescribirlo; el comando lo tacha. |
| `**cadencia**` | Se da de alta algo que se repite. |

Una acción que nunca fue pendiente es un registro normal, no un cierre. Cualquier otra palabra entre `**` es una clasificación del autor: `reglas/bitacora.md`, `## Clasificaciones`. Cómo se redacta un registro: `tuku context style --chapter Registro`.

## Lo que no tiene comando

1. Di en una frase qué vas a hacer, en palabras del autor.
2. Espera el sí.
3. Hazlo entero: a medias deja el vault diciendo dos cosas a la vez.

## Límites

| Nivel | Regla |
| --- | --- |
| **Pregunta primero** | Leer, buscar o ejecutar fuera del vault. Si `tuku` falla sin que sea un error de lo que pediste (no arranca, no conecta), dilo y no lo depures. Mover archivos, o renombrar algo que no tenga su `rename`. Modificar cualquier `AGENTS.md` o `reglas/`. Cerrar el ciclo, o tocar `bitacoras/` fuera de `tuku entry move`. Cerrar un pendiente cuando el autor no repitió su texto: confirma cuál es antes. |
| **Nunca** | Editar a mano un archivo que tiene comando. Actuar sobre una petición ambigua. Escribir un pendiente que el autor no pidió. Marcar `(Hecho)` algo que nunca estuvo pendiente. Borrar sin confirmación. |

`AHORA.md`, `PENDIENTES.md`, `bitacoras/`, `ambitos/` y `notas/` los escribe el autor: nada los sobreescribe sin su aprobación. Todo lo demás se regenera desde ellos.

El código de `tuku` vive fuera del vault, en su paquete. Sin `tuku` instalado el vault funciona igual, a mano: `reglas/comandos.tuku.md` dice qué hace cada comando y cómo hacerlo.
