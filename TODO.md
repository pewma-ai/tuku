# TODO de TUKU

Lo que hay que hacer y no bloquea a nadie. Nada de aquí condiciona el orden de los epics: [`devel/epics.md`](devel/epics.md) sigue siendo la única fuente de verdad sobre qué se construye y en qué estado está. Un ítem sale de aquí cuando entra a un epic o cuando se hace.

**Quién toca qué.** El chat de specs y docs es dueño de `spec/` y `docs/`, y de lo que este archivo dice sobre ellos. Los comandos (`src/tuku/`, `tests/`, `template/`) y los epics son de otro chat: lo que el chat de specs note que hay que hacer allá se anota en "Para el chat de comandos y epics", al final de este archivo, y no se hace.

## Instalación y entorno

- **Configuración del agente tras la instalación:** `uv tool install` y [`tuku init`](src/tuku/init.py) dejan el vault escrito, pero no dejan configurado al agente que lo va a leer. Falta un paso complementario que aplique la configuración del agente elegido por el autor. El caso real es Claude Code: hardcodea `CLAUDE.md` como archivo de memoria y no expone ninguna opción para renombrarlo, así que leer el [`AGENTS.md`](AGENTS.md) del vault exige un hook `SessionStart` que lo descubra e inyecte. Codex lee `AGENTS.md` de forma nativa y Gemini usa `GEMINI.md`. Queda por decidir la forma: `tuku init --agente claude`, un comando propio, o solo instrucciones documentadas que el autor ejecuta a mano. Sea cual sea, el principio 1 exige el equivalente "A mano".

## Superficie del CLI (decidida el 2026-10-18)

La gramática está en [`spec/cli.md`](spec/cli.md), "Sustantivo, verbo y parámetro".

### El resto, por implementar

Falta:

- **Bajar un pendiente por la escalera de horizontes (B4 de [`005-00`](tests/escenarios/005-00-el-dia-ciento-cincuenta.md)).** [`spec/pendientes.md`](spec/pendientes.md) nombra las «postergaciones» como comandos de `tuku todo`, y `todo` solo tiene `open`, `close` y `lint`. Falta el nombre y la forma. El mismo comando serviría para corregir `Vence` (`--due`): hoy `entry update` cambia el texto del pendiente y deja la fecha como estaba, y el capítulo 5 del tutorial lo dice así. Propuesta: `tuku todo update "Llamar a Fabina" --horizon "próxima semana"`, sin verbo nuevo, igual que `entry update`. Modifica un comando, así que se hace donde se trabaja la superficie del CLI.
- **Cada cambio de esta lista toca [`spec/tuku.md`](spec/tuku.md):** se quita el `# pendiente` de lo implementado y la línea de "Lo que se retira" de lo que sale del CLI. [`tests/unitarios/test_superficie.py`](tests/unitarios/test_superficie.py) falla y dice qué línea cambiar si se olvida.

## Las cadencias llegan por un comando, no por un reporte

`reportes/cadencias.md` ("todas, colectadas del árbol") es un diseño obsoleto: se deriva de lo que hay en `ambitos/` y cada ámbito nuevo trae sus propias cadencias. Se retira de [`spec/vault.md`](spec/vault.md) (su entrada en el árbol de directorios y el párrafo que dice que se materializa).

En su lugar, **un comando nuevo** (lo escribe el autor, no el agente que implementa lo demás) que combina todas las cadencias de los `CADENCIAS.md` del árbol, en cascada, y devuelve **todas en un solo texto largo**. Encaja con la gramática de [`spec/cli.md`](spec/cli.md): es una lectura, así que el candidato natural es `tuku context cadence`. Cada cadencia debería salir con el `CADENCIAS.md` de donde viene, para que quien lea sepa dónde editar su `Historia`.

El libro de estilo estático dice el mecanismo (qué es una cadencia, cómo se declara, que se lee en cascada) y manda a buscarlas en `ambitos/`. No transcluye ni lista las cadencias del autor.

## Adaptar todo al libro de estilo nuevo (decidido el 2026-10-19)

