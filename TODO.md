# TODO de TUKU

Lo que hay que hacer y no bloquea a nadie. Nada de aquí condiciona el orden de los epics: [`devel/epics.md`](devel/epics.md) sigue siendo la única fuente de verdad sobre qué se construye y en qué estado está. Un ítem sale de aquí cuando entra a un epic o cuando se hace.

## Instalación y entorno

- **Configuración del agente tras la instalación:** `uv tool install` y [`tuku init`](src/tuku/init.py) dejan el vault escrito, pero no dejan configurado al agente que lo va a leer. Falta un paso complementario que aplique la configuración del agente elegido por el autor. El caso real es Claude Code: hardcodea `CLAUDE.md` como archivo de memoria y no expone ninguna opción para renombrarlo, así que leer el [`AGENTS.md`](AGENTS.md) del vault exige un hook `SessionStart` que lo descubra e inyecte. Codex lee `AGENTS.md` de forma nativa y Gemini usa `GEMINI.md`. Queda por decidir la forma: `tuku init --agente claude`, un comando propio, o solo instrucciones documentadas que el autor ejecuta a mano. Sea cual sea, el principio 1 exige el equivalente "A mano".
- **Resuelto (2026-09-19): prueba con usuario ajeno:** verificada la instalación limpia (`uv tool install`) y primer registro a mano leyendo solo [`AGENTS.md`](AGENTS.md). Epic 001 cerrado.

## Superficie del CLI (decidida el 2026-10-18)

La gramática está en [`spec/cli.md`](spec/cli.md), "Sustantivo, verbo y parámetro".

### Quitar los `lint` y dejar solo `tuku doctor TEMA`

Tarea mecánica: no cambia ninguna regla, solo por dónde se invoca. El 2026-10-18 los cinco `lint` y su `tuku doctor TEMA` dieron el mismo código y el mismo resultado sobre un vault recién sembrado.

| Se borra | Se usa en su lugar |
| --- | --- |
| `tuku entry lint` | `tuku doctor entry` |
| `tuku todo lint` | `tuku doctor todo` |
| `tuku scope lint` | `tuku doctor scope` |
| `tuku cycle lint` | `tuku doctor cycle` |
| `tuku style lint` | `tuku doctor style` |
| `tuku note lint [ARCHIVO]` | `tuku doctor note [ARCHIVO]`, un tema nuevo |

1. Antes de tocar nada, corre `uv run pytest` y anota qué tests fallan. Hoy son 7: dos de `005-04` y cinco de `005-05`.
2. Borra el subparser `lint` de cada sustantivo, su función `_cmd_<sustantivo>_lint` y su entrada en el diccionario de comandos, en [`src/tuku/cli/entry.py`](src/tuku/cli/entry.py), [`todo.py`](src/tuku/cli/todo.py), [`scope.py`](src/tuku/cli/scope.py), [`note.py`](src/tuku/cli/note.py) y [`system.py`](src/tuku/cli/system.py) (`cycle lint` y `style lint`). `style` queda sin verbos: borra también el sustantivo. `cycle` conserva `open`.
3. En [`src/tuku/doctor.py`](src/tuku/doctor.py), agrega `"note"` al final de `TEMAS` y una revisión con la misma forma que las demás (`Revision("note", …)`) que llame a `note.lint_del_vault`.
4. `tuku doctor` acepta un `ARCHIVO` opcional solo con el tema `note`. `tuku doctor note notas/reunion-con-viana.md` revisa ese archivo y funciona fuera de un vault, igual que hoy `tuku note lint ARCHIVO`. Con cualquier otro tema, un `ARCHIVO` es error de uso: `parser.error`, que sale con 2.
5. Cambia cada texto que nombra `tuku X lint` por `tuku doctor X`: mensajes y ayudas de `src/tuku/`, `spec/`, `docs/`, `template/vanilla/` y `DEVEL.md`.
6. En `tests/escenarios/*.md` y en los `tests/**/test_*.py` que invocan el CLI, cambia el comando y la salida esperada: donde decía `sin hallazgos.`, `todo lint: …` o `tuku entry lint: …`, ahora dice `doctor todo: …` o `doctor entry: …`. Los unit tests que llaman directo a `lint()` o `lint_del_vault()` quedan como están.
7. Deja intacto: los nombres internos (`lint.py`, `cyclelint.py`, las funciones `lint` y `lint_del_vault`), `devel/iteraciones/`, `devel/VAULT/`, `src/tuku/_home/` (se genera) y `playground/`.

