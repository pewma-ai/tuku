# TODO de TUKU

Lo que hay que hacer y no bloquea a nadie. Nada de aquí condiciona el orden de los epics: [`devel/epics.md`](devel/epics.md) sigue siendo la única fuente de verdad sobre qué se construye y en qué estado está. Un ítem sale de aquí cuando entra a un epic o cuando se hace.

## Instalación y entorno

- **Configuración del agente tras la instalación:** `uv tool install` y [`tuku init`](src/tuku/init.py) dejan el vault escrito, pero no dejan configurado al agente que lo va a leer. Falta un paso complementario que aplique la configuración del agente elegido por el autor. El caso real es Claude Code: hardcodea `CLAUDE.md` como archivo de memoria y no expone ninguna opción para renombrarlo, así que leer el [`AGENTS.md`](AGENTS.md) del vault exige un hook `SessionStart` que lo descubra e inyecte. Codex lee `AGENTS.md` de forma nativa y Gemini usa `GEMINI.md`. Queda por decidir la forma: `tuku init --agente claude`, un comando propio, o solo instrucciones documentadas que el autor ejecuta a mano. Sea cual sea, el principio 1 exige el equivalente "A mano".
- **Prueba con usuario ajeno:** verificar instalación y primer registro leyendo solo [`AGENTS.md`](AGENTS.md). Es el criterio de salida pendiente del epic 001.

## Spec por alinear

- **Cómo se llama el subtipo de una nota tipada.** [`spec/notas.md`](spec/notas.md) dice que una nota tipada declara `tipo:` en su frontmatter, y con OKF el campo `type` ya está tomado y vale `Note` para todas. El subtipo (persona, lugar, concepto) necesita otro nombre, en inglés como el resto del frontmatter, y la lista sigue siendo abierta y viviendo en `### Tipos de nota` del libro de estilo. Es una decisión de diseño, no una corrección de redacción: lo decide el epic que escriba la primera nota tipada.

## Sistema

- **Endurecimiento:** casos de error, reconstrucción completa (`tuku rebuild`) e idempotencia global sobre el sistema entero. Un error del autor nunca se rechaza, se reporta. Era la fase 8 y no agrega capacidades, cierra huecos.

## Alrededor del vault

- **Publicación web:** visor estático con Quartz.
- **Captura móvil:** integración ligera por Telegram.
