# Epic 005 · El día ciento cincuenta

> **Marco:** [Brief de TUKU](../../docs/brief.md) · [Principios normativos](../../docs/principios.md) · [Especificaciones](../../spec/README.md) · [Corpus de la Pyme](../../corpus/referencia/referencia-pyme.md) · [Tutorial, capítulo 4](../../docs/tutorial/04-una-semana-despues.md)

Lo del epic 002 sobre un vault que ya tiene historia: ámbitos anidados con registros, pendientes en varios escalones, una bitácora cerrada y notas. El vault deja de ser una página en blanco y cada comando se enfrenta a lo que ya hay.

## Qué entrega el epic

1. **Las dos semanas de Andrea Bustos** ([`referencia-pyme.md`](../../corpus/referencia/referencia-pyme.md)) escritas con un comando por hecho, la primera archivada a mano en `bitacoras/` y la segunda sobre ella: el vault poblado del que parten los demás escenarios.
2. **Lo derivado se reconstruye** sobre ese vault (principio 9), y un vault armado comando a comando ya está regenerado.
3. **Reorganizar con historia** sin romper un link, bitácoras cerradas incluidas (principio 7).
4. **Los pendientes atrasados se calculan** y un comando los informa y las filas quedan donde están.
5. **Las notas tejidas**: el `## Ver además` verificable y la primera nota tipada, una persona.
6. **El agente con historia**: elige el ámbito por las keywords y espera al autor cuando dos personas tienen el mismo nombre.

## Qué se verifica

- **Superficie del vault:** diff entre estados encadenados, con estricta idempotencia (el segundo pase da diff vacío).
- **Superficie del comando:** códigos de salida y mensajes que nombran la corrección, según [`spec/cli.md`](../../spec/cli.md).
- **El agente (solo `005-06`):** la traza de lo que ejecutó, no lo que dijo.
- **Aceptación humana:** legibilidad en Obsidian del vault de Andrea.

## Escenarios del epic

Cada `.md` parte del vault que deja el `005-01`; dentro de él los escenarios se encadenan.

- [`005-01-las-dos-semanas-de-andrea.md`](005-01-las-dos-semanas-de-andrea.md): el árbol del negocio, la primera semana, el cierre a mano, la segunda semana y repetirla sin cambios.
- [`005-02-lo-derivado-se-reconstruye.md`](005-02-lo-derivado-se-reconstruye.md): borrar lo derivado y regenerar devuelve el mismo vault.
- [`005-03-reorganizar-con-historia.md`](005-03-reorganizar-con-historia.md): mover y renombrar ámbitos anidados, con una bitácora cerrada que los enlaza.
- [`005-04-los-atrasados-se-calculan.md`](005-04-los-atrasados-se-calculan.md): qué venció, con cada fila donde estaba.
- [`005-05-las-notas-de-la-pyme.md`](005-05-las-notas-de-la-pyme.md): notas con `## Ver además` y la primera nota tipada.
- [`005-06-el-agente-con-historia.md`](005-06-el-agente-con-historia.md): la Patricia y las dos Paulas. Agéntico.

## Por qué el vault tiene dos semanas y no ciento cincuenta días

El nombre del epic es el estado inicial (`ciclo-en-curso`: un vault con meses encima), no una cantidad. Lo que cambia de un vault vacío a uno poblado es que las cosas existen: un ámbito tiene registros, un pendiente viene de otra semana, un link apunta a una bitácora cerrada. Dos semanas del corpus bastan para eso, y repetirlas hasta llegar a ciento cincuenta días probaría el volumen y no el comportamiento. El volumen es una prueba de rendimiento y no pertenece a este epic.

Un vault no puede llegar a ser más que eso por comandos, porque `tuku cycle close` es del epic 006: la primera semana se archiva como lo haría Andrea con un editor (principio 1), y el escenario `005-01` lo escribe paso a paso.

## Cómo se leyó el corpus

La Parte 2 del corpus (la tabla de verdad) se tradujo a comandos con cuatro ajustes, que `005-01` repite: un registro nunca apunta a una categoría ni a una persona, un cuerpo no lleva wikilinks, un `(Hecho)` solo cierra un pendiente que estaba abierto, y un pendiente con día nace `con fecha`. Se agregó un registro, el de Paula Reyes, para tener dos Paulas.