8. En [`spec/tuku.md`](spec/tuku.md), "Lo que se retira", borra las seis líneas de los `lint`, y en "Mantención" quita "(pendiente, …)" del tema `note` y `# pendiente: ARCHIVO` de la firma de `doctor`.

Queda hecho cuando:

- `rg -n "(entry|todo|scope|cycle|note|style) lint" --glob '!devel/iteraciones/**' --glob '!devel/VAULT/**' --glob '!src/tuku/_home/**' --glob '!TODO.md'` solo encuentra nombres de funciones Python.
- `uv run pytest` falla en los mismos tests del paso 1 y por la misma causa. Los de `005-05` cambian de comando y siguen rojos por lo suyo.
- `uv run ruff check` y `uv run mypy src` pasan.

Si algún `tuku doctor X` da otro código o reporta otros hallazgos que el `tuku X lint` que reemplaza, detente y repórtalo: no ajustes el test para que pase.

### El resto, por implementar

Hecho el 2026-10-18 ([`devel/iteraciones/2026-10-18.md`](devel/iteraciones/2026-10-18.md)): escritura atómica con reintentos, `regenerate` con su tabla de dependencias, `entry update` y `entry move`, registros sin hora, `tuku context`, `tuku process`, el `AGENTS.md` de dos invocadores, enlazar al registrar con la columna "Enlazable", `todo close TEXTO`, `Actividad reciente` de doce meses, `scope create --since`, el retiro de `cycle open` y `vocab show`, y los ejemplos en la ayuda ([`ejemplos.py`](src/tuku/cli/ejemplos.py)). Falta:

- **Retirar `tuku vocab show` y `cycle open` en los escenarios históricos** de [`005-00`](tests/escenarios/005-00-el-dia-ciento-cincuenta.md): es un análisis de esa fecha y se dejó como estaba.
- **Medir el `AGENTS.md` de dos invocadores** con la cadena agéntica del epic 003: cambió la tabla (`tuku context` al empezar, filas de corrección separadas, `process cycle`, `todo close TEXTO`) y la suite no agéntica no lo cubre.
- **Cada cambio de esta lista toca [`spec/tuku.md`](spec/tuku.md):** se quita el `# pendiente` de lo implementado y la línea de "Lo que se retira" de lo que sale del CLI. [`tests/unitarios/test_superficie.py`](tests/unitarios/test_superficie.py) falla y dice qué línea cambiar si se olvida.

## Ciclos con nombre, config y libro de estilo (conversación del 2026-10-18)

Tres temas que salieron de revisar cómo se declara el ciclo del autor, que trabaja por turnos. Están decididos en su dirección y se implementan después de la conversación sobre `reglas/config.tuku.md`, que merece su propia sesión. **Hasta entonces no se tocan los comandos que leen la config ni el libro de estilo.**

### El ciclo tiene nombre y el largo no es fijo

Hoy el ciclo es la semana de lunes a domingo, fija en el código. `cycle_type` es un campo requerido de la config ([`src/tuku/config.py`](src/tuku/config.py), [`src/tuku/doctor.py`](src/tuku/doctor.py)) que se lee y no se usa. El autor trabaja turnos de martes a martes (8 días) y descansa de miércoles a lunes (6 días), pero hay turnos de 10 o 14 días y vacaciones: en mac-jpgil cada fase es un ciclo y un agente le pregunta el rango al cambiar de ciclo, a partir de [`Capacidad.md`](../mac-jpgil/estrategia/Capacidad.md).

