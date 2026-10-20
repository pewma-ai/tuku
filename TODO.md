# TODO de TUKU

Lo que hay que hacer y no bloquea a nadie. Nada de aquí condiciona el orden de los epics: [`devel/epics.md`](devel/epics.md) sigue siendo la única fuente de verdad sobre qué se construye y en qué estado está. Un ítem sale de aquí cuando entra a un epic o cuando se hace.

**Quién toca qué.** El chat de specs y docs es dueño de `spec/` y `docs/`, y de lo que este archivo dice sobre ellos. Los comandos (`src/tuku/`, `tests/`, `template/`) y los epics son de otro chat: lo que el chat de specs note que hay que hacer allá se anota en "Para el chat de comandos y epics", al final de este archivo, y no se hace.

## Instalación y entorno

- **Configuración del agente tras la instalación:** `uv tool install` y [`tuku init`](src/tuku/init.py) dejan el vault escrito, pero no dejan configurado al agente que lo va a leer. Falta un paso complementario que aplique la configuración del agente elegido por el autor. El caso real es Claude Code: hardcodea `CLAUDE.md` como archivo de memoria y no expone ninguna opción para renombrarlo, así que leer el [`AGENTS.md`](AGENTS.md) del vault exige un hook `SessionStart` que lo descubra e inyecte. Codex lee `AGENTS.md` de forma nativa y Gemini usa `GEMINI.md`. Queda por decidir la forma: `tuku init --agente claude`, un comando propio, o solo instrucciones documentadas que el autor ejecuta a mano. Sea cual sea, el principio 1 exige el equivalente "A mano".
- **Resuelto (2026-09-19): prueba con usuario ajeno:** verificada la instalación limpia (`uv tool install`) y primer registro a mano leyendo solo [`AGENTS.md`](AGENTS.md). Epic 001 cerrado.

## Superficie del CLI (decidida el 2026-10-18)

La gramática está en [`spec/cli.md`](spec/cli.md), "Sustantivo, verbo y parámetro".

### El resto, por implementar

Hecho el 2026-10-18 ([`devel/iteraciones/2026-10-18.md`](devel/iteraciones/2026-10-18.md)): escritura atómica con reintentos, `regenerate` con su tabla de dependencias, `entry update` y `entry move`, registros sin hora, `tuku context`, `tuku process`, el `AGENTS.md` de dos invocadores, enlazar al registrar con la columna "Enlazable", los `lint` pasados a `doctor TEMA`, `todo close TEXTO`, `Actividad reciente` de doce meses, `scope create --since`, el retiro de `cycle open` y `vocab show`, y los ejemplos en la ayuda ([`ejemplos.py`](src/tuku/cli/ejemplos.py)). Falta:

- **Bajar un pendiente por la escalera de horizontes (B4 de [`005-00`](tests/escenarios/005-00-el-dia-ciento-cincuenta.md)).** [`spec/pendientes.md`](spec/pendientes.md) nombra las «postergaciones» como comandos de `tuku todo`, y `todo` solo tiene `open`, `close` y `lint`. Falta el nombre y la forma. El mismo comando serviría para corregir `Vence` (`--due`): hoy `entry update` cambia el texto del pendiente y deja la fecha como estaba, y el capítulo 5 del tutorial lo dice así. Propuesta: `tuku todo update "Llamar a Fabina" --horizon "próxima semana"`, sin verbo nuevo, igual que `entry update`. Modifica un comando, así que se hace donde se trabaja la superficie del CLI.
- **Cada cambio de esta lista toca [`spec/tuku.md`](spec/tuku.md):** se quita el `# pendiente` de lo implementado y la línea de "Lo que se retira" de lo que sale del CLI. [`tests/unitarios/test_superficie.py`](tests/unitarios/test_superficie.py) falla y dice qué línea cambiar si se olvida.

## Ciclos con nombre, config y libro de estilo (conversación del 2026-10-18)

