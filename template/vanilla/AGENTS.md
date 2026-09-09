# Reglas de este vault

Un vault de TUKU: la bitácora de la vida de su autor, en archivos de texto que se leen y editan sin ningún programa especial.

Este archivo se lee entero en toda sesión, así que dice **a dónde va cada cosa** y nada más. El cómo vive donde se hace, y la tabla de abajo nombra el archivo que hay que abrir antes de ejecutar cada fila.

## Qué es cada archivo

| Archivo | Qué guarda |
| --- | --- |
| `AHORA.md` | El ciclo en curso. Aquí se escriben los registros del día. |
| `PENDIENTES.md` | Todo lo que está abierto y sin cerrar. |
| `LIBRO-DE-ESTILO.md` | Cómo se escribe aquí, y el vocabulario del autor. |
| `ambitos/` | Los frentes de tu vida, uno por carpeta o archivo. |
| `notas/` | Ideas y notas que no pertenecen a un día. |
| `reglas/` | Reglas de las automatizaciones y configuración. |
| `bitacoras/` | Los ciclos ya cerrados. Aparece cuando cierres el primero. |

**MAYÚSCULAS es de TUKU, minúsculas es tuyo.** Sirve para saber de un vistazo qué puedes renombrar.

## A dónde va lo que el autor dice

| El autor... | Lee antes | Comando |
| --- | --- | --- |
| cuenta algo que pasó: "hablé con", "llegó", "quedó listo" | `reglas/bitacora.tuku.md` | `tuku entry add` |
| deja algo por hacer: "hay que", "recuérdame", "para el lunes" | `reglas/bitacora.tuku.md` | `tuku entry add`, marca `**pendiente**` |
| da por hecho algo que estaba pendiente: "ya pagué", "listo lo de" | `reglas/bitacora.tuku.md` | `tuku entry add`, marca `~~(Hecho)~~` |
| nombra un frente que todavía no existe | `ambitos/AGENTS.md` | `tuku scope create` |
| pide guardar una idea que no es de un día | `reglas/notas.tuku.md` | `tuku note create` |
| empieza el ciclo | nada | `tuku cycle open` |
| corrige algo ya escrito: "no era eso", "cámbiale el nombre" | nada | `tuku entry rename`, `scope rename`, `note rename` |
| nombra un proceso del vault | ese proceso | el que el proceso diga |
| pide algo que ninguna fila cubre | nada | ninguno: **[reformula y confirma](#lo-que-no-tiene-comando)** |
| pregunta, delibera o pide investigar | nada | ninguno: se responde, no se escribe |

**Contarlo es pedirlo.** Cuando el autor cuenta algo, ejecuta el comando de su fila: no preguntes qué quiere que hagas con lo que acaba de contarte, ni ofrezcas alternativas. Esta tabla ya respondió esa pregunta.

**Abre lo que dice "Lee antes", y ábrelo antes de ejecutar.** Ahí está lo que este archivo no dice: los campos, los plazos, los casos. Si no lo lees, el comando sale mal en la mitad de los casos y bien en la otra mitad, que es peor que fallar.

Casi todo entra por las tres primeras filas, que son el mismo comando y difieren solo en la marca. Pero no todo es un registro: las filas de más abajo no pasan por la bitácora, y dos de ellas no escriben nada.

**Un registro es un comando, y sus consecuencias son parte de escribirlo.** `tuku entry add` deja la línea, actualiza las páginas de ámbito y aplica lo que la marca declara. No hay una segunda llamada que recordar.

## Las tres marcas

Elegir la marca es lo único que es juicio. Va al principio del cuerpo del registro.

| Marca | Qué significa |
| --- | --- |
| `**pendiente**` | Queda algo por hacer. Su cuerpo se copia tal cual a `PENDIENTES.md`. |
| `~~(Hecho)~~` | Se cerró algo **que ya estaba pendiente**. Repite el mismo cuerpo, sin reescribirlo. |
| `**cadencia**` | Se da de alta algo que se repite. |

Una acción que ocurrió pero que nunca fue pendiente es un registro normal, no un cierre. Todo lo demás que se escriba entre `**` es vocabulario del autor y vive en `LIBRO-DE-ESTILO.md`.

## Lo que no tiene comando

Cuando existe un comando, hace en una llamada lo que a ti te cuesta muchas. Cuando no existe, el trabajo se hace igual, a mano, más caro y menos seguro. Por eso:

1. **Di en una frase qué vas a hacer**, en palabras del autor y no en las tuyas.
2. **Espera el sí.** Una petición abierta admite varias lecturas y la tuya puede no ser la suya.
3. **Después hazlo entero.** A medias deja el vault diciendo dos cosas a la vez.

Reformular es decirle qué entendiste, para que corrija ahora y no después de que esté escrito.

## Límites

| Nivel | Regla |
| --- | --- |
| **Pregunta primero** | Mover archivos, o renombrar algo que no tenga su `rename`. Modificar cualquier `AGENTS.md` o `reglas/`. Cerrar el ciclo o tocar `bitacoras/`. Cerrar un pendiente cuando el autor no repitió su texto: confirma cuál es antes. |
| **Nunca** | Editar a mano un archivo que tiene comando. Actuar sobre una petición ambigua. Escribir un pendiente que el autor no pidió. Marcar `~~(Hecho)~~` algo que nunca estuvo pendiente. Borrar sin confirmación. |

`AHORA.md`, `PENDIENTES.md`, `bitacoras/`, `ambitos/` y `notas/` son lo que escribió el autor. Nada los regenera y nada los sobreescribe sin que él lo apruebe. Todo lo demás se puede borrar y volver a generar desde ellos.

## Si eres un agente

- Un hecho dictado ya viene aprobado: escríbelo. Lo que necesita aprobación es lo que el autor **no** pidió, y eso está en Límites.
- Un hecho, un comando. Si te descubres corriendo dos para un mismo hecho, revisa la tabla: casi siempre el segundo ya lo hizo el primero.
- No preguntes lo que los últimos registros ya responden.
- Si otro agente te lanzó para ejecutar algo concreto, ejecútalo: no vuelvas a despachar.
- No narres el mecanismo. Di qué quedó escrito y en qué archivo.

Este vault no contiene código: las automatizaciones se instalan aparte, con el comando `tuku`, y cada una documenta cómo hacer a mano lo que ella hace. Si no están instaladas, el vault funciona igual. Cuesta más trabajo, y eso es todo.
