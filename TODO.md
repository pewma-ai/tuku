# TODO de TUKU

Lo que hay que hacer y no bloquea a nadie. Nada de aquí condiciona el orden de los epics: [`devel/epics.md`](devel/epics.md) sigue siendo la única fuente de verdad sobre qué se construye y en qué estado está. Un ítem sale de aquí cuando entra a un epic o cuando se hace.

## Instalación y entorno

- **Configuración del agente tras la instalación:** `uv tool install` y [`tuku init`](src/tuku/init.py) dejan el vault escrito, pero no dejan configurado al agente que lo va a leer. Falta un paso complementario que aplique la configuración del agente elegido por el autor. El caso real es Claude Code: hardcodea `CLAUDE.md` como archivo de memoria y no expone ninguna opción para renombrarlo, así que leer el [`AGENTS.md`](AGENTS.md) del vault exige un hook `SessionStart` que lo descubra e inyecte. Codex lee `AGENTS.md` de forma nativa y Gemini usa `GEMINI.md`. Queda por decidir la forma: `tuku init --agente claude`, un comando propio, o solo instrucciones documentadas que el autor ejecuta a mano. Sea cual sea, el principio 1 exige el equivalente "A mano".
- **Prueba con usuario ajeno:** verificar instalación y primer registro leyendo solo [`AGENTS.md`](AGENTS.md). Es el criterio de salida pendiente del epic 001.

## Spec por alinear

- **Cómo se llama el subtipo de una nota tipada.** [`spec/notas.md`](spec/notas.md) dice que una nota tipada declara `tipo:` en su frontmatter, y con OKF el campo `type` ya está tomado y vale `Note` para todas. El subtipo (persona, lugar, concepto) necesita otro nombre, en inglés como el resto del frontmatter, y la lista sigue siendo abierta y viviendo en `### Tipos de nota` del libro de estilo. Es una decisión de diseño, no una corrección de redacción: lo decide el epic que escriba la primera nota tipada.

## Sistema

- **Endurecimiento:** casos de error, reconstrucción completa (`tuku rebuild`) e idempotencia global sobre el sistema entero. Un error del autor nunca se rechaza, se reporta. Era la fase 8 y no agrega capacidades, cierra huecos.

## Suite de escenarios

- **Resuelto (2026-09-08): no era un flake, era un sincronizador restaurando archivos borrados.** La suite fallaba en cerca de la mitad de las corridas, en cascada, con `<slug>/<escenario> ya existe después de limpiar el epic`. La causa no estaba en los tests: un LaunchAgent del autor, `com.jgil.sync-obsidian-gdrive`, corría `rclone bisync` **bidireccional** entre `~/Code/MaC` y Google Drive, con el filtro `+ *.md`, que incluye todos los Markdown a cualquier profundidad. Un vault de TUKU es puro Markdown, así que cada corrida sincronizaba `playground/` con la nube: los tests borraban, y rclone reponía desde Drive.

  Cómo se acorraló, por si vuelve algo parecido: el fallo se reprodujo **sin pytest**, con un script que solo copiaba y borraba árboles con el mismo patrón (`rm -rf 001-* 002-*` y treinta carpetas de golpe). Ese reproductor de veinte segundos permitió medir por ubicación, y la frontera fue nítida: `/tmp`, `~` y `~/Code` limpios; `~/Code/MaC` fallando. Esa frontera es la raíz del bisync, y `lsof` más el log del agente pusieron el nombre.

  La lección de método: llamarlo "flake" costó horas. Un flake invita a reintentar, y por eso los primeros cuatro intentos fueron reintentos, esperas y verificaciones, o sea curar el síntoma. En cuanto se nombró como "hay un intruso escribiendo en `playground/`", la pregunta pasó a ser "¿quién?" y se resolvió en minutos. **Ante un fallo intermitente, reproducirlo fuera del framework antes de tocar el framework.**

  El agente quedó detenido y deshabilitado (`launchctl bootout` más `disable`), y **no se vuelve a activar**: es una decisión del autor, tomada tras meses de incidentes con la sincronización a Drive, no una medida temporal mientras se buscaba la causa. El plist sigue en `~/Library/LaunchAgents/com.jgil.sync-obsidian-gdrive.plist` por si se quiere borrar a mano.

  Queda pendiente **limpiar de Google Drive los vaults de prueba** que se subieron durante meses de corridas.

- **Quitar el andamiaje defensivo que se puso mientras se buscaba la causa.** Con el sincronizador fuera, sobran los reintentos y las verificaciones que hoy tiene [`tests/scripts/vault.py`](tests/scripts/vault.py) y [`tests/scripts/gherkin.py`](tests/scripts/gherkin.py): el borrado con reintentos (`_borrar`), el apartado por renombre (`_apartar`), el barrido de apartadas con su `atexit`, y la insistencia de `_verificar_limpio`. Ninguno resolvió nada y todos oscurecen el código. Conviene medir sin ellos antes de borrarlos: si la suite aguanta 40 corridas limpias, se van.

- **Retirar [`tests/scripts/cadena.py`](tests/scripts/cadena.py).** Los epics 001 y 002 están migrados enteros: todos sus escenarios toman los comandos del `.md` mediante [`tests/scripts/gherkin.py`](tests/scripts/gherkin.py), y ya ningún arnés usa `preparar_paso`. El módulo queda sin consumidores, salvo `instantanea` y `delta`, que se reexportan desde `vault`. Se borra cuando el epic 003 confirme que no lo necesita.

## Alrededor del vault

- **Publicación web:** visor estático con Quartz.
- **Captura móvil:** integración ligera por Telegram.