Tres temas que salieron de revisar cómo se declara el ciclo del autor, que trabaja por turnos. Están decididos en su dirección y se implementan después de la conversación sobre `reglas/config.tuku.md`, que merece su propia sesión. **Hasta entonces no se tocan los comandos que leen la config ni el libro de estilo.**

### El ciclo tiene nombre y el largo no es fijo

Hoy el ciclo es la semana de lunes a domingo, fija en el código. `cycle_type` ya se reemplazó por `cycle_name` en la config, el template y el código ([`src/tuku/config.py`](src/tuku/config.py)), que lo lee como lista de nombres y todavía no lo usa para abrir ciclos. El autor trabaja turnos de martes a martes (8 días) y descansa de miércoles a lunes (6 días), pero hay turnos de 10 o 14 días y vacaciones: en mac-jpgil cada fase es un ciclo y un agente le pregunta el rango al cambiar de ciclo, a partir de [`Capacidad.md`](../mac-jpgil/estrategia/Capacidad.md).

Lo decidido:

- **`cycle_name` reemplaza a `cycle_type`.** Admite una lista, `cycle_name = [turno, descanso]`, y `tuku` la lee y actúa en consecuencia. Por defecto vale `semana`.
- **Cada ciclo declara cuál es** en su frontmatter, `cycle: turno`, junto a `status`, `from` y `to`, tanto en `AHORA.md` como en la bitácora cerrada. La lista de la config solo da los nombres posibles: nada más dice qué fase corre hoy.
- **El ciclo siguiente es el siguiente de la lista**, y al llegar al final vuelve al primero. Con un solo nombre, es el mismo.
- **Con `semana` el rango se deriva** (lunes a domingo). **Con cualquier otro nombre el rango es obligatorio**: el agente le pregunta al autor hasta qué día va y abre el ciclo con ese rango. Decidir el rango es del autor y abrirlo con un rango dado es determinista.
- **La bitácora cerrada lleva el nombre del ciclo**: `bitacora-2026-08-11-2026-08-18-turno.md`. `plan-…-turno.md` y `resumen-…-turno.md` ya lo llevaban en [`spec/vault.md`](spec/vault.md).
- **La plantilla [`reglas/plantilla/AHORA.md`](template/vanilla/reglas/plantilla/AHORA.md) deja de traer siete días fijos**: genera un encabezado por cada fecha entre `from` y `to`.

Los horizontes del libro de estilo se nombran con el ciclo: `esta semana` y `próxima semana` pasan a poder escribirse con `$cycle_name[N]`, donde `N` es cualquier índice de la lista (`$cycle_name[0]` es `turno` y `$cycle_name[1]` es `descanso`). Lo que significa cada uno, según el autor:

| Horizonte | Hasta cuándo | Ejemplo con `[turno, descanso]`, estando en turno |
| --- | --- | --- |
| `este $cycle_name[N]` | El ciclo en curso, si se llama así | Este turno |
| `próximo $cycle_name[N]` | El siguiente ciclo de ese nombre, pasando por los demás | El turno que viene después del descanso |
| `fin de mes` | El último día del mes, menos uno, por si acaso | 30 en un mes de 31 días |

Con `semana`, `próxima semana` es desde el lunes siguiente, fijo. El artículo (`este` o `esta`) lo escribe el autor en su tabla, porque no se deduce del nombre. Estando en el descanso, `este turno` es un error del autor, no un horizonte válido: el comando rechaza sin escribir, nombra la corrección (`próximo turno`, o `este descanso`) y el agente desambigua con el autor. Con los índices la escalera puede declarar `este turno` y `este descanso` a la vez. Queda abierto cuál de los dos es el escalón del ciclo en curso para el callout y para un pendiente que no dice horizonte; la propuesta es el `este …` cuyo índice es el del ciclo en curso.

**Defecto relacionado, sin resolver.** El libro de estilo promete que renombrar un horizonte no rompe nada, y no es así: [`regenerate.py`](src/tuku/regenerate.py) selecciona los pendientes del callout del ciclo por el texto literal `esta semana` (`todo.ESTA_SEMANA`), y `todo open` usa esa misma constante de valor por defecto. Quien renombre el primer horizonte a `este turno` deja el callout vacío, sin aviso. Debe seleccionar por posición (el primer escalón de la escalera del autor), no por texto.