El template ya está hecho ([`LIBRO-DE-ESTILO.md`](template/vanilla/LIBRO-DE-ESTILO.md) y [`reglas/`](template/vanilla/reglas/)). Lo que quedó decidido:

- **El libro es orientación, no la especificación completa.** Es de TUKU, legible para una persona y un agente, y los comandos hacen cumplir lo determinista. No repite lo que un comando verifica.
- **Cada capítulo se basta solo para su tarea** (Registro, Pendiente, Ciclo, Ámbito, Nota, Cadencia, Formato OKF, Uso de Markdown...) y dice su "Lee también". La skill del asistente (`reglas/skills/asistente/SKILL.md`) manda leer el capítulo una vez por sesión antes de la primera escritura de cada tipo. Se acepta que un agente se la salte; si pasa, la salida es una compuerta en el comando con estado local `.tuku/leidos`.
- **Los únicos `*.tuku.md` son `config.tuku.md` y `comandos.tuku.md`.** Desaparecen `bitacora.tuku.md`, `notas.tuku.md` y `subtipos/persona.tuku.md`, y su contenido vive en el libro.
- **Lo del autor está en `reglas/*.user.md`**, con lo mínimo: frontmatter `type: Style Guide`, `editable: true`, `modified_time` (null hasta que el agente guarda una preferencia) y `rules` (sus reglas de edición); el cuerpo es solo su tabla o su texto, **sin encabezado**. Los encabezados `###` y las frases viven en el libro. `lenguaje` se fundió en `autor.user.md` (tabla Campo y Valor), y `bitacora.md` pasó a `clasificaciones.user.md`.
- **`cycle_name` salió de `config.tuku.md`** y vive en `reglas/ciclo.user.md`, como una tabla de dos columnas, `Ciclo` y `Días`, con una fila por ciclo en el orden en que se alternan. El código usa la primera columna; `Días` es informativa por ahora.
- **Las clasificaciones solo llegan con el capítulo Registro**; `tuku context` sin tema deja de traer el vocabulario.
- **No hay `ambitos.user.md` ni `cadencias.user.md`.** Los ámbitos se infieren y se crean a petición del autor o por sugerencia de TUKU (regla fija en el capítulo Ámbito), y las cadencias se declaran dentro de los ámbitos. `lenguaje.user.md` tampoco existe.
- **La capacidad del autor es texto abierto**, en `ambitos/personal/CAPACIDAD.md` (sin `Bruto` ni `Costo fijo`), que el libro transcluye. Si no se define, se infiere de las bitácoras. Un ámbito puede tener su propio `CAPACIDAD.md` si el autor lo considera necesario.

### Queda

- **`Días` de `ciclo.user.md`** es solo texto. Si los largos variables (8, 10, 14) deben leerlo `process cycle` y las cadencias, hay que fijar su formato.
- **Transclusiones fuera de `reglas/`.** `doctor style` carga las del libro por su ruta y `context style` las expande, pero no hay un test del caso `ambitos/personal/CAPACIDAD.md`.
- **Cadencias al cambiar de ciclo** y **capacidad al crear un ciclo**: `process cycle` no las lee, y `spec/cadencias.md`, `spec/ciclo.md` y `spec/ambitos.md` no las describen así. La capacidad de cada proyecto, su lectura recursiva y las magnitudes se piensan aparte.
- **`doctor`:** revisar el frontmatter de los `.user.md` (`editable`, `modified_time`, `rules`) y avisar si `modified_time` es `null` y el archivo difiere del template. `autor.user.md` trae `PEDIR AL AUTOR!`: avisar si queda.
- **`template/README.md`:** la fila de `CAPACIDAD.md` y el paso de instalar a mano (la skill ya tiene su fila en la tabla).
- **Tutorial con `test-tui tutorial`:** en el último recorrido (2-8) pasaron 2, 3, 6 y 7. Fallan 4, 5 y 8 por el agente y el entorno, no por el texto: el modelo barato (`gemini-3.8-flash-low`) usa heredocs que `agy` niega, no contesta la fusión de frentes del capítulo 5, y el `tuku` del agente da a veces `PermissionError` al conectar con su socket. Los capítulos 9 y 10 prometen lo que dependen de los epics 006 y 007 y no se corrieron. Para cerrar: otro modelo o permitir en `agy` los comandos compuestos.
- **La skill vive en `reglas/skills/`**, que ningún arnés descubre solo: depende de que `AGENTS.md` la nombre. Si algún arnés no la carga, volver a `AGENTS.md` plano.

