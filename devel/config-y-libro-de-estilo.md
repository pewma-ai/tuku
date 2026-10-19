# Config de tuku y libro de estilo: inventario y propuesta

Material para la conversación sobre `reglas/config.tuku.md` que [TODO.md](../TODO.md) dejó pendiente ("Ciclos con nombre, config y libro de estilo") y que [plan-temporal-ciclos-y-libro.md](plan-temporal-ciclos-y-libro.md) llama Paso 5. Escrito el 2026-10-18 sobre el código de `devel` en `fc94839`. No cambia código ni spec: lista lo que hay y propone qué mover.

## Lo ya decidido

- **Criterio de ubicación** ([iteración del 2026-09-06](iteraciones/2026-09-06.md)): `config.tuku.md` guarda lo que las automatizaciones deterministas necesitan y no pueden adivinar. El libro de estilo guarda lo que gobierna cómo se escribe.
- **Ningún dato nuevo para automatizaciones entra al libro de estilo** ([2026-09-07](iteraciones/2026-09-07.md)).
- **El diseño del libro ya está en la spec**: [`spec/vault.md`](../spec/vault.md) reserva `reglas/autor.md`, `clasificaciones.md` y `horizontes.md` ("todavía no existe"), y el Paso 8 del plan temporal dice que el libro pasa a ser prosa estática de TUKU que transcluye esos archivos del autor.

## Dos tipos de configuración

| Tipo | Quién lo pone | Dónde vive | Ejemplos |
| --- | --- | --- | --- |
| **Sistema** | TUKU | El código y `template/`. Cambia con la versión | Marcas `**pendiente**` y `(Hecho)`, `type` de OKF, nombres de campo, códigos de salida, nombres de archivo en MAYÚSCULAS |
| **Usuario** | El autor | `reglas/` del vault | Zona horaria, nombres de ciclo, ámbito por defecto, formato de fecha, horizontes, clasificaciones |

Entre ambos va un tercero, los **valores por defecto del sistema que el usuario puede pisar** (límite de notas 25, formato `MMM/DD`). Hoy están repartidos por el código.

Hoy `config.tuku.md` mezcla los dos tipos: `tuku_template`, `tuku_version` y `origen` son sellos de la instalación (no se editan); `TZ`, `cycle_name`, `scope_default`, `date_format` y `context_note_limit` son preferencias del autor.

## Defectos hallados al hacer el inventario

1. **`TZ` no se aplica.** [`spec/bitacora.md`](../spec/bitacora.md) y [`spec/pendientes.md`](../spec/pendientes.md) (regla 6) dicen que HOY se evalúa en la zona horaria de `TZ`. [`cli/__init__.py:102`](../src/tuku/cli/__init__.py) hace `datetime.now()` con la zona del sistema. `Configuracion.zona_horaria` se lee y nadie la usa. Con una VM en otra zona, el día de un pendiente y su atraso salen mal.
2. **Dos fallbacks distintos para la zona**: `config.py` cae a `America/Santiago` y [`init.py`](../src/tuku/init.py) a `UTC`.
3. **El primer horizonte está escrito `esta semana`** ([`regenerate.py:230`](../src/tuku/regenerate.py), `todo_core.ESTA_SEMANA` y el valor por defecto de `todo open`). El libro de estilo promete que se renombra, y al hacerlo el callout del ciclo queda vacío sin aviso. Ya figura en TODO.md y en el Paso 7.
4. **Tres lectores sueltos del mismo archivo**: `formato_fecha`, `ambito_por_defecto` y `limite_de_notas` releen y reparsean `config.tuku.md` cada uno. Existe `leer_config`, pero exige que haya `LIBRO-DE-ESTILO.md` y por eso no se usa para esto.
5. **`TIPOS_REQUERIDOS` en `doctor` repite `reglas/types.md`**, que ya declara los tipos válidos en tiempo de ejecución.
6. **`**Nombre del autor:**` está escrito tres veces** (`config.py`, `style.py`, `init.py`). Desaparece con `reglas/autor.md`.

## Hecho el 2026-10-19 (sin commit)

Resuelve los defectos 1 a 4 y la decisión 1:

- [`config.leer_preferencias`](../src/tuku/config.py) es el único lector de `config.tuku.md`: devuelve `Preferencias` con el default de cada campo (zona del sistema, ciclo `semana`, formato `MMM/DD`, 25 notas). `formato_fecha`, `ambito_por_defecto` y `limite_de_notas` son envoltorios de una línea sobre él, y `leer_config` también lo usa.
- [`cli.main`](../src/tuku/cli/__init__.py) lee el reloj en la zona de `TZ` del vault (`config.hora_local`). Sin vault, sin config o con una zona vacía vale la del sistema; con una zona inexistente avisa por stderr y usa la del sistema. `now=` explícito (el arnés, `TUKU_NOW`) sigue mandando.
- `tuku doctor config` rechaza una `TZ` que el sistema no conozca (`TZ-DEL-SISTEMA` sin sustituir, por ejemplo).
- El fallback `America/Santiago` de `leer_config` desapareció; `init.TZ_FALLBACK` (`UTC`) queda solo para sembrar el vault.
- Pruebas: tres funciones nuevas en `test_config.py`.
- **Primer horizonte por posición** (defecto 3): [`regenerate.primer_escalon`](../src/tuku/regenerate.py) lee el primer escalón de `### Horizontes` y `vistas_en_ahora` titula y selecciona el callout del ciclo con él, así que renombrarlo a `este turno` ya no lo vacía. `todo open` sin horizonte ya usaba `escalera[0]`; solo quedaba `ESTA_SEMANA` como default de las funciones puras. Prueba: `test_el_primer_escalon_del_autor_titula_el_callout_aunque_lo_renombre`.

## Paso 2 del libro hecho el 2026-10-19 (sin commit)

- [`capitulos.py`](../src/tuku/capitulos.py): el parser de capítulos `##`, con la regla de una tabla por capítulo y sin mirar dentro de vallas de código.
- [`vocab.py`](../src/tuku/vocab.py) lee `reglas/bitacora.md`, `reglas/pendientes.md` y `reglas/notas.md` por capítulo (`FUENTES`); `config.leer_config` toma el autor de `reglas/autor.md`; `init --author` escribe ahí; `style.lint` revisa los archivos del autor, una tabla por capítulo y que cada transclusión del libro apunte a un archivo; `doctor` lee los `type` de TUKU del capítulo «Tipos de archivo» del libro y los propios de `reglas/types.md`, y exige los cuatro archivos nuevos. Sin fallback.
- Template: ocho archivos nuevos del autor en `reglas/` (`bitacora`, `pendientes`, `notas`, `ciclo`, `ambitos`, `cadencias`, `autor`, `lenguaje`), `types.md` solo para tipos propios y `LIBRO-DE-ESTILO.md` reescrito por entidad con sus transclusiones. Las referencias al libro en `AGENTS.md` y en los `reglas/*.tuku.md` apuntan ahora a `reglas/`.
- Escenarios `001-04` y `001-07` adaptados (el segundo suma «un capítulo con dos tablas»); `001-02` y `005-0X` pasaron sin cambios. 343 tests por defecto en verde. Los agénticos no se corrieron.
- Queda del plan: paso 3 (`context style` por capítulos con transclusión expandida), paso 4 (`context cadence`), paso 5 (`regenerate libro`, aviso en `doctor`) y paso 6 (fusionar tests).

## Pasos 3 a 6 del libro hechos el 2026-10-19 (sin commit)

- **Paso 3.** [`context style`](../src/tuku/context.py) devuelve el libro con cada `![](reglas/X.md)` expandido por [`capitulos.expandir`](../src/tuku/capitulos.py): de lo transcluido entran sus capítulos `##`, bajados a `###`; un archivo que falta sale marcado y una ruta que sale del vault cuenta como faltante. `--chapter NOMBRE` deja uno solo y, con un nombre que no existe, rechaza listando los que hay. Antes de armar el libro se leen los tres vocabularios, así que un archivo del autor roto rechaza ruidoso. Sin tema, `tuku context` trae de `style` solo `autor`, `lenguaje` y los vocabularios.
- **Paso 4.** `tuku context cadence`: las cadencias de todo `ambitos/`, de lo general a lo hondo, cada una con `origen` y `alcance`. No entra en "todos".
- **Paso 5.** `tuku regenerate libro` (también en el `regenerate` sin tema): copia del template del `tuku` instalado `LIBRO-DE-ESTILO.md`, `reglas/*.tuku.md` y `reglas/subtipos/*.tuku.md`. No toca `reglas/config.tuku.md` (valores del autor), `reglas/comandos.tuku.md` (derivado del CLI) ni ningún `reglas/*.md` sin `.tuku`. `tuku doctor version` avisa cuándo esa prosa difiere del template. El `AGENTS.md` del template manda al agente a `tuku context style --chapter X`. Specs: `cli.md`, `tuku.md`, `cadencias.md`, `vault.md`.
- **Paso 6.** Con la unión de arcos, 100 de los 209 unitarios no aportan un arco que otro no ejecute, pero eso no mide redundancia (casi cualquier test pasa por `archivo.leer`): solo se fundió `test_vocab` en una función. Lo demás son tests de reglas distintas, o ya se fundió en la fase 3.
- Verificación: 348 tests por defecto en verde, `ruff` y `mypy` limpios. Los agénticos no se corrieron.