Lo decidido el 2026-10-18 sobre `tuku process cycle` ([`spec/ciclo.md`](spec/ciclo.md), "Abrir el siguiente ciclo"), **implementado ese día** en [`cycle.py`](src/tuku/cycle.py) y, para los hoyos y solapes de `doctor cycle`, en [`cyclelint.py`](src/tuku/cyclelint.py):

- `--at` se reemplaza por `--from` y `--to`, con el nombre de los campos del frontmatter. Con `semana`, `--from` es un día cualquiera de la semana y `--to` se deduce.
- Sin `--from`, empieza el día siguiente al `to` del ciclo anterior (el abierto o, si ya se archivó, la bitácora más reciente).
- Sin hoyos: un `from` distinto del día siguiente al `to` anterior se rechaza, salvo repetir el ciclo abierto con su mismo `from`, que solo verifica y, sin registros, lo regenera. El nombre avanza en `cycle_name` con cada ciclo nuevo y se conserva al repetir. La regla vale para el `from` efectivo, el ya deducido con `semana`.
- Un `--from` anterior al del ciclo abierto es un ciclo histórico: se escribe en `bitacoras/` sin verificar contra los vecinos, con `--name`, y `tuku doctor cycle` reporta los hoyos y solapes que queden.
- El cambio de ciclo lo dispara el rechazo de `tuku entry create` ante un día fuera del ciclo abierto; ya existe, y el agente avisa al autor, cierra el ciclo si tiene registros y corre `process cycle`.
- `--name` opcional. Fuera de `cycle_name` se rechaza con aviso y se repite con `--force` tras confirmarlo con el autor.

### El libro de estilo estático, con los datos del autor aparte

Hoy [`LIBRO-DE-ESTILO.md`](template/vanilla/LIBRO-DE-ESTILO.md) mezcla prosa de TUKU (qué es una clasificación, qué es OKF, cómo se escribe una cadencia) con datos del autor (su nombre, las filas de las tablas, las reglas de escritura). Se copia una vez al sembrar el vault: cuando TUKU mejora una explicación, el vault ya quedó editado y no se puede pisar. Además la spec dice que MAYÚSCULAS es de TUKU y este archivo se declara a sí mismo "suyo".

La dirección decidida:

- **El libro pasa a ser estático y de TUKU**, regenerado con `tuku regenerate`, igual que [`reglas/comandos.tuku.md`](template/vanilla/reglas/comandos.tuku.md). **Vive en el vault**, no en `~/.tuku`: un vault clonado o abierto en otra máquina se lee solo, y Obsidian no transcluye archivos de fuera.
- **Los datos del autor viven en archivos propios**, que el libro transcluye: `reglas/autor.md` (quién soy), `reglas/clasificaciones.md`, `reglas/horizontes.md`, `reglas/types.md` (ya existe, el libro ya lo transcluye) y las reglas de escritura propias. La regla 4 de "Cómo escribe el autor" (el pendiente va en infinitivo y su cierre repite el texto) es contrato y queda en el libro estático.
- **Los comandos no cambian todavía.** Hoy `tuku vocab show` y `tuku style lint` leen las tablas por sus encabezados dentro del libro. Cuándo pasan a leer los archivos del autor es parte de la conversación sobre la config.

Riesgos a resolver al implementarlo:

- Un editor básico, o un agente que lee el archivo crudo, ve enlaces en vez de las tablas. Lo cubre `tuku context style`, ya planeado arriba como reemplazo de `tuku vocab show`: imprime el libro expandido.
- Quien edite `LIBRO-DE-ESTILO.md` a mano pierde el cambio al regenerar. Una revisión de `doctor` debería avisar si difiere del generado.
- Las reglas de escritura 1 a 3 pasan a un archivo del autor.

