# spec · vault

> Qué hay en el disco, quién escribe cada cosa y qué declara cada archivo. Las demás specs lo dan por sabido. Se justifica por los principios 1, 5 y 7 de [`../docs/principios.md`](../docs/principios.md).

## Árbol de directorios

```text
AGENTS.md                     # reglas de todo el repo
LIBRO-DE-ESTILO.md            # prosa de TUKU, estática y regenerada. Transcluye los datos del autor de reglas/
AHORA.md                      # ciclo en curso
PENDIENTES.md                 # fuente de verdad
log.md                        # generado, OKF compliant. Todavía no existe
index.md                      # generado, OKF compliant. Todavía no existe
.gitignore                    # de .obsidian/ se versiona solo la semilla

.obsidian/                    # configuración de Obsidian, el editor de referencia
  app.json                    # links Markdown y rutas relativas. Lo siembra el template

bitacoras/                    # ciclos cerrados, inmutables. Aparece al cerrar el primero (epic 006)
  bitacora-2026-08-25-2026-09-01-turno.md

ambitos/                      # el árbol de la vida
  AGENTS.md                   # reglas de toda la rama
  CADENCIAS.md                # cadencias de toda la rama
  PENDIENTES-AMBITOS.md       # generado, un callout por ámbito, se transcluye
  personal/
    CAPACIDAD.md              # el bruto, si se declara. Opcional
    personal.md               # página propia: es ámbito
  trabajo/
    trabajo.md
    CAPACIDAD.md              # costo fijo de este ámbito. Opcional
    AGENTS.md                 # solo si el ámbito tiene reglas propias
    CADENCIAS.md              # solo si tiene cadencias propias
    clientes/                 # sin página: es categoría
      juanito-perez.md        # hoja: recibe registros
    jefatura/                 # un ámbito dentro de otro, con su propia página
      jefatura.md

notas/                        # zettelkasten, formato libre

reglas/                       # por entidad: X.tuku.md es la prosa de TUKU y X.md lo del autor
  bitacora.tuku.md            # cómo se escribe un registro
  bitacora.md                 # del autor: ## Clasificaciones y ## Escritura
  pendientes.tuku.md          # todavía no existe
  pendientes.md               # del autor: ## Horizontes
  notas.tuku.md               # cómo se escribe una nota
  notas.md                    # del autor: ## Tipos de nota
  ciclo.tuku.md               # todavía no existe
  ciclo.md                    # del autor: cómo es su ciclo
  ambitos.md                  # del autor: las convenciones de sus ámbitos
  cadencias.tuku.md           # todavía no existe (epic 006)
  cadencias.md                # del autor: las convenciones de sus cadencias
  autor.md                    # del autor: nombre y rol
  lenguaje.md                 # del autor: idioma, trato, registro y términos propios
  types.md                    # del autor: los `type` que agrega a los de TUKU
  comandos.tuku.md            # qué hace cada comando y cómo a mano. Lo escribe `tuku init`
  config.tuku.md              # TZ, cycle_name, tuku_template, tuku_version, origen, scope_default, date_format, context_note_limit
  plantilla/
    AHORA.md                  # de aquí sale un ciclo nuevo
  enlaces.tuku.md             # todavía no existe
  propuestas.tuku.md          # todavía no existe (epic 007)
  subtipos/                   # una por subtipo de nota, con su plantilla y qué inferir
    persona.tuku.md

procesos/                     # los que el autor invoca por su nombre. Aparece con el primero

planes/                       # un plan por ciclo. Todavía no existe (epic 006)
  plan-2026-08-25-turno.md

reportes/                     # generados, el autor los lee. Todavía no existe (epic 006)
  resumen-2026-08-25-turno.md

archivado/                    # ramas cerradas, enlaces vivos. Todavía no existe (epic 006)
```

**MAYÚSCULAS es de TUKU, minúsculas es del autor.** `AHORA.md`, `PENDIENTES.md`, `AGENTS.md`, `CADENCIAS.md` y `CAPACIDAD.md` son de TUKU; `trabajo.md`, `juanito-perez.md` y las notas, del autor. Se ve de un vistazo, sin abrir nada.