## Inventario de lo hardcodeado

La columna "Destino" es una propuesta. **Config** es una fila nueva de `config.tuku.md`; **Archivo** es un archivo del autor en `reglas/`; **Sistema** se queda en el código.

| # | Qué | Dónde | Destino |
| --- | --- | --- | --- |
| 1 | Zona horaria que fija HOY | `cli/__init__.py`, `config.py`, `init.py` | **Config** (`TZ` ya existe): aplicarla |
| 2 | Primer horizonte `esta semana` y callout `Pendientes de esta semana` | `regenerate.py`, `todo_core.py`, `todo.py` | **Archivo** (`horizontes.md`): por posición |
| 3 | Escalera por defecto `esta semana`, `próxima semana`, `fin de mes` | `todo_core.ESCALERA` | **Sistema**: solo para funciones puras. El vault trae la suya |
| 4 | Horizonte `con fecha` | `todo_core.CON_FECHA` | **Sistema**: lo dice el libro como "horizonte del sistema" |
| 5 | Ventana de `context entry`: 2 días | `context.DESDE_POR_DEFECTO` | **Config** (`context_entry_days`) |
| 6 | Ventana de `context scope`: 7 días (otra constante con el mismo nombre) | `scope.DESDE_POR_DEFECTO` | **Config** (`context_scope_days`) |
| 7 | Meses de `## Actividad reciente` en la página de ámbito: 12 | `scope.MESES_DE_ACTIVIDAD` | **Config** (`scope_activity_months`) |
| 8 | Notas por tipo en `context note`: 25 | `config.LIMITE_DE_NOTAS` | Ya es **Config**; el 25 queda solo como fallback |
| 9 | Formato de fecha corta `MMM/DD` | `config.FORMATO_FECHA` | Ya es **Config** |
| 10 | Nombre de ciclo por defecto `semana` y semana de lunes a domingo | `ahora.SEMANA`, `config.py` | `cycle_name` ya es **Config**. El lunes como inicio podría ser `week_start`, y no urge |
| 11 | Pendiente que abre `process cycle`: `revisar la bitácora anterior` | `cycle.REVISAR_BITACORA` | **Archivo** (`reglas/plantilla/`), como el resto de lo que TUKU genera |
| 12 | Constancia de `scope create`: `**nota**: abrí el ámbito` | `scope.CONSTANCIA` | **Archivo** (plantilla). Hoy fuerza la clasificación `nota`, que el autor puede haber quitado de su tabla |
| 13 | Días y meses en castellano en los encabezados `## Lunes 7 de septiembre` | `init.DIAS`, `init.MESES`, `ahora.py` | **Sistema**, decisión abierta (ver abajo) |
| 14 | Cabecera de la tabla `| Horizonte | Vence | Ámbito | Detalle |` | `todo_core.CABECERA` | **Sistema**: el mismo caso del idioma |
| 15 | Marcas `**pendiente**`, `(Hecho)`, `**cadencia**` | `todo_core.py`, `lint.py` | **Sistema**: el libro ya dice que no se renombran |
| 16 | Nombres de carpeta y archivo (`ambitos`, `notas`, `bitacoras`, `reglas`, `AHORA.md`, `PENDIENTES.md`) | 68 apariciones en 13 módulos | **Sistema**, pero centralizar en un solo módulo |
| 17 | `ARCHIVOS_REQUERIDOS`, `CAMPOS_REQUERIDOS`, `SIN_FRONTMATTER` | `doctor.py` | **Sistema** |
| 18 | `TIPOS_REQUERIDOS` y `TYPE_DEL_CICLO` (`Logbook`, `Note`, `Config`...) | `doctor.py`, `cyclelint.py` | **Archivo** (`types.md`): derivar en vez de repetir |
| 19 | Encabezados de contrato del libro (`### Clasificaciones`, `### Horizontes`, `### Tipos de nota`) | `vocab.ENCABEZADOS` | **Sistema** hoy. Desaparecen si cada vocabulario es un archivo |
| 20 | `**Nombre del autor:**` | tres módulos | **Archivo** (`autor.md`) |
| 21 | `## Ver además`, callout `> [!abstract]+ En ` | `note.py`, `scope.py` | **Sistema** |
| 22 | Formato de hora `HH:MM` de 24 h | `entry.py`, `lint.py`, `ahora.py` | **Sistema**: contrato de la bitácora |
| 23 | Reintentos de escritura `(0.1, 0.3, 1.0)`, `ORIGEN`, `SELLO`, códigos de salida | `archivo.py`, `init.py`, `cli/helpers.py` | **Sistema** |
| 24 | Mensajes de la CLI en castellano | `cli/` | **Sistema**: es el producto |