La Parte 3 (el estado reconstruible) **no se usa como aserción**: contiene pendientes que ningún registro de la Parte 2 abre (renovar la patente, pedir cartulina, pagar el F29, evaluar un proveedor alternativo), porque los infiere quien la escribió. Las aserciones del `005-01` salen de aplicar la Parte 2 con la spec de hoy.

## Pendientes del epic

Lo que los escenarios encontraron, jerarquizado y con un identificador estable. Se trabajan en el orden de las tablas, y cada uno que se completa se tacha (`~~así~~`) sin borrarlo: qué hacer con la lista al cerrar el epic se decide entonces.

El orden sigue tres criterios: primero la sintaxis del CLI, que está en revisión y de la que cuelgan los nombres de varios pendientes; después lo que el diseño ya dice y el código no cumple (hay un test rojo que lo prueba y no hace falta decidir nada); al final lo que pide una decisión y los documentos que se contradicen. Cada fila nombra el test que la prueba, o dice por qué no lo tiene.

### S. La sintaxis del CLI está abierta

La superficie decidida el 2026-10-18 vive en [`spec/tuku.md`](../../spec/tuku.md) y la compara [`test_superficie.py`](../unitarios/test_superficie.py). Los escenarios usan la de hoy: el `.md` es la fuente ejecutable, así que un nombre nuevo cambia solo sus líneas `tuku`. Los nombres que este epic propone (`note create --subtype`, el verbo de postergar) siguen provisionales. Un nombre vive en el código, en `reglas/comandos.tuku.md`, en el `AGENTS.md` del template, en las specs y en los escenarios.

| Id | Pendiente |
| --- | --- |
| ~~S1~~ | ~~Los verbos de crear son tres: `entry add`, `scope create` y `note create`, más `todo open` y `cycle open`. `add` es el que desentona.~~ Resuelto el 2026-10-17: `entry add` pasó a `entry create`. `todo open` y `cycle open` se quedan, porque abren algo que después se cierra |
| ~~S2~~ | ~~`scope keywords NOMBRE PALABRA...` usa un sustantivo como verbo, y las keywords se dan de dos formas.~~ Resuelto el 2026-10-17: `scope update NOMBRE --keyword P` es la única forma; `--keyword` es repetible o admite varias palabras separadas por coma, y los espacios de una palabra pasan a guion (kebab-case). `scope create` usa la misma regla |
| ~~S3~~ | ~~Los temas de `doctor`, `fix` y `regenerate` son tres listas distintas; `doctor scope` se rechaza aunque `doctor` corre el lint de ámbitos.~~ Resuelto el 2026-10-17: un tema es el nombre de la cosa y `link`, `todo` y `scope` significan lo mismo en los tres comandos. `doctor TEMA` acepta el nombre de cada una de sus revisiones (`config`, `version`, `types`, `files`, `frontmatter`, `dispatch`, `link`, `cycle`, `entry`, `todo`, `style`, `scope`) y solo corre esa; `fix` acepta los que tienen arreglo (`link`, `todo`) y `regenerate` los que tienen derivado (`todo`, `scope`, `comandos`). Cada comando rechaza los que no le tienen sentido |
| ~~S4~~ | ~~Los alias en español cubrían la mitad de las opciones.~~ Resuelto el 2026-10-17 (lo decidió el autor): se quitan todos. Cada opción tiene una sola forma, en inglés (`--body`, `--scope`, `--at`, `--parent`, `--due`, `--horizon`, `--variant`, `--author`, `--body-file`, `--no-record`) |
| S5 | `--at` significaba tres cosas. Resuelto el 2026-10-18 para dos: `entry update` y `entry move` ubican con `--match` y `--at` queda solo para «cuándo ocurrió» (`spec/cli.md`). Falta `process cycle --at`, que pasa a `--from` y `--to` ([`TODO.md`](../../TODO.md), «Ciclos con nombre») |
| ~~S6~~ | ~~El CLI no tenía comandos de lectura: ni `todo list`, ni `scope list` o `scope tree`, ni `note list`.~~ Resuelto el 2026-10-18: `tuku context [TEMA] [--since]` lee `entry`, `scope` (el árbol con sus keywords), `todo` (abiertos y atrasados), `style` y `note` (las enlazables). No hay verbo `list`: B1 y B4 ya no dependen de decidirlo |
| ~~S7~~ | ~~`doctor note` aceptaba un archivo y los demás lint no; `vocab` y `style` eran nouns con un solo verbo.~~ Resuelto el 2026-10-18: `tuku doctor [TEMA] [ARCHIVO]` es la única entrada de revisión, `ARCHIVO` solo vale con `note`, y `vocab` y `style` se retiraron (`context style`) |
| S8 | `tuku init DIR` ya es posicional en `spec/tuku.md` y `--variant` se queda. Falta el campo `tuku_template` de `reglas/config.tuku.md`, que se decide en la conversación sobre la config |
| S9 | Falta un escenario de superficie para el CLI completo: [`devel/epics.md`](../../devel/epics.md) pide que todo epic que añada comandos fije su superficie con `tuku -h`. [`test_superficie.py`](../unitarios/test_superficie.py) compara cada firma de `spec/tuku.md` con argparse; el autor decide si basta o se escribe un escenario con `tuku -h` |
| ~~S10~~ | ~~Los nombres de ámbito y las keywords conservaban las mayúsculas del dictado (`Los-Robles`).~~ Resuelto el 2026-10-17 (lo pidió el autor): todo nombre de carpeta o archivo que TUKU genera, y las keywords, van en kebab-case en minúsculas (`importadora-andina`). Un ámbito escrito en mayúsculas encuentra el existente. Las notas ya lo cumplían, además sin tildes |