### Las cadencias llegan por un comando, no por un reporte

`reportes/cadencias.md` ("todas, colectadas del árbol") es un diseño obsoleto: se deriva de lo que hay en `ambitos/` y cada ámbito nuevo trae sus propias cadencias. Se retira de [`spec/vault.md`](spec/vault.md) (su entrada en el árbol de directorios y el párrafo que dice que se materializa).

En su lugar, **un comando nuevo** (lo escribe el autor, no el agente que implementa lo demás) que combina todas las cadencias de los `CADENCIAS.md` del árbol, en cascada, y devuelve **todas en un solo texto largo**. Encaja con la gramática de [`spec/cli.md`](spec/cli.md): es una lectura, así que el candidato natural es `tuku context cadence`. Cada cadencia debería salir con el `CADENCIAS.md` de donde viene, para que quien lea sepa dónde editar su `Historia`.

El libro de estilo estático dice el mecanismo (qué es una cadencia, cómo se declara, que se lee en cascada) y manda a buscarlas en `ambitos/`. No transcluye ni lista las cadencias del autor.

### La conversación sobre `reglas/config.tuku.md`

Pendiente para una sesión propia. Temas que ya están sobre la mesa:

- `cycle_name` y su lista, y que la tabla de la config hoy solo tiene campos de un valor.
- Qué comandos pasan a leer los archivos de datos del autor en vez del libro.
- `tuku_template` frente a `--variant` ([`spec/cli.md`](spec/cli.md) y 005-00, S8).

## Adaptar todo al libro de estilo nuevo (decidido el 2026-10-19)

El template ya está hecho ([`LIBRO-DE-ESTILO.md`](template/vanilla/LIBRO-DE-ESTILO.md) y [`reglas/`](template/vanilla/reglas/)). Esto reemplaza la dirección de "El libro de estilo estático" y la conversación sobre `reglas/config.tuku.md` de más arriba. Lo que quedó decidido:

- **El libro es orientación, no la especificación completa.** Es de TUKU, legible para una persona y un agente, y los comandos hacen cumplir lo determinista. No repite lo que un comando verifica.
- **Cada capítulo se basta solo para su tarea** (Registro, Pendiente, Ciclo, Ámbito, Nota, Cadencia, Formato OKF, Uso de Markdown...) y dice su "Lee también". La skill del asistente (`reglas/skills/asistente/SKILL.md`) manda leer el capítulo una vez por sesión antes de la primera escritura de cada tipo. Se acepta que un agente se la salte; si pasa, la salida es una compuerta en el comando con estado local `.tuku/leidos`.
- **Los únicos `*.tuku.md` son `config.tuku.md` y `comandos.tuku.md`.** Desaparecen `bitacora.tuku.md`, `notas.tuku.md` y `subtipos/persona.tuku.md`, y su contenido vive en el libro.
- **Lo del autor está en `reglas/*.user.md`**, con lo mínimo: frontmatter `type: Style Guide`, `editable: true`, `modified_time` (null hasta que el agente guarda una preferencia) y `rules` (sus reglas de edición); el cuerpo es solo su tabla o su texto, **sin encabezado**. Los encabezados `###` y las frases viven en el libro. `lenguaje` se fundió en `autor.user.md` (tabla Campo y Valor), y `bitacora.md` pasó a `clasificaciones.user.md`.
- **`cycle_name` salió de `config.tuku.md`** y vive en `reglas/ciclo.user.md`, como una tabla de dos columnas, `Ciclo` y `Días`, con una fila por ciclo en el orden en que se alternan. El código usa la primera columna; `Días` es informativa por ahora.
- **Las clasificaciones solo llegan con el capítulo Registro**; `tuku context` sin tema deja de traer el vocabulario.
- **No hay `ambitos.user.md` ni `cadencias.user.md`.** Los ámbitos se infieren y se crean a petición del autor o por sugerencia de TUKU (regla fija en el capítulo Ámbito), y las cadencias se declaran dentro de los ámbitos. `lenguaje.user.md` tampoco existe.
- **La capacidad del autor es texto abierto**, en `ambitos/personal/CAPACIDAD.md` (sin `Bruto` ni `Costo fijo`), que el libro transcluye. Si no se define, se infiere de las bitácoras. Un ámbito puede tener su propio `CAPACIDAD.md` si el autor lo considera necesario.