**En `reglas/`, `X.tuku.md` es la prosa de TUKU para la entidad `X` y `X.md` es lo que el autor decide sobre ella.** `bitacora.tuku.md` explica cómo se escribe un registro y `bitacora.md` trae las clasificaciones del autor. Una versión nueva de TUKU reemplaza los `X.tuku.md` y el libro de estilo (`tuku regenerate libro`) y no toca ningún `X.md`.

**Todo nombre de archivo o carpeta que TUKU genera va en kebab-case y en minúsculas**: `depto-centro/depto-centro.md` para un ámbito, `reunion-con-viana.md` para una nota, `bitacora-2026-08-25-2026-09-01-turno.md` para un ciclo archivado. Los espacios pasan a guion, y la misma regla vale para las keywords de un ámbito (`los-robles`). Así dos nombres no difieren solo en mayúsculas, que el disco de macOS y Windows no distingue, y la forma en que el autor dictó el nombre no crea un segundo archivo. La única excepción son los archivos de TUKU en MAYÚSCULAS. El detalle para ámbitos está en [ambitos.md](ambitos.md).

Lo marcado "todavía no existe" es diseño: el árbol lo muestra para que se sepa dónde va, y el vault sembrado hoy trae el resto. Fuera de este árbol no hay nada más en el disco. **Todo lo que existe, el autor lo puede abrir y leer.** No hay carpeta de cache ni archivos de máquina. `.obsidian/` es la excepción acotada: configura el editor y guarda cero contenido: borrarla deja el vault intacto. Por qué se siembra y con qué ajustes está en [markdown.md](markdown.md). Obsidian agrega ahí sus propios archivos al usarse, y `.gitignore` los deja fuera de git.

El contexto reciente y el vocabulario de ámbitos no son archivos: son la **salida de un comando**, que se calcula cuando hace falta y se inyecta. Materializarlos solo agregaría copias que envejecen, porque una cola de bitácora queda vieja apenas se escribe el registro siguiente. Calcularla en el momento es más simple y además más correcto. Los calcula `tuku context` ([cli.md](cli.md)).

Lo que sí se materializa, aunque sea generado, es lo que alguien mira o transcluye: `ambitos/PENDIENTES-AMBITOS.md` lo transcluyen las páginas de ámbito. Las cadencias vigentes no se materializan: las combina un comando que recorre los `CADENCIAS.md` del árbol ([cadencias.md](cadencias.md)), porque cada ámbito nuevo trae las suyas y una lista guardada envejecería.

## El frontmatter

Todo archivo del vault que guarde conocimiento **declara `type`** en un bloque YAML arriba. Es el único campo obligatorio, y es lo que hace que un vault lo entienda algo que nunca oyó hablar de TUKU.

El formato es [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format), el Open Knowledge Format de Google: markdown con frontmatter, un concepto por archivo, sin herramientas obligatorias ni registro central de esquemas. Se adopta porque describe lo que el diseño ya hacía, no porque agregue algo.

**Los nombres de campo van en inglés**, como los comandos `tuku`: son superficie experta, la lee una máquina o alguien que sabe lo que busca. El cuerpo sigue en castellano, que es donde escribe el autor.

**Los `type` de TUKU son contrato y viajan en el libro de estilo** (capítulo «Tipos de archivo», una tabla). Renombrar `Logbook` rompe los comandos y deja el vault ilegible para cualquier herramienta que hable OKF, así que esa tabla es de TUKU y el autor no la edita. Hoy son `Logbook`, `Todo`, `Derived`, `Scope`, `Note`, `Cadence`, `Capacity`, `Config` y `Style Guide`.

**Los que el autor agrega viven en [`reglas/types.md`](../template/vanilla/reglas/types.md)**, otra tabla, y el libro la transcluye debajo de la de TUKU. Agregar un tipo propio es agregar una fila ahí. Un nombre no puede repetir uno de TUKU.

**Los `AGENTS.md` quedan fuera** y no llevan frontmatter: son reglas de operación, no conocimiento.