Resultado: 8 candidatos reales a config o archivo (1, 2, 5, 6, 7, 11, 12, 20), 1 duplicación que se elimina (18), y el resto es contrato del sistema que no debe moverse. Pasar todo a config sería un error: cada fila que el autor puede cambiar es una fila que `doctor` debe validar.

## Propuesta para `config.tuku.md`

1. **Dos tablas en el mismo archivo.** `## Sellos de la instalación` (`tuku_template`, `tuku_version`, `origen`) y `## Preferencias`. El parser ya lee cualquier fila con campo entre backticks, así que no cambia el código. Dice de un vistazo qué se puede tocar.
2. **Un solo lector con valores por defecto tipados.** `leer_config` no depende del libro: lee la config y devuelve un dataclass con todos los defaults en un lugar. `formato_fecha`, `ambito_por_defecto` y `limite_de_notas` desaparecen, y también los dos fallbacks de zona.
3. **Filas nuevas, pocas**: `context_entry_days` (2), `context_scope_days` (7), `scope_activity_months` (12). Cada una con su default en el código y `doctor` valida que sea un entero positivo, como hoy con `context_note_limit`.
4. **Aplicar `TZ`** en `cli.main`: `datetime.now(ZoneInfo(tz))`. Si la zona no existe, `doctor` lo reporta y el comando usa la del sistema con un aviso.
5. **Precedencia**: vault, luego default del sistema. No hay variables de entorno ni archivo global del usuario: un vault es autónomo.

## El libro de estilo

### Qué hay hoy (124 líneas)

| Parte | Líneas (aprox.) | Es de |
| --- | --- | --- |
| El autor (nombre y primera persona) | 7 | Autor |
| Tres tablas de vocabulario (clasificaciones, horizontes, tipos de nota) | 40 | Autor |
| Cómo escribe el autor (4 reglas) | 6 | Autor, con la regla 4 atada al sistema |
| Plantillas en `reglas/` | 6 | Sistema |
| Cadencias: formato, cascada, ejemplo | 36 | Sistema |
| OKF y la tabla de `type` (transcluida) | 12 | Sistema |

Más de la mitad es manual de TUKU dentro de un archivo que dice "este archivo es suyo".

### Problemas para el agente

1. **Lo general no va primero.** El agente abre el libro para saber cómo escribir para este autor y encuentra el nombre, tres tablas, cadencias y OKF en ese orden. No hay un objetivo de dos líneas arriba.
2. **La transclusión `![Tipos de archivo](reglas/types.md)` es sintaxis de Obsidian.** Un agente que lee el archivo crudo ve un enlace de imagen y no la tabla. Hoy `tuku context style` entrega solo los vocabularios (`vocab.formatear`), sin el nombre del autor ni las reglas de escritura.
3. **Cada actualización de TUKU pisa lo que el autor editó** en las partes de sistema, porque están en el mismo archivo que sus datos. `tuku_version` avisa que hay versión nueva, pero no distingue qué parte del libro es del autor.
4. **Las tablas se encuentran por encabezado de prosa.** `vocab.leer` busca `### Horizontes` dentro de texto libre; si el autor reescribe esa sección, el vocabulario se pierde en silencio (lo mitiga `style lint`).

### Propuesta (2026-10-19, tras la conversación con el autor)

**El libro es de TUKU y viene de este repo; lo del autor vive en `reglas/` y el libro lo transcluye.** Una versión nueva de TUKU trae un libro nuevo y no toca nada de `reglas/`.

Reglas que salen de la conversación:

1. **El libro se organiza por entidad principal** (registro, pendiente, ciclo, ámbito, nota, cadencia, tipos de archivo, cómo escribe el autor). Cada sección dice en pocas líneas qué hace el comando `tuku` para esa entidad, nombra el comando que lo hace, y termina con `El detalle de este vault está en reglas/X.md` más la transclusión `![](reglas/X.md)`. Ejemplo: en cadencias, que `tuku` calcula las de esta semana concatenando las de cada ámbito, y el comando que las recolecta.
2. **El libro no lleva vocabulario.** Las clasificaciones, los horizontes y los tipos de nota viven en `reglas/` y se calculan con `tuku context style`. Lo que haya que agregar y no sea de una entidad va a las preferencias de autor o de lenguaje.
3. **Los tipos de archivo (OKF) tienen dos tablas**: los de TUKU en el libro (`Logbook`, `Todo`, `Scope`, `Note`, `Cadence`, `Config`, `Style Guide`) y los que el autor agregue en `reglas/types.md`. Hoy `types.md` mezcla ambos y `doctor` repite los de TUKU en `TIPOS_REQUERIDOS`.
4. **Cómo escribe el autor**: el libro fija lo que es de TUKU (el registro va en primera persona, y el pendiente en infinitivo con su cierre igual al texto, que es de lo que dependen los comandos). Las reglas de redacción propias van a `reglas/bitacora.md`.
5. **Cada capítulo es un `##` y lleva como máximo una tabla.** Vale para el libro y para cada archivo de `reglas/`. El parser deja de buscar encabezados dentro de prosa: pide el capítulo por su nombre y toma su única tabla (`## Clasificaciones` en `reglas/bitacora.md`, `## Tipos de archivo` en el libro). Una regla que `style lint` y `doctor` verifican (`error: el capítulo «X» tiene 2 tablas`). La regla es sobre el texto de cada archivo, no sobre el resultado expandido: el capítulo «Tipos de archivo» del libro tiene la tabla de TUKU, y la del autor llega por la transclusión desde `reglas/types.md`, que también cumple la regla por su cuenta. Los subtítulos `###` dentro de un capítulo son libres, pero sin tablas propias.
6. **No hay vaults antiguos**: sin fallback ni migración.

#### Convención de nombres en `reglas/`

Extiende la de MAYÚSCULAS contra minúsculas: **`X.tuku.md` es la prosa de TUKU para la entidad `X` y `X.md` es la personalización del autor.** Ya existen `bitacora.tuku.md` y `notas.tuku.md`; sus pares serían `bitacora.md` y `notas.md`. La spec lista hoy `clasificaciones.md` y `horizontes.md` sueltos; se cambia a esta forma, que sigue el pedido de personalizar por entidad.

| Entidad | Prosa de TUKU | Del autor | Qué trae |
| --- | --- | --- | --- |
| Registro | `reglas/bitacora.tuku.md` | `reglas/bitacora.md` | `## Clasificaciones` (tabla) y `## Escritura` (sus reglas de redacción) |
| Pendiente | `reglas/pendientes.tuku.md` | `reglas/pendientes.md` | `## Horizontes` (tabla) |
| Nota | `reglas/notas.tuku.md` | `reglas/notas.md` | `## Tipos de nota` (tabla con "Enlazable") |
| Ciclo | `reglas/ciclo.tuku.md` | `reglas/ciclo.md` | Cómo es su ciclo en palabras (el dato mecánico sigue en `config.tuku.md`) |
| Ámbito | | `reglas/ambitos.md` | Convenciones propias de sus ámbitos |
| Cadencia | `reglas/cadencias.tuku.md` | `reglas/cadencias.md` | Convenciones propias |
| Tipos de archivo | libro | `reglas/types.md` | Solo los que el autor agrega |
| Autor | | `reglas/autor.md` | Nombre, rol |
| Lenguaje | | `reglas/lenguaje.md` | Idioma, trato, registro, términos propios |

`tuku init` siembra los del autor con su estructura y los defaults de hoy (las tres primeras reglas de "Cómo escribe el autor" pasan a `bitacora.md`). `--autor` escribe `reglas/autor.md`.

#### Qué hace cada pieza