### Hecho el 2026-10-19

- **Epic 004 con tests agénticos:** `test_004_01` a `test_004_05` corren la conversación con Damián simulado (`tests/scripts/conversacion.py`) y evalúan la tabla de deltas por turno; los cinco pasan. Para eso la skill ganó cuatro reglas: la decisión sin cuándo es un registro, lo que el autor deja sin resolver no se escribe, el ámbito no se pregunta, y `--at` vale también en `note create`.
- **Asistente:** `AGENTS.md` quedó en invocación y límites; las reglas de trabajo y los ejemplos petición, capítulo y comando viven en `reglas/skills/asistente/SKILL.md`. El doctor lee ambos. `spec/despacho.md` y `spec/vault.md` al día.
- **Specs:** `vault`, `bitacora`, `pendientes`, `notas`, `cli`, `markdown` al día con el libro y `reglas/*.user.md`; `ambitos` y `ciclo` con la capacidad marcada como provisional. **Docs:** glosario y tutoriales 01 a 04.
- **Código:** `capitulos.primera_tabla`; `vocab`, `style`, `config`, `init`, `doctor`, `context` y `regenerate` leen los `.user.md` sin capítulos; `context` sin tema trae solo la tabla del autor; los textos con rutas viejas. **Tests:** unitarios y escenarios 001-04, 001-07, 003-11 y 005-05 adaptados; la suite no agéntica pasa.
- **El agente de 003-11 falló sin la regla del día fuera del ciclo**, y la volvió a ganar al restaurarla como regla 5 del capítulo Registro. Es la prueba de que esa regla es de juicio y debe quedar en el libro.

### Queda

- **`Días` de `ciclo.user.md`** es solo texto. Si los largos variables (8, 10, 14) deben leerlo `process cycle` y las cadencias, hay que fijar su formato.
- **Transclusiones fuera de `reglas/`.** `doctor style` carga las del libro por su ruta y `context style` las expande, pero no hay un test del caso `ambitos/personal/CAPACIDAD.md`.
- **Cadencias al cambiar de ciclo** y **capacidad al crear un ciclo**: `process cycle` no las lee, y `spec/cadencias.md`, `spec/ciclo.md` y `spec/ambitos.md` no las describen así. La capacidad de cada proyecto, su lectura recursiva y las magnitudes se piensan aparte.
- **`**cadencia**`:** el libro ya no la reserva; `spec/bitacora.md` la sigue tratando como marca. Decidir.
- **`doctor`:** revisar el frontmatter de los `.user.md` (`editable`, `modified_time`, `rules`) y avisar si `modified_time` es `null` y el archivo difiere del template. `autor.user.md` trae `PEDIR AL AUTOR!`: avisar si queda.
- **La compuerta `.tuku/leidos`**, solo si se mide que los agentes se saltan la lectura del capítulo. Con 003-11 el agente sí lee `Registro`.
- **`template/README.md`:** la fila de `CAPACIDAD.md` y el paso de instalar a mano (la skill ya tiene su fila en la tabla).
- **Epics:** `devel/epics.md` no nombra nada del libro viejo; revisar si 001 o 005 deben mencionar el libro por capítulos.
- **Tutorial con `test-tui tutorial`:** en el último recorrido (2-8) pasaron 2, 3, 6 y 7. Fallan 4, 5 y 8 por el agente y el entorno, no por el texto: el modelo barato (`gemini-3.8-flash-low`) usa heredocs que `agy` niega, no contesta la fusión de frentes del capítulo 5, y el `tuku` del agente da a veces `PermissionError` al conectar con su socket. Los capítulos 9 y 10 prometen lo que dependen de los epics 006 y 007 y no se corrieron. Para cerrar: otro modelo o permitir en `agy` los comandos compuestos.
- **Correr los demás agénticos** con el `AGENTS.md` mínimo y la skill del asistente (solo corrió 003-11, y antes de la skill). Ver si el agente real carga la skill sin que falle el despacho.
- **La skill vive en `reglas/skills/`**, que ningún arnés descubre solo: depende de que `AGENTS.md` la nombre. Si algún arnés no la carga, volver a `AGENTS.md` plano.