### A. Defectos: la spec ya lo dice y el CLI no lo cumple

| Id | Pendiente | Test |
| --- | --- | --- |
| ~~A1~~ | ~~La lista de hijos salía en orden de creación con `scope create` y `scope move`, y alfabética con `tuku regenerate`.~~ Resuelto el 2026-10-17: el callout de hijos se deriva siempre de las carpetas. Primero los ámbitos en orden alfabético, después cada categoría (`clientes/`, `proveedores/`) como callout interior plegable, separadas por `---`; `create`, `move` y `rename` lo dejan igual que `regenerate scope`. Antes las categorías no se veían: sus ámbitos no aparecían en la página de `negocio` | ~~`005-01` repetir, `005-02` ×2, `005-03` regenerar~~ |
| ~~A2~~ | ~~`tuku doctor note` sin archivo salía con error en un vault recién sembrado: revisaba `notas/AGENTS.md`, que es del sistema y no una nota.~~ Resuelto el 2026-10-18: `note.lint_del_vault` ya no cuenta `notas/AGENTS.md` | ~~`005-05` lint sin archivo~~ |
| ~~A3~~ | ~~`doctor note` no miraba los enlaces del cuerpo: un enlace ausente de `## Ver además` pasaba.~~ Resuelto el 2026-10-18: `doctor note` nombra cada enlace local del cuerpo que la sección no lista, con la línea y el `* [texto](destino) — para qué conecta` que se agrega | ~~`005-05` enlace sin motivo~~ |
| ~~A4~~ | ~~Las keywords de un ámbito repetían su nombre: `keywords: [importadora-andina, Gloria]`.~~ Resuelto el 2026-10-17 (lo vio el autor): el nombre ya es el de la carpeta y no va en la lista, que nace vacía (`keywords: []`) si no se dieron palabras, y una keyword que repite el nombre no entra. `scope rename` ya no toca las keywords | `tests/unitarios/test_scope_keywords.py` |
| ~~A5~~ | ~~`scope rename` de un ámbito con hijos dejaba rotos los links a los descendientes.~~ Resuelto el 2026-10-18: el rename recalcula con `link.reubicar` los links de los descendientes, como `scope move`. Lo cubre `test_scope_arbol` (renombrar `negocio` a `pyme` deja `doctor` sano) | ~~`test_scope_arbol` (sin escenario)~~ |
| ~~A6~~ | ~~`tuku entry update` sobre un pendiente le quitaba la marca `**pendiente**:` al registro y dejaba la fila de `PENDIENTES.md` con el texto viejo, y `tuku doctor todo` salía sin hallazgos aunque la fila quedara sin registro pendiente.~~ Resuelto el 2026-10-18: `entry update` conserva la marca y arrastra la fila; `doctor todo` nombra una fila que no tiene registro `**pendiente**` en `AHORA.md` ni en las bitácoras, con el `tuku todo open` que se lo devuelve | ~~`002-14` corregir un pendiente y fila sin registro~~ |

