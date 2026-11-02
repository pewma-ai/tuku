# TODO de TUKU

Lo que hay que hacer y no bloquea a nadie. Nada de aquí condiciona el orden de los epics: [`devel/epics.md`](devel/epics.md) sigue siendo la única fuente de verdad sobre qué se construye y en qué estado está. Un ítem sale de aquí cuando entra a un epic o cuando se hace.

**Quién toca qué.** El chat de specs y docs es dueño de `spec/` y `docs/`, y de lo que este archivo dice sobre ellos. Los comandos (`src/tuku/`, `tests/`, `template/`) y los epics son de otro chat: lo que el chat de specs note que hay que hacer allá se anota en "Para el chat de comandos y epics", al final de este archivo, y no se hace.

## Instalación y entorno

- **Configuración del agente tras la instalación:** `uv tool install` y [`tuku init`](src/tuku/init.py) dejan el vault escrito, pero no dejan configurado al agente que lo va a leer. Falta un paso complementario que aplique la configuración del agente elegido por el autor. El caso real es Claude Code: hardcodea `CLAUDE.md` como archivo de memoria y no expone ninguna opción para renombrarlo, así que leer el [`AGENTS.md`](AGENTS.md) del vault exige un hook `SessionStart` que lo descubra e inyecte. Codex lee `AGENTS.md` de forma nativa y Gemini usa `GEMINI.md`. Queda por decidir la forma: `tuku init --agente claude`, un comando propio, o solo instrucciones documentadas que el autor ejecuta a mano. Sea cual sea, el principio 1 exige el equivalente "A mano".

## Superficie del CLI (decidida el 2026-10-18)

La gramática está en [`devel/VAULT/spec-anterior/cli.md`](devel/VAULT/spec-anterior/cli.md), "Sustantivo, verbo y parámetro".

### El resto, por implementar

Falta:

- **Bajar un pendiente por la escalera de horizontes (B4 de [`005-00`](tests/escenarios/005-00-el-dia-ciento-cincuenta.md)).** [`devel/VAULT/spec-anterior/pendientes.md`](devel/VAULT/spec-anterior/pendientes.md) nombra las «postergaciones» como comandos de `tuku todo`, y `todo` solo tiene `open`, `close` y `lint`. Falta el nombre y la forma. El mismo comando serviría para corregir `Vence` (`--due`): hoy `entry update` cambia el texto del pendiente y deja la fecha como estaba, y el capítulo 5 del tutorial lo dice así. Propuesta: `tuku todo update "Llamar a Fabina" --horizon "próxima semana"`, sin verbo nuevo, igual que `entry update`. Modifica un comando, así que se hace donde se trabaja la superficie del CLI.
- **Cada cambio de esta lista toca [`spec/tuku.md`](spec/tuku.md):** se quita el `# pendiente` de lo implementado y la línea de "Lo que se retira" de lo que sale del CLI. [`tests/unitarios/test_superficie.py`](tests/unitarios/test_superficie.py) falla y dice qué línea cambiar si se olvida.

## AHORA.md sin ciclos (decidido el 2026-11-02, por implementar)

Abrir y cerrar un ciclo es complejidad innecesaria: corta el flujo de trabajo y no deja ver lo que pasó hace poco en el mismo archivo. Se reemplaza por un `AHORA.md` que siempre muestra lo reciente y se archiva solo. Hasta implementarlo, el libro de estilo y el código siguen con ciclos. Los epics se revisan uno por uno después: el 006 se reformula y los 002, 005 y 010 se tocan.

### Cómo queda `AHORA.md`

De arriba abajo:

1. **El foco:** un texto breve que sugiere en qué concentrarse los próximos días. Por ahora lo escribe el autor.
2. **Los pendientes de los próximos 7 días** (el 7 es configurable), y ya no «los de esta semana». Los pendientes con fecha aparecen además bajo su día en cuanto ese día existe en el archivo.
3. **Los registros por día, del más nuevo al más viejo.** Dentro de cada día también va lo más reciente arriba. Registrar «acabo de tener una reunión» lo pone bajo hoy, encima de lo demás de hoy. Un registro sin hora conserva su orden relativo dentro del día y no se le inventa una.

### `PENDIENTES.md` lleva la fecha de creación

La tabla suma una columna `Creado` (`| Horizonte | Vence | Creado | Ámbito | Detalle |`), con el día en que se prometió el pendiente, el mismo que `--at`. Con ella un horizonte relativo se resuelve sin ciclos: `esta semana` dicho el lunes 19 cubre hasta el lunes 26, y pasada esa fecha el pendiente está atrasado. Se calcula y no se guarda, como hoy. Esa fecha reemplaza a dos cosas: el horizonte que expiraba al cerrar el ciclo y la antigüedad que hoy se saca del historial de git.

### Autoarchivado

- **La ventana por defecto son 14 días contando desde un lunes:** el archivo lleva la semana anterior completa y la actual hasta hoy, así que un lunes tiene 8 días y un domingo 14. El largo es configurable, en días o en semanas.
- **El disparo es escribir.** Cuando un comando que escribe corre un día posterior a la ventana (el lunes siguiente o cualquier día futuro), archiva lo que quedó fuera antes de escribir. Es determinista e idempotente, y un comando que solo lee no archiva.
- **Solo viajan los registros.** El foco y los pendientes de la semana archivada se descartan.
- **Al archivar, se recalculan las rutas** de los links de cada registro, que cambian de archivo.
- **Cada ámbito enlaza a la bitácora histórica** que contiene lo suyo, en el momento del archivado.

### Las bitácoras históricas