- **`tuku context style`** pasa de extraer vocabularios a leer el libro: devuelve los capítulos del libro, de lo general a lo específico, con cada transclusión `![](reglas/X.md)` expandida en su lugar. El agente corre este comando y no lee el libro crudo.
  - `--chapter NOMBRE` devuelve un solo capítulo (el nombre es el encabezado `##`, sin tabla aparte). Sin la opción, el libro completo.
  - Sin bloque de vocabulario al final: las tablas ya vienen dentro de su capítulo. El vocabulario "calculado" lo leen `doctor` y `style lint` desde `reglas/`.
  - La expansión es de un nivel. Un archivo que falta sale con la marca `falta reglas/X.md` y `doctor` lo reporta. Los encabezados de lo transcluido bajan un nivel para quedar dentro de su capítulo.
  - `tuku context` sin tema (decidido el 2026-10-19): trae de `style` solo `autor`, `lenguaje` y las tablas (clasificaciones, horizontes, tipos de nota). El libro completo sale únicamente con `tuku context style`, para no pagar unas 100 líneas en cada llamada rutinaria.
- **`tuku regenerate libro`** (tema nuevo) copia `LIBRO-DE-ESTILO.md` y los `reglas/*.tuku.md` desde el template del `tuku` instalado. Nunca toca un `reglas/*.md` sin `.tuku`. Es lo que se corre tras actualizar TUKU desde git. `doctor` avisa si el libro del vault difiere del template.
- **`vocab.ENCABEZADOS`** pasa a mapear cada vocabulario a su archivo y capítulo (`clasificaciones` a `reglas/bitacora.md`, `## Clasificaciones`), y lee la única tabla de ese capítulo. Con la misma pieza `doctor` valida `types`: tipos de TUKU del capítulo del libro más los de `reglas/types.md`. `style lint` y `doctor` revisan esos archivos en vez de las tablas del libro y verifican que ningún capítulo tenga más de una tabla.
- **`tuku context cadence`** (comando nuevo, el Paso 9 del [plan temporal](plan-temporal-ciclos-y-libro.md)) concatena los `CADENCIAS.md` del árbol en cascada. La sección de cadencias del libro lo nombra, así que **el comando va antes que esa sección**: el libro no puede citar un comando que no existe.

#### Pasos

1. **Spec primero, sin código**: [`spec/vault.md`](../spec/vault.md) ("El libro de estilo", el árbol de `reglas/`, la convención `X.tuku.md` contra `X.md`, ocho campos de config en vez de siete) y [`spec/bitacora.md`](../spec/bitacora.md) ("dónde vive cada una").
2. **Los archivos del autor y su lectura**: template, `init`, `vocab`, `style`, `config` (sin `parsear_autor`), `doctor`. Se adaptan `001-02`, `001-07` y los `005-0X` que leen el libro. Sin fallback.
3. **`tuku context style` lee el libro por capítulos** (`--chapter`), con la expansión de transclusiones. Incluye el parser de capítulos con su regla de una tabla. Es el paso con más valor para el agente.
4. **`tuku context cadence`.**
5. **El libro nuevo**, escrito por entidad, y **`tuku regenerate libro`** con su aviso en `doctor`. Se actualiza el `AGENTS.md` del template para que el agente corra `tuku context style` (es producto, se edita sin pedir permiso).
6. **Fusionar los tests** que queden redundantes con la medición de arcos, como en la fase 3.

Cada paso deja la suite en verde y se verifica con los escenarios no agénticos.

### Riesgos

- **Más archivos que abrir.** Un humano en un editor simple ve enlaces en vez de tablas; lo cubre `context style`. Los archivos son cortos.
- **`vocab.py`, `style.py`, `context.py`, `todo.py` y `doctor.py` cambian de fuente.** Es el tramo más grande de código, y lo arbitran los escenarios.
- **Quien edite el libro a mano pierde el cambio** al correr `regenerate libro`. Lo avisa `doctor` antes.
- **La transclusión es de Obsidian.** Cualquier otro lector necesita `context style`. Es una dependencia aceptada.

## Decisiones que necesito

1. **¿Se aplica `TZ` ya?** Hecho el 2026-10-19.
2. **¿Idioma de los encabezados de día y mes y de `CABECERA`?** Contrato fijo en castellano; un vault en inglés sería una variante de template. Sin cambio.
3. **¿Entran las tres filas de ventana** (`context_entry_days`, `context_scope_days`, `scope_activity_months`)? Recomiendo que sí.
4. **¿Se parte el libro como arriba?** Es la propuesta de esta sección.
5. **Tres decisiones de forma**, con lo que tomaría si no se opone:
   1. Archivos por entidad (`X.tuku.md` contra `X.md`) en vez de uno por vocabulario como dice la spec hoy.
   2. Los tipos OKF de TUKU en el libro y los del autor en `reglas/types.md`.
   3. `lenguaje.md` aparte de `autor.md`: quién es no es lo mismo que cómo se le habla.