## Agente

- **Detectar menciones sin enlace.** Los comandos no enlazan solos: si el agente olvida enlazar una nota que `tuku context note` le ofreció, nada lo avisa. Un chequeo de `tuku doctor` que lo nombre como pregunta, sin fallar, queda por decidir.
- **`updated` de las notas editadas a mano.** Solo lo mueven los comandos que reescriben la nota (`note rename`). Una edición en Obsidian no lo toca, y la nota sale tarde en `tuku context note`. Queda por decidir si `doctor` lo avisa.
- **El contexto que se inyecta al agente.** Decidido el 2026-10-18: `tuku context [TEMA] [--since]`, en [Superficie del CLI](#superficie-del-cli-decidida-el-2026-10-18).

## Reglas del vault

- **El mínimo viable es Deepseek v4.1 Flash.** Ese es el suelo contra el que se valida: si el `AGENTS.md` no funciona con él, no funciona. Cualquier cosa más tonta que eso **no se ha probado que no falle, ni se va a probar**. No es un límite provisional a la espera de más presupuesto: es hasta dónde llega la promesa del vault, y por debajo de ahí el problema deja de ser del `AGENTS.md`.

  Tiene consecuencia de diseño y por eso está escrito acá y no en un comentario: una regla que solo obedece un modelo caro no es una regla del vault, es una que se aprovecha de que el modelo adivina. Cuando algo falle con el mínimo, la primera hipótesis es que la regla está mal escrita, no que el modelo es corto.

## Tutorial


## Sistema

- **Endurecimiento:** casos de error, regeneración completa (`tuku regenerate`) e idempotencia global sobre el sistema entero. Un error del autor nunca se rechaza, se reporta. Era la fase 8 y no agrega capacidades, cierra huecos.

## Suite de escenarios

- **Resuelto (2026-09-10): tests en Epic 002 para entradas y pendientes sin fecha (fallback a hoy):** Se implementó `_congelar_tiempo` en [`tests/scripts/gherkin.py`](tests/scripts/gherkin.py) para interceptar `TUKU_NOW="AAAA-MM-DD HH:MM"` en bloques bash y congelar deterministamente `date.today()` y `datetime.now()` durante llamadas en proceso a `cli.main`, sin tocar el código de producción. Probado en `002-02-registro-en-su-dia`.

- **Resuelto (2026-09-10): cobertura de comandos directos para pendientes:** Se incorporaron escenarios BDD en `002-04` (`tuku todo open`) y `002-05` (`tuku todo close`) verificando que operan de forma idempotente, actualizan `PENDIENTES.md` y estampan su huella cronológica en `AHORA.md` respetando la regla normativa de huella obligatoria.

- **Resuelto (2026-09-08): no era un flake, era un sincronizador restaurando archivos borrados.** La suite fallaba en cerca de la mitad de las corridas, en cascada, con `<slug>/<escenario> ya existe después de limpiar el epic`. La causa no estaba en los tests: un LaunchAgent del autor, `com.jgil.sync-obsidian-gdrive`, corría `rclone bisync` **bidireccional** entre `~/Code/MaC` y Google Drive, con el filtro `+ *.md`, que incluye todos los Markdown a cualquier profundidad. Un vault de TUKU es puro Markdown, así que cada corrida sincronizaba `playground/` con la nube: los tests borraban, y rclone reponía desde Drive.

  Cómo se acorraló, por si vuelve algo parecido: el fallo se reprodujo **sin pytest**, con un script que solo copiaba y borraba árboles con el mismo patrón (`rm -rf 001-* 002-*` y treinta carpetas de golpe). Ese reproductor de veinte segundos permitió medir por ubicación, y la frontera fue nítida: `/tmp`, `~` y `~/Code` limpios; `~/Code/MaC` fallando. Esa frontera es la raíz del bisync, y `lsof` más el log del agente pusieron el nombre.

  La lección de método: llamarlo "flake" costó horas. Un flake invita a reintentar, y por eso los primeros cuatro intentos fueron reintentos, esperas y verificaciones, o sea curar el síntoma. En cuanto se nombró como "hay un intruso escribiendo en `playground/`", la pregunta pasó a ser "¿quién?" y se resolvió en minutos. **Ante un fallo intermitente, reproducirlo fuera del framework antes de tocar el framework.**

  El agente quedó detenido y deshabilitado (`launchctl bootout` más `disable`), y **no se vuelve a activar**: es una decisión del autor, tomada tras meses de incidentes con la sincronización a Drive, no una medida temporal mientras se buscaba la causa. El plist sigue en `~/Library/LaunchAgents/com.jgil.sync-obsidian-gdrive.plist` por si se quiere borrar a mano.

## Alrededor del vault

- **Publicación web:** visor estático con Quartz.
- **Captura móvil:** integración ligera por Telegram.

## Para el chat de comandos y epics

Anotado desde el chat de specs el 2026-10-18. Lo de comandos y tests vive además en el bloque "Lo decidido el 2026-10-18 sobre `tuku process cycle`" de arriba.

### Comandos

- **`cycle_type` pasó a `cycle_name` y luego a la tabla de `ciclo.user.md` (2026-10-19).** Lo que sigue describe el paso intermedio. El chat de specs lo hizo en [`config.py`](src/tuku/config.py) (`Configuracion.nombres_de_ciclo`, una tupla con `("semana",)` por defecto), en una línea de `CAMPOS_REQUERIDOS` de [`doctor.py`](src/tuku/doctor.py), en el template (`reglas/config.tuku.md` y su README) y en `test_config.py` y `test_init.py`. Revisarlo al integrar. Sigue sin uso: nada abre ciclos con él todavía.
- **Vaults ya sembrados con `cycle_type`.** Ahora lo ignoran y usan `semana`. Decidir si `doctor config` avisa de la fila vieja.
- **`process cycle`:** `--from`, `--to`, `--name`, `--force`, sin `--at`. Un `--from` anterior al del ciclo abierto escribe un ciclo histórico en `bitacoras/` con `--name` y sin verificar contra los vecinos ([`spec/ciclo.md`](spec/ciclo.md), "Abrir el siguiente ciclo").
- **`doctor cycle` reporta hoyos y solapes** entre los ciclos de `bitacoras/`, sin rechazar nada. Hoy solo revisa `AHORA.md`.
- **`context cadence`:** las cadencias vigentes de todo el árbol en un texto, cada una con su `CADENCIAS.md` ([`spec/cadencias.md`](spec/cadencias.md)). La firma de `context` no cambia.
- **El nombre de la bitácora cerrada lleva el ciclo** (`bitacora-DESDE-HASTA-CICLO.md`) cuando exista `cycle close`.

### Epics
- **Epic 010, el tutorial entero** ([`010-00`](tests/escenarios/010-00-el-tutorial.md)). El arnés ya existe: `uv run python tests/scripts/test-tui.py tutorial [capítulos]` ([`tutorial.py`](tests/scripts/tutorial.py)). Falta correrlo con un agente real y ajustar lo que el primer pasaje destape. Las ediciones a mano son un callout `> [!warning] Edita a mano` con bloque `edit` y el arnés las aplica. Los capítulos 7 a 10 prometen lo que dependen de los epics 004, 006 y 007: el flujo del lunes (rechazo de `entry create`, aviso, cierre, `process cycle`), `cycle close`, la cadencia declarada que emite lo que falta de la semana en curso, y `tuku context todo --late`.