Un `type` puede pedir campos propios, y los declara la spec de esa primitiva: `Logbook` lleva además `status`, `from` y `to` ([ciclo.md](ciclo.md)).

Que se cumpla lo verifica `tuku doctor`, que lee los tipos válidos de las dos tablas en tiempo de ejecución y recorre el vault entero.

**Se documenta lo que se usa.** OKF permite más campos de los que TUKU escribe hoy; los que no se escriben todavía no se declaran, para que la spec no prometa lo que el vault no trae.

## El libro de estilo

`LIBRO-DE-ESTILO.md` es de TUKU, como dice el nombre en MAYÚSCULAS, y viene del repositorio: explica qué hace `tuku` con cada entidad, igual para todos los vaults. Es estático y lo regenera `tuku regenerate libro`, que lo copia del template del `tuku` instalado junto con los `reglas/*.tuku.md`. **Una versión nueva de TUKU trae un libro nuevo y no toca nada de lo que el autor decidió.** Vive en el vault y no en `~/.tuku`: un vault clonado o abierto en otra máquina se lee solo, y Obsidian no transcluye archivos de fuera.

**Se organiza por entidad.** Un capítulo por cada una: registro, pendiente, ciclo, ámbito, nota, cadencia, tipos de archivo y cómo escribe el autor. Cada capítulo dice en pocas líneas qué hace el comando `tuku` para esa entidad y cuál es (por ejemplo, que las cadencias de la semana son la concatenación de las de cada ámbito, y `tuku context cadence` las recolecta). Al final apunta a `reglas/X.md` y lo transcluye con `![](reglas/X.md)`, que es donde el autor decide lo suyo.

**El libro no lleva vocabulario del autor.** Las clasificaciones, los horizontes y los tipos de nota viven en `reglas/bitacora.md`, `reglas/pendientes.md` y `reglas/notas.md`. Lo que no sea de una entidad va a `reglas/autor.md` (quién es el autor: nombre, rol) o a `reglas/lenguaje.md` (idioma, trato, registro, términos propios). La regla de que el registro va en primera persona, y la de que el pendiente va en infinitivo y su cierre repite el texto, son contrato y se quedan en el libro.

**Cada capítulo es un `##` y lleva como máximo una tabla.** Vale para el libro y para cada archivo de `reglas/`, y es lo que hace que un comando pueda leer un capítulo por su nombre y tomar su única tabla (`## Clasificaciones` en `reglas/bitacora.md`; «Tipos de archivo» en el libro). Los `###` dentro de un capítulo son libres, pero sin tablas propias. La regla es sobre el texto de cada archivo y no sobre el resultado de expandir las transclusiones. `tuku doctor style` la verifica.

**El agente no lee el libro crudo: corre `tuku context style`**, que devuelve los capítulos, de lo general a lo específico, con cada transclusión expandida en su lugar. Con `--chapter NOMBRE` devuelve uno solo. Sin tema, `tuku context` trae de `style` solo `autor`, `lenguaje` y las tablas. De un archivo transcluido entran sus capítulos `##`: lo que haya antes del primero (el título, un aviso) es para quien lo edita y no llega al agente. Uno que falta sale marcado en el texto y `doctor style` lo reporta.

Los comandos leen cada tabla del archivo y el capítulo que le corresponde ([bitacora.md](bitacora.md), "dónde vive cada una"). Por qué el libro se redacta en tercera persona está en la [iteración del 2026-09-06](../devel/iteraciones/2026-09-06.md).

## La configuración

**`reglas/config.tuku.md` es una tabla**, y es lo único que leen las automatizaciones de ese archivo. Ocho campos:

| Campo | Qué dice |
| --- | --- |
| `TZ` | La zona horaria, con su nombre IANA. Decide qué día es HOY y por lo tanto qué está atrasado |
| `cycle_name` | Cómo se llama el ciclo: `semana` si falta, o una lista de nombres que se alternan en orden (`turno, descanso`). Cada ciclo declara cuál es en su frontmatter ([ciclo.md](ciclo.md)). El template siembra `semana`. Es opcional: `doctor config` no lo exige |
| `tuku_template` | La variante de la que salió el vault |
| `tuku_version` | La versión de TUKU con que se sembró. `tuku doctor` la compara con la de `~/.tuku` y avisa si el vault quedó atrás |
| `origen` | La URL del repositorio, para saber dónde revisar cambios |
| `scope_default` | El ámbito de un registro, un pendiente o su cierre cuando el comando no nombra otro (`personal` en el template) |
| `date_format` | Cómo se escribe la fecha corta de un pendiente fuera de `AHORA.md`, con `MMM` (mes abreviado, `Ago`), `MM`, `DD` y `AAAA`. `MMM/DD` por defecto y también si falta |
| `context_note_limit` | Cuántas notas de cada tipo enlazable trae `tuku context note`, las de `updated` más reciente. `25` por defecto y también si falta o no es un entero positivo |

La escribe `tuku init`, que toma la zona horaria de la máquina, y un callout en el archivo lo dice. Cada campo que no es un sello de la instalación (`tuku_template`, `tuku_version`, `origen`) tiene un valor por defecto, escrito una sola vez en el código.

**Cada comando mide HOY en la zona `TZ` del vault**, no en la del sistema. Con una zona vacía o inexistente usa la del sistema; si es inexistente, el comando avisa por stderr y `tuku doctor config` lo reporta como error.

**Ningún dato nuevo destinado a una automatización se agrega al libro de estilo** ([bitacora.md](bitacora.md), "dónde vive cada una"): va a esta tabla, y quien necesite mostrarlo la transcluye en vez de copiarla.

`~/.tuku` no es parte del vault: es un artefacto de la instalación. Trae `template/`, `docs/` y `spec/`, lleva el sello `tuku.version` y se reemplaza entero cuando ese sello no coincide con el `tuku` instalado.

## Dónde viven los comandos

La **especificación** viaja con el vault: `reglas/comandos.tuku.md` dice en prosa qué hace cada comando sobre los archivos del vault, para que alguien pueda operar el vault, o volver a implementar el comando, aunque el código de hoy ya no exista. Lo escribe `tuku init` desde el párrafo de ayuda de cada comando ([cli.md](cli.md)) y lo reescribe `tuku regenerate comandos`, porque es derivado: de la versión de `tuku` instalada, no del conjunto canónico.

El **código** vive fuera del vault, en el paquete `tuku` que instala `uv tool install` o `pipx` (epic 001 de [`../devel/epics.md`](../devel/epics.md)). En el vault no hay código. El `AGENTS.md` de la raíz lo declara, así que quien opere el libro lo encuentra en el primer archivo que abre.

La división es la de siempre: **la especificación sobrevive, la implementación se reemplaza.** Un script de 2026 no va a correr en 2046, pero la descripción de lo que hacía sí se va a leer. Y así el repositorio del autor no se vuelve una copia del código de TUKU que después diverge por su cuenta.

El nombre canónico de cada comando es su invocación, `tuku <noun> <verb>` (o `tuku <noun>` en los que no tienen verbo, como `init` y `doctor`), y ese es el encabezado con que se especifica: `##` para el sustantivo, con qué es, y `###` para cada verbo. Cada uno se especifica igual:

```markdown
### tuku todo close

Escribe en `AHORA.md` el registro `- HH:MM - [ámbito](ruta) (Hecho): ~~cuerpo~~`, borra de `PENDIENTES.md` la fila cuyo detalle coincide palabra por palabra y regenera las vistas. Si ninguna fila coincide, lo reporta y deja solo el registro.
```

Que el párrafo nombre archivos y cómo cambian no es cortesía documental, es lo que sostiene el principio 1: si un comando no se puede ejecutar, el trabajo se hace igual con un editor, solo que cuesta más. Un comando cuya descripción no alcanza para eso es una dependencia disfrazada.

## No entra

- El formato de cada archivo. Lo especifica la spec de su primitiva: [bitacora.md](bitacora.md), [pendientes.md](pendientes.md), [ambitos.md](ambitos.md), [cadencias.md](cadencias.md), [notas.md](notas.md), [ciclo.md](ciclo.md).
- Qué hay en un vault recién sembrado. Eso es [`../template/README.md`](../template/README.md).