Lo decidido:

- **`cycle_name` reemplaza a `cycle_type`.** Admite una lista, `cycle_name = [turno, descanso]`, y `tuku` la lee y actúa en consecuencia. Por defecto vale `semana`.
- **Cada ciclo declara cuál es** en su frontmatter, `cycle: turno`, junto a `status`, `from` y `to`, tanto en `AHORA.md` como en la bitácora cerrada. La lista de la config solo da los nombres posibles: nada más dice qué fase corre hoy.
- **El ciclo siguiente es el siguiente de la lista**, y al llegar al final vuelve al primero. Con un solo nombre, es el mismo.
- **Con `semana` el rango se deriva** (lunes a domingo). **Con cualquier otro nombre el rango es obligatorio**: el agente le pregunta al autor hasta qué día va y abre el ciclo con ese rango. Decidir el rango es del autor y abrirlo con un rango dado es determinista.
- **La bitácora cerrada lleva el nombre del ciclo**: `bitacora-2026-08-11-2026-08-18-turno.md`. `plan-…-turno.md` y `resumen-…-turno.md` ya lo llevaban en [`spec/vault.md`](spec/vault.md).
- **La plantilla [`reglas/plantilla/AHORA.md`](template/vanilla/reglas/plantilla/AHORA.md) deja de traer siete días fijos**: genera un encabezado por cada fecha entre `from` y `to`.

Los horizontes del libro de estilo se nombran con el ciclo: `esta semana` y `próxima semana` pasan a poder escribirse con `$cycle_name[0]`. Lo que significa cada uno, según el autor:

| Horizonte | Hasta cuándo | Ejemplo con `[turno, descanso]`, estando en turno |
| --- | --- | --- |
| `este $cycle_name[0]` | El ciclo en curso | Este turno |
| `próximo $cycle_name[0]` | El siguiente ciclo de ese nombre, pasando por los demás | El turno que viene después del descanso |
| `fin de mes` | El último día del mes, menos uno, por si acaso | 30 en un mes de 31 días |

Con `semana`, `próxima semana` es desde el lunes siguiente, fijo. El artículo (`este` o `esta`) lo escribe el autor en su tabla, porque no se deduce del nombre. Estando en el descanso, `este turno` es un error del autor, no un horizonte válido: el comando rechaza sin escribir, nombra la corrección (`próximo turno`, o la fase en curso) y el agente desambigua con el autor. Queda abierto si, estando en el descanso, la escalera debe empezar por `este descanso` para tener dónde poner lo de esa fase.

**Defecto relacionado, sin resolver.** El libro de estilo promete que renombrar un horizonte no rompe nada, y no es así: [`regenerate.py`](src/tuku/regenerate.py) selecciona los pendientes del callout del ciclo por el texto literal `esta semana` (`todo.ESTA_SEMANA`), y `todo open` usa esa misma constante de valor por defecto. Quien renombre el primer horizonte a `este turno` deja el callout vacío, sin aviso. Debe seleccionar por posición (el primer escalón de la escalera del autor), no por texto.

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

## Agente

