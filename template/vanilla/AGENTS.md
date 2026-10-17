# Reglas de este vault

Un vault de TUKU: la bitácora de la vida de su autor, en archivos de texto que se leen y editan sin programas especiales.

Este archivo dice **a dónde va cada cosa**. El cómo está en el archivo que nombra la columna "Lee antes".

## Cómo trabajas

- **Un pedido, un comando.** Ejecuta el comando de la fila con los campos que dio el autor. El comando valida, rechaza con la corrección y escribe todo lo derivado.
- **Atiende todo lo que el autor dijo, en su orden:** cada cosa que cuenta o pide es un comando o una respuesta. No termines con una sin atender.
- **Antes de registrar lo que el autor hizo, mira `PENDIENTES.md`.** Si calza con un pendiente abierto es un cierre (`tuku todo close`); si calzan varios, pregunta cuál y no escribas nada (si la respuesta tampoco lo aclara, vuelve a preguntar: lo que solo el autor sabe no se busca en el vault); si ninguno, es un registro (`tuku entry add`). Fuera de eso no leas el vault: el comando conoce el formato, el día y el orden. Abre solo el archivo que la fila nombra en "Lee antes".
- **Los comandos están en la tabla y en los ejemplos de abajo,** así que no consultes `-h` antes de ejecutar. Si uno rechaza, haz lo que su mensaje dice; solo si no basta, `tuku <comando> -h`.
- **No verifiques después.** El mensaje del comando dice qué quedó escrito. Cuando termina el último, respondes: no releas archivos ni explores el CLI.
- **Responde en una o dos frases:** qué quedó escrito, o la pregunta que falta.

## Qué es cada archivo

| Archivo | Qué guarda |
| --- | --- |
| `AHORA.md` | El ciclo en curso. Aquí se escriben los registros del día. |
| `PENDIENTES.md` | Todo lo que está abierto. |
| `LIBRO-DE-ESTILO.md` | Cómo se escribe aquí y el vocabulario del autor. |
| `ambitos/` | Los frentes de la vida del autor, uno por carpeta. |
| `notas/` | Ideas que no pertenecen a un día. |
| `reglas/` | Reglas de las automatizaciones y configuración. |
| `bitacoras/` | Los ciclos cerrados. Aparece al cerrar el primero. |

MAYÚSCULAS es de TUKU, minúsculas es del autor.

## A dónde va lo que el autor dice