## Agente

- **Detectar menciones sin enlace.** Los comandos no enlazan solos: si el agente olvida enlazar una nota que `tuku context note` le ofreció, nada lo avisa. Un chequeo de `tuku doctor` que lo nombre como pregunta, sin fallar, queda por decidir.
- **`updated` de las notas editadas a mano.** Solo lo mueven los comandos que reescriben la nota (`note rename`). Una edición en Obsidian no lo toca, y la nota sale tarde en `tuku context note`. Queda por decidir si `doctor` lo avisa.
- **El contexto que se inyecta al agente.** Decidido el 2026-10-18: `tuku context [TEMA] [--since]`, en [Superficie del CLI](#superficie-del-cli-decidida-el-2026-10-18).

## Reglas del vault

- **El mínimo viable es Deepseek v4.1 Flash.** Ese es el suelo contra el que se valida: si el `AGENTS.md` no funciona con él, no funciona. Cualquier cosa más tonta que eso **no se ha probado que no falle, ni se va a probar**. No es un límite provisional a la espera de más presupuesto: es hasta dónde llega la promesa del vault, y por debajo de ahí el problema deja de ser del `AGENTS.md`.

  Tiene consecuencia de diseño y por eso está escrito acá y no en un comentario: una regla que solo obedece un modelo caro no es una regla del vault, es una que se aprovecha de que el modelo adivina. Cuando algo falle con el mínimo, la primera hipótesis es que la regla está mal escrita, no que el modelo es corto.

## Sistema

- **Defecto: el horizonte del callout se selecciona por texto.** El libro promete que renombrar un horizonte no rompe nada, y no es así: [`regenerate.py`](src/tuku/regenerate.py) selecciona los pendientes del callout del ciclo por el texto literal `esta semana` (`todo_core.ESTA_SEMANA`), y `todo open` usa esa misma constante de valor por defecto. Quien renombre el primer horizonte a `este turno` deja el callout vacío, sin aviso. Debe seleccionar por posición (el primer escalón de la escalera del autor).
- **Endurecimiento:** casos de error, regeneración completa (`tuku regenerate`) e idempotencia global sobre el sistema entero. Un error del autor nunca se rechaza, se reporta. Era la fase 8 y no agrega capacidades, cierra huecos.

## Para el chat de comandos y epics

Anotado desde el chat de specs el 2026-10-18.

### Comandos

- **Vaults ya sembrados con `cycle_type`.** Ahora lo ignoran y usan `semana`. Decidir si `doctor config` avisa de la fila vieja.
- **`context cadence`:** las cadencias vigentes de todo el árbol en un texto, cada una con su `CADENCIAS.md` ([`spec/cadencias.md`](spec/cadencias.md)). La firma de `context` no cambia.
- **El nombre de la bitácora cerrada lleva el ciclo** (`bitacora-DESDE-HASTA-CICLO.md`) cuando exista `cycle close`.

### Epics
- **Epic 010, el tutorial entero** ([`010-00`](tests/escenarios/010-00-el-tutorial.md)). El arnés ya existe: `uv run python tests/scripts/test-tui.py tutorial [capítulos]` ([`tutorial.py`](tests/scripts/tutorial.py)). Falta correrlo con un agente real y ajustar lo que el primer pasaje destape. Las ediciones a mano son un callout `> [!warning] Edita a mano` con bloque `edit` y el arnés las aplica. Los capítulos 4, 5 y 8 fallan por el modelo barato y el sandbox de `agy` (ver "Queda" más arriba). Los capítulos 9 y 10 prometen lo que depende de los epics 006 y 007: el flujo del lunes (rechazo de `entry create`, aviso, cierre, `process cycle`), `cycle close`, la cadencia declarada que emite lo que falta de la semana en curso, y `tuku context todo --late`.