### B. Lo que la spec promete y no existe

| Id | Pendiente | Test |
| --- | --- | --- |
| ~~B1~~ | ~~Ningún comando informaba los atrasados: `spec/pendientes.md` dice «un comando lo informa» sin nombrarlo.~~ Resuelto el 2026-10-18: `tuku context todo --late` deja solo los pendientes con `Vence` anterior a hoy. El atraso por horizonte expirado sigue en E2 | ~~`005-04` (2 rojos y 2 guardas)~~ |
| ~~B2~~ | ~~No existía una nota tipada: `note create` no tenía `--subtype` y no se sembraba el archivo de reglas del tipo.~~ Resuelto el 2026-10-18: `note create --subtype persona` escribe el campo y rechaza un tipo que `### Tipos de nota` no lista; `tuku init` siembra `reglas/subtipos/persona.tuku.md`; y los links que `note create` pone al enlazar entran a `## Ver además` con el motivo «mencionada en el cuerpo» | ~~`005-05` tipada (3 rojos)~~ |
| ~~B3~~ | ~~Las keywords repetidas entre ámbitos pasaban sin aviso: `scope update escuela-los-maitenes --keyword Paula` salía con 0 y `tuku doctor` decía que el vault estaba sano, con `Paula` ya en `catalogo-marzo`.~~ Resuelto el 2026-10-18: `scope create` y `scope update` avisan por stderr (código 0) cuando la palabra, o el nombre de un ámbito, ya nombra a otro, y `tuku doctor scope` lo pregunta sin fallar | ~~`test_scope_keywords`~~ |
| B4 | `spec/pendientes.md` nombra «postergaciones» como comandos de `tuku todo`, y `todo` solo tiene `open`, `close` y `lint`: la escalera de horizontes no se baja con un comando. Falta el nombre y la forma | sin test: se escribe cuando B4 tenga nombre |
| ~~B5~~ | ~~El rechazo de `process cycle` con un ciclo con registros decía «mueve AHORA.md a bitacoras/…». Quien lo seguía al pie de la letra dejaba 9 links rotos en la bitácora (están a un nivel más adentro) y `doctor` fallaba sin que `fix link` pudiera repararlos.~~ Resuelto el 2026-10-18: el rechazo de `process cycle` y el de `entry create` fuera del ciclo dicen cómo archivar a mano (`ahora.como_cerrar`): copiar a la bitácora, `status: stable` y bajar un nivel los links (`](ambitos/` pasa a `](../ambitos/`). Mientras archivar el ciclo sea del epic 006 | ~~unitario `test_cycle_open`; `005-01` lo hace a mano~~ |

### C. El agente

| Id | Pendiente | Test |
| --- | --- | --- |
| C1 | Ante «le mandé el catálogo a la Paula», con dos Paulas en la historia, el agente eligió `catalogo-marzo` sin preguntar. Las specs ya dicen que se pregunta (X4). Falta que el `AGENTS.md` del template lo diga con un caso general, y medirlo con `005-06`, que es agéntico | `005-06` Paula (1 rojo, 1 saltado) |

### D. Documentos que se contradicen