- **El nombre lleva el rango:** `bitacora-20261019-20261025.md`, sin nombre de ciclo. Su frontmatter lleva `from` y `to`.
- **Son inmutables en lo posible.** Solo se tocan para reparar rutas cuando cambia el nombre de un ámbito o de una nota, y para corregir un registro (`entry update`, `entry move`).
- **Un registro con fecha antigua** va a la bitácora que le corresponde, y si no existe la crea. No se rechaza por «fuera del ciclo».

### Lo que desaparece

`tuku process cycle`, `cycle close` (nunca existió), el rechazo de `entry create` por un día fuera del ciclo, el campo `cycle:`, `cycle_name` y `reglas/ciclo.user.md`, `doctor cycle` (se reemplaza por una revisión de las bitácoras históricas), el capítulo Ciclo del libro y [`devel/borradores/ciclo.md`](devel/borradores/ciclo.md). La capacidad «al crear un ciclo» pierde su disparador. La región de la semana del callout se reemplaza por la ventana de 7 días, y el horizonte que expiraba al cerrar un ciclo, por la fecha `Creado`.

### Abierto

- **Pendientes que no son una ventana de días.** «Cuando esté en Santiago» es una condición, «el fin de semana» es una fecha y «próximo turno en el cerro» depende del ritmo de trabajo del autor. Propuesta: la fecha es lo único que `tuku` entiende; el agente traduce «próximo turno» a un `--due` usando lo que el autor escribió de su ritmo (`CAPACIDAD.md`); una condición es un horizonte propio de la tabla del autor que no vence nunca, y por lo tanto nunca está atrasado. Las cadencias no sirven: emiten pendientes por calendario, y una condición no es calendario.
- **Las bitácoras son siempre semanales** (lunes a domingo) aunque la ventana sea otra, o su rango sigue a lo que se archivó.
- **Qué hace la página de un ámbito con la bitácora histórica:** listar enlaces a las bitácoras que lo contienen, o seguir copiando su actividad reciente.
- **Un vault ya sembrado con ciclos:** qué se hace con `cycle:` en sus bitácoras cerradas y con `reglas/ciclo.user.md`.
- **El comienzo de la semana** es el lunes, fijo o configurable.
- **`Creado` y las postergaciones.** `esta semana` se mide desde `Creado`: no se decidió si el escalón dura 7 días desde esa fecha o llega hasta el domingo de esa semana, ni qué pasa al postergar con `todo update`: si `Creado` se conserva, un pendiente movido a `próxima semana` se mediría desde su creación y no desde la postergación. Quizá la columna deba llamarse `Desde` y reiniciarse al postergar.
- **Vaults ya sembrados:** la tabla de `PENDIENTES.md` cambia de cuatro a cinco columnas, y las filas existentes no tienen `Creado`.

## Las cadencias llegan por un comando, no por un reporte

`reportes/cadencias.md` ("todas, colectadas del árbol") es un diseño obsoleto: se deriva de lo que hay en `ambitos/` y cada ámbito nuevo trae sus propias cadencias. Se retira de [`devel/VAULT/spec-anterior/vault.md`](devel/VAULT/spec-anterior/vault.md) (su entrada en el árbol de directorios y el párrafo que dice que se materializa).

En su lugar, **un comando nuevo** (lo escribe el autor, no el agente que implementa lo demás) que combina todas las cadencias de los `CADENCIAS.md` del árbol, en cascada, y devuelve **todas en un solo texto largo**. Encaja con la gramática de [`devel/VAULT/spec-anterior/cli.md`](devel/VAULT/spec-anterior/cli.md): es una lectura, así que el candidato natural es `tuku context cadence`. Cada cadencia debería salir con el `CADENCIAS.md` de donde viene, para que quien lea sepa dónde editar su `Historia`.

El libro de estilo estático dice el mecanismo (qué es una cadencia, cómo se declara, que se lee en cascada) y manda a buscarlas en `ambitos/`. No transcluye ni lista las cadencias del autor.

## Adaptar todo al libro de estilo nuevo (decidido el 2026-10-19)

El template ya está hecho ([`LIBRO-DE-ESTILO.md`](template/vanilla/LIBRO-DE-ESTILO.md) y [`reglas/`](template/vanilla/reglas)). Lo que quedó decidido:

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
- **Cadencias al cambiar de ciclo** y **capacidad al crear un ciclo**: `process cycle` no las lee, y `devel/borradores/cadencias.md`, `devel/borradores/ciclo.md` y el capítulo Ámbito del libro no las describen así. La capacidad de cada proyecto, su lectura recursiva y las magnitudes se piensan aparte.
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
- **`context cadence`:** las cadencias vigentes de todo el árbol en un texto, cada una con su `CADENCIAS.md` ([`devel/borradores/cadencias.md`](devel/borradores/cadencias.md)). La firma de `context` no cambia.
- **El nombre de la bitácora cerrada lleva el ciclo** (`bitacora-DESDE-HASTA-CICLO.md`) cuando exista `cycle close`.

### Epics
- **Epic 010, el tutorial entero** ([`010-00`](tests/escenarios/010-00-el-tutorial.md)). El arnés ya existe: `uv run python tests/scripts/test-tui.py tutorial [capítulos]` ([`tutorial.py`](tests/scripts/tutorial.py)). Falta correrlo con un agente real y ajustar lo que el primer pasaje destape. Las ediciones a mano son un callout `> [!warning] Edita a mano` con bloque `edit` y el arnés las aplica. Los capítulos 4, 5 y 8 fallan por el modelo barato y el sandbox de `agy` (ver "Queda" más arriba). Los capítulos 9 y 10 prometen lo que depende de los epics 006 y 007: el flujo del lunes (rechazo de `entry create`, aviso, cierre, `process cycle`), `cycle close`, la cadencia declarada que emite lo que falta de la semana en curso, y `tuku context todo --late`.