- **El contexto que se inyecta al agente.** Decidido el 2026-10-18: `tuku context [TEMA] [--since]`, en [Superficie del CLI](#superficie-del-cli-decidida-el-2026-10-18).

## Reglas del vault

- **Validar el `AGENTS.md` adelgazado contra un agente vivo.** El refactor del 2026-09-09 bajó de la raíz todo lo que dice *cómo* se escribe un registro: los campos de `tuku entry create`, el día y la hora, `--when` y `--horizon` pasaron a [`template/vanilla/reglas/bitacora.tuku.md`](template/vanilla/reglas/bitacora.tuku.md), y la elección de ámbito a [`template/vanilla/ambitos/AGENTS.md`](template/vanilla/ambitos/AGENTS.md). La raíz volvió a enrutar y nada más.

  Lo que hay que medir es una sola cosa, y no es la longitud: **si la regla que se carga tarde llega a tiempo**. Con `ambitos/AGENTS.md` el agente entra al directorio y lo lee; con `reglas/bitacora.tuku.md` no hay un "entrar" equivalente, así que la raíz tiene que mandar a leerlo antes de la primera llamada a `entry create` y eso puede no ocurrir. Los dos párrafos que bajaron son justamente los que se escribieron porque dos agentes distintos fallaron sin ellos, así que un refactor que los aleje demasiado reintroduce esos fallos.

  Se mide con la cadena del epic 003, que ya distingue el modelo que alcanza del que no. Es un experimento con resultado esperado, no una revisión de redacción: si falla, la regla vuelve a subir y queda escrito que la cascada tiene un piso.

- **El mínimo viable es Deepseek v4.1 Flash.** Ese es el suelo contra el que se valida: si el `AGENTS.md` no funciona con él, no funciona. Cualquier cosa más tonta que eso **no se ha probado que no falle, ni se va a probar**. No es un límite provisional a la espera de más presupuesto: es hasta dónde llega la promesa del vault, y por debajo de ahí el problema deja de ser del `AGENTS.md`.

  Tiene consecuencia de diseño y por eso está escrito acá y no en un comentario: una regla que solo obedece un modelo caro no es una regla del vault, es una que se aprovecha de que el modelo adivina. Cuando algo falle con el mínimo, la primera hipótesis es que la regla está mal escrita, no que el modelo es corto.

## Tutorial

- **La historia de Andrea no es coherente entre capítulos** ([`docs/tutorial/`](docs/tutorial/README.md), revisión del 2026-10-16):
  - En el capítulo 2, la sección "Cuando quedó mal dicho" pide fusionar Liceo Los Robles con `personal` y no le dice al lector que lo rechace. Si confirma, `personal` desaparece y los capítulos siguientes dejan de funcionar.
  - El capítulo 3 cierra el anticipo de una profesora Marcela que ningún capítulo anterior abrió, y usa un ámbito `compras` que no existe.
  - El capítulo 5 espera un seguimiento a "Los Robles", que en el capítulo 2 se renombró y quizás se fusionó.
  - En el capítulo 2, "cambiaron de categoría" usa en sentido coloquial una palabra que en TUKU es un término técnico (directorio sin página propia), y la línea 117 tiene un em dash.
  - El capítulo 2 anuncia resultados ("la fila desapareció", "las cuatro frases se desglosaron"), aunque el README del tutorial promete no anticiparlos.

## Sistema

- **Endurecimiento:** casos de error, regeneración completa (`tuku regenerate`) e idempotencia global sobre el sistema entero. Un error del autor nunca se rechaza, se reporta. Era la fase 8 y no agrega capacidades, cierra huecos.

## Suite de escenarios

- **Resuelto (2026-09-10): tests en Epic 002 para entradas y pendientes sin fecha (fallback a hoy):** Se implementó `_congelar_tiempo` en [`tests/scripts/gherkin.py`](tests/scripts/gherkin.py) para interceptar `TUKU_NOW="AAAA-MM-DD HH:MM"` en bloques bash y congelar deterministamente `date.today()` y `datetime.now()` durante llamadas en proceso a `cli.main`, sin tocar el código de producción. Probado en `002-02-registro-en-su-dia`.

- **Resuelto (2026-09-10): cobertura de comandos directos para pendientes:** Se incorporaron escenarios BDD en `002-04` (`tuku todo open`) y `002-05` (`tuku todo close`) verificando que operan de forma idempotente, actualizan `PENDIENTES.md` y estampan su huella cronológica en `AHORA.md` respetando la regla normativa de huella obligatoria.

- **Resuelto (2026-09-08): no era un flake, era un sincronizador restaurando archivos borrados.** La suite fallaba en cerca de la mitad de las corridas, en cascada, con `<slug>/<escenario> ya existe después de limpiar el epic`. La causa no estaba en los tests: un LaunchAgent del autor, `com.jgil.sync-obsidian-gdrive`, corría `rclone bisync` **bidireccional** entre `~/Code/MaC` y Google Drive, con el filtro `+ *.md`, que incluye todos los Markdown a cualquier profundidad. Un vault de TUKU es puro Markdown, así que cada corrida sincronizaba `playground/` con la nube: los tests borraban, y rclone reponía desde Drive.

  Cómo se acorraló, por si vuelve algo parecido: el fallo se reprodujo **sin pytest**, con un script que solo copiaba y borraba árboles con el mismo patrón (`rm -rf 001-* 002-*` y treinta carpetas de golpe). Ese reproductor de veinte segundos permitió medir por ubicación, y la frontera fue nítida: `/tmp`, `~` y `~/Code` limpios; `~/Code/MaC` fallando. Esa frontera es la raíz del bisync, y `lsof` más el log del agente pusieron el nombre.

  La lección de método: llamarlo "flake" costó horas. Un flake invita a reintentar, y por eso los primeros cuatro intentos fueron reintentos, esperas y verificaciones, o sea curar el síntoma. En cuanto se nombró como "hay un intruso escribiendo en `playground/`", la pregunta pasó a ser "¿quién?" y se resolvió en minutos. **Ante un fallo intermitente, reproducirlo fuera del framework antes de tocar el framework.**

  El agente quedó detenido y deshabilitado (`launchctl bootout` más `disable`), y **no se vuelve a activar**: es una decisión del autor, tomada tras meses de incidentes con la sincronización a Drive, no una medida temporal mientras se buscaba la causa. El plist sigue en `~/Library/LaunchAgents/com.jgil.sync-obsidian-gdrive.plist` por si se quiere borrar a mano.

- **Dos corridas simultáneas de la suite se pisan.** `playground/` es compartido y el `XXX-00` de un epic lo limpia al empezar, así que si el autor corre `uv run pytest` mientras otra corrida está a mitad, la segunda borra lo que la primera está usando. El síntoma es el mismo `ya existe después de limpiar el epic`, culpando a un escenario inocente. Se arregla con un lock en `playground/` (un archivo con el pid, borrado al terminar) que haga fallar la segunda corrida diciendo qué está pasando, en vez de dejar que las dos se destrocen.

- **Quitar el andamiaje defensivo que se puso mientras se buscaba la causa.** Con el sincronizador fuera, sobran los reintentos y las verificaciones que hoy tiene [`tests/scripts/vault.py`](tests/scripts/vault.py) y [`tests/scripts/gherkin.py`](tests/scripts/gherkin.py): el borrado con reintentos (`_borrar`), el apartado por renombre (`_apartar`), el barrido de apartadas con su `atexit`, y la insistencia de `_verificar_limpio`. Ninguno resolvió nada y todos oscurecen el código. Conviene medir sin ellos antes de borrarlos: si la suite aguanta 40 corridas limpias, se van.

- **Retirar [`tests/scripts/cadena.py`](tests/scripts/cadena.py).** Los epics 001 y 002 están migrados enteros: todos sus escenarios toman los comandos del `.md` mediante [`tests/scripts/gherkin.py`](tests/scripts/gherkin.py), y ya ningún arnés usa `preparar_paso`. El módulo queda sin consumidores, salvo `instantanea` y `delta`, que se reexportan desde `vault`. Se borra cuando el epic 003 confirme que no lo necesita.

## Alrededor del vault

- **Publicación web:** visor estático con Quartz.
- **Captura móvil:** integración ligera por Telegram.