| El autor... | Lee antes | Comando |
| --- | --- | --- |
| cuenta algo que pasó: "hablé con", "llegó", "quedó listo" | `PENDIENTES.md`; si el comando rechaza el día, `reglas/bitacora.tuku.md` | `tuku entry add` |
| deja algo por hacer: "hay que", "recuérdame", "para el lunes" | nada | `tuku todo open` |
| da por hecho algo que estaba pendiente: "ya pagué", "listo lo de" | `PENDIENTES.md` | `tuku todo close` |
| nombra un frente que todavía no existe | `ambitos/AGENTS.md` | `tuku scope create` |
| dice que un frente es parte de otro: "va dentro de" | `ambitos/AGENTS.md` | `tuku scope move` |
| pide guardar una idea que no es de un día | `reglas/notas.tuku.md` | `tuku note create` |
| empieza el ciclo | nada | `tuku cycle open` |
| corrige algo ya escrito: "no era eso", "cámbiale el nombre" | nada | `tuku entry rename`, `scope rename`, `note rename` |
| nombra un proceso del vault | ese proceso | el que el proceso diga |
| pide algo que ninguna fila cubre | nada | ninguno: [reformula y confirma](#lo-que-no-tiene-comando) |
| pregunta, delibera o pide investigar | nada | ninguno: se responde, no se escribe |

```bash
tuku entry add --scope personal --body "revisé el contrato del arriendo" --at 10:30
tuku todo open --scope personal --body "renovar el seguro" --at 13:00
tuku todo open --scope personal --body "pagar el arriendo" --due "2026-08-14 09:00"
tuku todo close --body "pagar el arriendo" --at 16:45
tuku scope create "casa de playa"
tuku note create "cómo se prorroga un arriendo" --scope personal --body "…" --at 21:15
```

- **Los campos.** `--scope` es el nombre de una carpeta de `ambitos/` (`grep -r '^keywords:' ambitos` las lista con sus palabras; si ninguno calza, `personal`). `--at "2026-08-11 09:12"` (o solo `09:12`) es cuándo pasó, cuándo prometió algo el autor o cuándo lo dio por hecho ("a la una, tengo que…", "a las siete, listo lo de…"), también en `todo open` y `todo close`; sin él el comando usa hoy y ahora. `--due "2026-08-14 09:00"` es solo para cuándo vence un pendiente ("el viernes a las nueve", "mañana"), con la hora si el autor la dijo.
- **El cuerpo (`--body`).** Es el hecho, no la conversación: lo dirigido a ti ("recuérdame", "anota", "guárdame") se queda fuera, con todo lo que lo acompaña. No agregues lo que el autor no dijo. El pendiente va en infinitivo, sin mayúscula inicial ("pagar la sesión con el psicólogo"), y `todo close` repite ese texto sin reescribirlo. En `entry add` puede abrir con una clasificación: `**progreso**`, `**decisión**`, `**fricción**`, `**señal**` o `**nota**`.
- **Contarlo es pedirlo.** Si el autor cuenta algo, ejecuta el comando de su fila. No preguntes qué hacer con eso ni ofrezcas alternativas.
- **Lo tentativo espera.** Un compromiso con el día, la hora o la forma sin decidir ("quizás el jueves", "mejor el viernes", "todavía no sé") no se abre. Conversa con el autor y ejecuta `tuku todo open` cuando lo ratifique ("quedamos así"), con el último acuerdo y no con los anteriores.
- **"Lee antes" es lo único que abres antes de ejecutar.**
- **Un hecho, un comando.** El comando ya escribe su registro: `tuku todo open`, `tuku todo close`, `tuku note create` y `tuku scope create` lo dejan en la bitácora, así que no corras además `tuku entry add`.
- **Respeta el orden del dictado.** Cada hecho se registra en el vault tal como estaba en ese momento: un frente que el autor pide abrir más adelante no se crea antes.
- **Si un hallazgo nombra `tuku fix`, córrelo.** Si devuelve decisiones, plantéaselas al autor y espera su respuesta.

## Las tres marcas

Elegir la marca es lo único que es juicio. `**pendiente**` y `(Hecho)` los escriben `tuku todo open` y `tuku todo close`; las demás van al principio de `--body` de `tuku entry add`.

| Marca | Qué significa |
| --- | --- |
| `**pendiente**` | Queda algo por hacer: `tuku todo open`. |
| `(Hecho)` | Se cerró algo **que ya estaba pendiente**: `tuku todo close` con su cuerpo sin reescribirlo; el comando lo tacha. |
| `**cadencia**` | Se da de alta algo que se repite. |

Una acción que nunca fue pendiente es un registro normal, no un cierre. Cualquier otra palabra entre `**` es una clasificación del autor: `LIBRO-DE-ESTILO.md`, `### Clasificaciones`. Cómo se redacta un registro: `LIBRO-DE-ESTILO.md`, `## Cómo escribe el autor`.

## Lo que no tiene comando

1. Di en una frase qué vas a hacer, en palabras del autor.
2. Espera el sí.
3. Hazlo entero: a medias deja el vault diciendo dos cosas a la vez.

## Límites

| Nivel | Regla |
| --- | --- |
| **Pregunta primero** | Mover archivos, o renombrar algo que no tenga su `rename`. Modificar cualquier `AGENTS.md` o `reglas/`. Cerrar el ciclo o tocar `bitacoras/`. Cerrar un pendiente cuando el autor no repitió su texto: confirma cuál es antes. |
| **Nunca** | Editar a mano un archivo que tiene comando. Actuar sobre una petición ambigua. Escribir un pendiente que el autor no pidió. Marcar `(Hecho)` algo que nunca estuvo pendiente. Borrar sin confirmación. |

`AHORA.md`, `PENDIENTES.md`, `bitacoras/`, `ambitos/` y `notas/` los escribe el autor: nada los sobreescribe sin su aprobación. Todo lo demás se regenera desde ellos.

## Si eres un agente

- Si otro agente te lanzó para ejecutar algo concreto, ejecútalo sin volver a despachar.
- Al terminar, di qué quedó escrito, no cómo se hizo.

El código de `tuku` vive fuera del vault, en su paquete. Sin `tuku` instalado el vault funciona igual, a mano: `reglas/comandos.tuku.md` dice qué hace cada comando y cómo hacerlo.
