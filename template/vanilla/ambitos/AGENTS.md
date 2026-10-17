# Reglas de todos los ámbitos

Un ámbito es un frente de la vida del autor. Lo que escribas aquí vale para todo lo que cuelgue de `ambitos/`, y cuando una regla valga solo para una rama, va en el `AGENTS.md` de esa rama: ante dos reglas que aplican, gana la más cercana.

## Cuál ámbito lleva un registro

Cada registro dice a qué frente pertenece. Va en `--scope`, sin corchetes.

Usa uno que exista como carpeta o archivo aquí. Si ninguno calza, es `personal`, que siempre está.

El `keywords:` del frontmatter de cada página lista los nombres con que el autor se refiere al ámbito sin decir su nombre (siglas, sistemas, personas, proyectos). Un hecho que menciona una keyword es de ese ámbito, aunque parezca no tener relación.

Si el autor nombra un frente que todavía no existe, **no lo crees por tu cuenta ni antes de tiempo**: escríbelo en el cuerpo del registro bajo `personal`, en palabras, y sigue. En un dictado con varios hechos, procesa cada uno en su orden cronológico sin anticipar la creación de frentes nombrados más adelante. El momento de crearlo es cuando la narración llega a esa petición; al crearse, las menciones anteriores se vuelven enlaces solas.

## Cuándo se crea un ámbito

Cuando el autor lo pide. `tuku scope create` arma la carpeta y su página, enlaza hacia atrás lo que ya lo nombraba y deja la constancia en la bitácora: no escribas otro registro para eso. El nombre se pasa tal como lo dijo el autor: el comando cambia los espacios por guiones. El día y la hora de la constancia se pasan como en un registro, con `--at`.

Al crearlo, la salida del comando pide las keywords. Pregúntaselas al autor con sus propias palabras, sin inventarlas, y regístralas con `tuku scope keywords paranal vlti gravity LCU`. Si ya las dio al pedir el ámbito, pásalas en el mismo comando con `--keyword`: `tuku scope create paranal --keyword vlti --keyword LCU`. Las menciones sueltas que ya había quedan enlazadas. Para sumar otras después, el mismo `scope keywords`.

Si un comando rechaza un ámbito porque no existe, ofrécele al autor crearlo y espera el sí.

Un frente que aparece dos veces en la semana probablemente merece página, y eso se propone; no se crea sin el sí. Crear un ámbito cambia dónde va a caer todo lo que venga después, y esa decisión es del autor.

## Un ámbito dentro de otro

Un frente puede ser parte de otro: `faena-ai` es parte de `faena`. Si el autor lo dice al pedirlo, pasa `--parent`: `tuku scope create faena-ai --parent faena`. Si el frente ya existe suelto, `tuku scope move faena-ai --parent faena` lo cambia de lugar y arregla sus links; sin `--parent` lo devuelve a la raíz de `ambitos/`.

El padre tiene que existir. Si no, ofrécele al autor crearlo y espera el sí. Los registros nombran el ámbito por su nombre, sin ruta: `--scope faena-ai`.

## Reglas y cadencias de un ámbito

Un ámbito no trae `AGENTS.md` ni `CADENCIAS.md`: existen cuando el autor les pone su primera regla o cadencia. Una regla que vale solo para un ámbito va en el `AGENTS.md` de su carpeta. Si falta, créalo después de preguntar, como con cualquier `AGENTS.md`.

## A mano

Crear la carpeta con su página del mismo nombre dentro (dentro de la carpeta del padre, si lo tiene), enlazar con `[nombre](ambitos/nombre/nombre.md)` (ruta relativa al archivo donde va, con las carpetas del padre en medio si es anidado) los registros que lo mencionen, y registrar en `AHORA.md` `- HH:MM - [nombre](ambitos/nombre/nombre.md) **nota**: abrí el ámbito`, y listar en `keywords: [nombre, otra]` del frontmatter las palabras con que el autor lo nombra. Si tiene padre, sumarlo a la lista `> [!abstract] En **Padre**:` de la página del padre, con un link relativo a su página.