| Id  | Pendiente                                                                                                                                                                                                                                                                                                                            | Dónde                                        |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------- |
| D1  | [`devel/epics.md`](../../devel/epics.md) describe el 005 con «enlaces automáticos desde el primer día» y asignación de ámbito «sin intervención». [`spec/ambitos.md`](../../spec/ambitos.md), «Nada se enlaza solo», dice que el cuerpo nunca se modifica ni se enlaza, y que elige el ámbito quien interpreta, leyendo las keywords | `devel/epics.md`, criterio de salida del 005 |
| D2  | El epic dice «resto de la fase 4» (cadencias) y «destilados». La tabla de fases pone las cadencias en el 006, y `spec/notas.md` deja el destilado fuera, para la fase 9                                                                                                                                                              | `devel/epics.md`                             |
| D3  | La página de un ámbito muestra solo el ciclo abierto: al archivar la primera semana desaparece el hilo de la cotización de Los Robles. `## Esta semana` y `## Actividad reciente` no están en ninguna spec                                                                                                                           | `scope.py`, `spec/ambitos.md`                |
| D4  | Un ámbito padre lista a sus hijos directos y los clientes de `negocio` cuelgan de la categoría `clientes`: ninguna página dice dónde están                                                                                                                                                                                           | `spec/ambitos.md`                            |
| D5  | El corpus de la Pyme contradice a la spec: `AGENTS.md` y `CADENCIAS.md` «obligatorios en cada directorio» (la spec: ausente es vacío), registros sobre categorías y personas, 17 de 29 `(Hecho)` sin pendiente abierto, un horizonte `sin fecha` que la spec descarta, y una Parte 3 que contiene pendientes que la Parte 2 no abre  | `corpus/referencia/referencia-pyme.md`       |
| D6  | El pendiente que abre `process cycle` («revisar la bitácora anterior») nace sin ámbito y con la hora del reloj, y su cierre cae en `personal`: apertura y cierre quedan en ámbitos distintos                                                                                                                                         | `spec/ciclo.md`, `spec/pendientes.md`        |

### E. De las pruebas mismas

| Id | Pendiente |
| --- | --- |
| ~~E1~~ | ~~Dos tests del `005-04` pasaban sin probar nada hasta que existiera B1.~~ Resuelto el 2026-10-18 con B1 |
| E2 | Falta el atraso por horizonte expirado (los cinco `esta semana` que siguen en `PENDIENTES.md` pasada la semana). Depende de cómo ruede un horizonte, que es del epic 006 |
| ~~E3~~ | ~~Cuatro tests del `005-05` caían en cascada de otros.~~ Resuelto el 2026-10-18 con A3 y B2 |

## Decisiones por confirmar

Tomadas al escribir los escenarios, para poder escribirlos. Cada una se confirma o se cambia aquí y en el escenario que la usa.

| Id | Decisión | Usa |
| --- | --- | --- |
| ~~X1~~ | ~~`tuku doctor todo` informa los atrasados como aviso, con código 0.~~ Cambiada el 2026-10-18: un atraso es un hecho del tiempo y no un defecto del vault, así que lo dice `tuku context todo --late`, no `doctor`. Sin verbo `list` | B1, `005-04` |
| ~~X2~~ | ~~`note create --subtype persona` y `reglas/tipos/persona.md` sembrado por `tuku init`.~~ Confirmada el 2026-10-18 con dos cambios: la carpeta se llama `reglas/subtipos/` (el archivo, `persona.tuku.md`) para no confundirse con `reglas/types.md`, y la tabla del libro de estilo es la única fuente de si un tipo es enlazable | B2, `005-05` |
| ~~X3~~ | ~~El cierre de la primera semana reescribe los links con `../`, como pide `spec/ambitos.md` al archivar, y el escenario lo hace con `sed` como lo haría Andrea~~ Confirmada el 2026-10-18 | B5, `005-01` |
| ~~X4~~ | ~~El test del agente acepta las dos conductas ante la ambigüedad (preguntar, o escribir en el ámbito que contiene a las dos) y rechaza elegir una de las dos.~~ Cambiada el 2026-10-18 por el autor: ante una ambigüedad de intención con consecuencias más allá de una línea en la bitácora, el agente pregunta y no escribe hasta que el autor conteste. `spec/flujo-informacion.md`, `spec/despacho.md` y el tutorial lo dicen así | C1, `005-06` |
| ~~X5~~ | ~~Los escenarios usan la sintaxis de hoy aunque esté en revisión (S): al cambiar un nombre se cambian sus líneas `tuku` y los tests no se tocan~~ Confirmada el 2026-10-18 | todos |

## Escenario: preparar el ambiente del epic

Dado el directorio de corridas
Cuando se borran las corridas anteriores del epic
```bash
rm -rf 005-*
```
Entonces el epic parte de cero

## Criterio de salida

Las dos semanas del corpus sobre un vault que ya tiene historia dejan el vault sano, regenerable byte a byte, reorganizable sin romper un link, con los atrasados informados por un comando y con una nota tipada. El agente elige el ámbito por las palabras que lo delatan y, cuando dos candidatos calzan, no adivina.
