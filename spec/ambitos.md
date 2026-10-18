# spec · ámbitos

> El árbol donde aterriza cada registro. Se justifica por el principio 7 de [`../docs/principios.md`](../docs/principios.md) (la regla más cercana prevalece).

## Tres roles, no tres niveles

El árbol crece orgánicamente y la profundidad no está fijada. Lo que distingue a cada nodo es qué carga, no dónde está:

| Rol | Qué es | Cómo se reconoce |
| --- | --- | --- |
| **Ámbito** | Frente de actividad con naturaleza propia | Directorio **con página propia** |
| **Categoría** | Agrupador, sin identidad propia | Directorio **sin página propia** |
| **Actividad** | La hoja, lo que efectivamente ocurre | Archivo `.md` en minúscula |

Regla operativa y verificable por comando: **los registros apuntan a una actividad o a un ámbito, nunca a una categoría.** Una categoría no tiene de qué hablar, solo agrupa.

## Qué carga cada directorio

Un directorio de `ambitos/` puede llevar tres archivos, y los tres son opcionales:

```text
ambitos/
├── AGENTS.md
├── CADENCIAS.md
└── trabajo/
    ├── trabajo.md            <- página propia: esto lo hace ámbito
    ├── AGENTS.md             <- solo si tiene reglas propias
    └── clientes/             <- sin página: es categoría
        └── juanito_perez.md  <- actividad
```

**Ausente significa vacío.** Un ámbito nuevo lleva solo su página: `AGENTS.md`, `CADENCIAS.md` y `CAPACIDAD.md` existen desde que el autor les pone su primera regla, cadencia o costo. El costo de no sembrarlos es una búsqueda hacia arriba: quien necesita las reglas de un ámbito sube por el árbol y toma lo que encuentra, y un archivo que falta no aporta nada y no es un error. Se evita así una pareja de archivos vacíos por cada carpeta, que además hay que mover y renombrar con ella.

**`AGENTS.md` prevalece, `CADENCIAS.md` se acumula.** Una regla escrita más adentro afina la de arriba sin repetirla, que es el principio 7. Una cadencia no afina nada: es algo que vuelve, y que `trabajo/turnos/` declare la suya no cancela la de `trabajo/`. Estar más adentro acota a quién le toca, no a qué se hereda.

## `CAPACIDAD.md`, el costo de un ámbito

Un ámbito puede declarar lo que cuesta sostenerlo, en un `CAPACIDAD.md` propio. Es lo que permite dimensionar el trabajo del ciclo antes de planificarlo, y su formato y uso están en [`ciclo.md`](ciclo.md).

**Es opcional en todas partes, incluida `ambitos/personal/`.** Deseable donde ayude, como muchas cadencias: TUKU se opera sin ninguno de los dos. El estado cero siembra uno en `ambitos/personal/`, sin datos: dice que todavía no se declaró nada y por qué conviene. Sin `CAPACIDAD.md` el plan se propone igual, solo que sin contraste de cuánto cabe, y el autor hace ese contraste en su cabeza como lo hacía antes. Degrada, no rompe. Es la misma relación que con las cadencias: sin ellas el sistema registra, con ellas además anticipa.

Cómo se comparan los tres archivos por directorio:

| | `AGENTS.md` | `CADENCIAS.md` | `CAPACIDAD.md` |
| --- | --- | --- | --- |
| Presencia | Solo donde hay una regla | Solo donde hay una cadencia | Solo donde hay algo que declarar |
| Combinación | La más cercana prevalece | Se acumulan | Se acumulan: el bruto menos la suma de los costos |

**Se acumula en vez de prevalecer** porque no es una regla, es una cantidad. Que `trabajo/` declare un costo no anula el que declaró `trabajo/turnos/`: los dos consumen del mismo día. Lo mismo vale para las cadencias por el mismo motivo, y por eso **solo `AGENTS.md` prevalece**: es el único de los tres que es una regla.

**Si se declara un bruto, va en `ambitos/personal/`**, porque el bruto es uno solo: el tiempo de la persona no se reparte por ámbito, se gasta en ellos. Un ámbito sin `CAPACIDAD.md` no cobra costo fijo, que es el caso por defecto. Y sin bruto declarado en ninguna parte, no hay dimensionamiento: los costos fijos quedan como advertencias sueltas en el plan, sin nada de qué restarse.

Se descartó la alternativa de que cada ámbito declare cuánto tiempo se le asigna y el total sea la suma: es más simétrica, pero obliga al autor a repartir por adelantado, antes de saber en qué se le va el ciclo, y deja con cero a un ámbito que no declaró nada. Cómo se suman las magnitudes sigue abierto ([README.md](README.md), "Decisiones abiertas").

## Transclusión de pendientes

Toda página de ámbito debe transcluir sus pendientes desde `PENDIENTES-AMBITOS.md` usando ruta relativa y ancla de bloque:

```markdown
![[../PENDIENTES-AMBITOS.md#^personal]]
```

Los nombres de ámbito van en minúsculas, en kebab-case (ver «El nombre de un ámbito»): `Depto Centro` es `depto-centro`. Así dos carpetas no pueden diferir solo en mayúsculas, que el disco de macOS y Windows no distingue, y un nombre mal escrito en mayúsculas encuentra el ámbito existente. `tuku scope create` siembra automáticamente esta transclusión al crear un nuevo ámbito, asegura su callout en `PENDIENTES-AMBITOS.md` y estampa una constancia cronológica en `AHORA.md`, con `--at` o, si falta, HOY y AHORA en `TZ`:

```text
- 18:45 - [depto-centro](ambitos/depto-centro/depto-centro.md) **nota**: abrí el ámbito
```

Con `--parent`, la constancia dice dónde quedó: `**nota**: abrí el ámbito bajo [negocio](ambitos/negocio/negocio.md)`, con el padre enlazado si es un ámbito y por su nombre (`bajo clientes`) si es una categoría.

La constancia la deja solo quien crea la carpeta. Un día fuera del ciclo abierto se rechaza antes de crear nada, igual que en `tuku note create`.

### Idempotencia y reparación con el comando original

`tuku scope create` es estrictamente idempotente: ejecutarlo sobre un ámbito ya existente no sobreescribe sus reglas ni duplica callouts en `PENDIENTES-AMBITOS.md`, y no escribe otra constancia en `AHORA.md`, ni en este ciclo ni en uno posterior. Con `--keyword` suma esas keywords, como `scope keywords`.

El comando `tuku scope lint` (y `tuku doctor`) verifica estructuralmente:
1. Que ningún registro en `AHORA.md` apunte a una categoría.
2. Que toda página de ámbito del árbol contenga la transclusión a su bloque en `PENDIENTES-AMBITOS.md`.
3. Que en `ambitos/PENDIENTES-AMBITOS.md` exista el callout con su ancla `^<ambito>` correspondiente a cada ámbito del árbol.

Ante cualquier defecto, el linter informa y nunca repara por su cuenta: nombra la discrepancia e indica el comando original correspondiente para reparar la consistencia.

## Las keywords de un ámbito

La línea `keywords: [vlti, LCU]` del frontmatter de la página lista las palabras con que el autor se refiere al ámbito sin decir su nombre. El nombre del ámbito no va en la lista: ya es el de la carpeta. Cuando lo que el autor dice menciona una de ellas, el ámbito es ese. Si `depto-centro` declara `viana`, `claudia` y `arriendo`, «hablé con Claudia por el arriendo» va a `depto-centro` aunque el autor no diga su nombre. Elige quien interpreta, leyendo las páginas, y el body queda como lo dijo el autor: una keyword no lo modifica ni lo enlaza.

- **`tuku scope create NOMBRE`** pide las keywords en su salida cuando el ámbito es nuevo y no recibió ninguna: el agente las pregunta al autor y no las inventa. `--keyword`, repetible o con varias palabras separadas por coma, las pone en el mismo comando.
- **`tuku scope update NOMBRE --keyword PALABRA`** las suma a la lista y no escribe nada más: ni `AHORA.md` ni ningún registro cambian. `--keyword` es repetible y admite varias palabras separadas por coma (`--keyword viana,claudia`). Una palabra va en kebab-case, como el nombre de un ámbito: minúsculas y con guiones en lugar de espacios, así que `Los Robles` se guarda `los-robles`. Lo que ya estaba, sin distinguir mayúsculas, guiones ni espacios, no se repite; si nada es nuevo, no escribe nada. Rechaza un ámbito que no existe y una palabra con corchetes.
- **`tuku scope rename`** no toca las keywords, porque el nombre no está entre ellas.

## El nombre de un ámbito

**Minúsculas y espacios en guion (kebab-case).** El autor dicta "Depto Centro" y el ámbito es `depto-centro`: carpeta, página y enlaces. Todo comando que recibe un ámbito (`scope create`, `scope rename`, `entry create`, `todo open`, `note create`) lo normaliza igual, así que la forma en que se dictó no crea un segundo frente.

**Un ámbito que no existe se rechaza.** `entry create`, `todo open` y `note create` salen con `RECHAZO` sin escribir nada, y el mensaje nombra `tuku scope create <nombre>` como corrección. Crear un ámbito cambia dónde cae todo lo que venga después, y esa decisión es del autor: se le ofrece, no se toma por él. Una categoría sí existe, y apuntarle un registro lo reporta `scope lint`, no lo impide el comando.

## Un ámbito dentro de otro

Un ámbito puede ir dentro de otro: `ambitos/faena/faena-ai/faena-ai.md`.

- **Los nombres son únicos en todo el árbol.** Un registro nombra el ámbito por su nombre, sin ruta (`--scope faena-ai`), y el link a su página lleva la ruta completa. Dos ámbitos no pueden llamarse igual aunque cuelguen de padres distintos.
- **Cada ámbito muestra solo lo suyo.** La página y el callout de un padre llevan sus propios registros y pendientes, no los de sus hijos. Cada ámbito tiene su callout y su ancla en `PENDIENTES-AMBITOS.md`, en el orden del árbol y con el camino hasta él en el título (`Faena / Faena Ai`).
- **`tuku scope create NOMBRE --parent PADRE`** crea el ámbito dentro de la carpeta del padre, que puede ser un ámbito o una categoría y debe existir. Un padre inexistente se rechaza nombrando `tuku scope create PADRE`: abrirlo es decisión del autor. Si el ámbito ya existe en otro lugar, se rechaza y se nombra `scope move`.
- **`tuku scope move NOMBRE [--parent PADRE]`** cambia un ámbito de lugar, o lo lleva a la raíz de `ambitos/` sin `--parent`. Como los links son rutas relativas, recalcula la ruta de cada link que apunta a lo movido, la de los links de sus propios archivos y la transclusión de su página, en todo el vault y también en las bitácoras cerradas: reparar un link que dejaría de resolver no es enriquecer el pasado. Se rechaza antes de escribir si el ámbito o el padre no existen, si el padre cuelga del propio ámbito o si el destino está ocupado. Moverlo donde ya está no escribe nada.
- **`tuku scope rename`** funciona igual sobre un ámbito anidado.
- **El padre lista a sus hijos** en un callout bajo la transclusión de pendientes, y lo derivan los comandos de las carpetas: `scope create`, `scope move` y `scope rename` lo dejan igual que `tuku regenerate scope`, así que un vault armado comando a comando es idéntico al regenerado. Primero salen los ámbitos hijos, uno por línea y en orden alfabético; después las categorías (carpetas sin página, como `clientes/`), cada una como un callout interior plegable con los ámbitos que contiene, separadas por `---` y también en orden alfabético. Una categoría sin ámbitos no sale, y un ámbito sin hijos no lleva callout. No se edita a mano: lo escrito ahí se pierde en el siguiente comando.

```markdown
> [!abstract]+ En **Negocio**:
> - [bodega](bodega/bodega.md)
> - [equipo](equipo/equipo.md)
> ---
> > [!abstract]+ Clientes
> > - [colegio-los-robles](clientes/colegio-los-robles/colegio-los-robles.md)
> > - [jardin-semillita](clientes/jardin-semillita/jardin-semillita.md)
> ---
> > [!abstract]+ Proveedores
> > - [importadora-andina](proveedores/importadora-andina/importadora-andina.md)
```

**La página de un ámbito hijo declara `parent:`** en su frontmatter: la carpeta que lo contiene, desde la raíz del vault (`parent: ambitos/negocio/clientes`). Un ámbito en la raíz de `ambitos/` no lleva la línea. La carpeta manda y `parent` es su reflejo, para que Obsidian y cualquier lector de propiedades vean dónde cuelga el ámbito sin recorrer rutas: `scope create`, `scope move`, `scope rename` y `tuku regenerate scope` lo escriben, y `scope lint` reporta el que no coincide con la carpeta.

Se descartó que `parent:` mande, moviendo un ámbito con solo editar el campo: la carpeta dejaría de decir dónde cae una regla (principio 7) y Obsidian mostraría un árbol distinto del lógico.

## Convención de mayúsculas

Los archivos de TUKU van en MAYÚSCULAS: `AHORA.md`, `PENDIENTES.md`, `AGENTS.md`, `CADENCIAS.md`, `CAPACIDAD.md`. El contenido del autor va en minúsculas: `trabajo.md`, `juanito_perez.md`, las notas.

Se ve de un vistazo qué es del sistema y qué es del autor, sin abrir nada.

## Archivar es caro

Archivar una actividad o un ámbito no es mover archivos, es una operación con cascada. Por eso **el sistema nunca la inicia solo**: propone, y el autor delibera.

Lo que hay que resolver en cada archivado:

- **Pendientes abiertos de esa rama.** Se cierran, se mueven a otro ámbito, o expiran dejando el motivo escrito.
- **Cadencias vigentes.** Dejan de emitir, pero hay que decidir si se archivan con la rama o se reasignan.
- **Enlaces desde bitácoras ya cerradas.** Este es el que pesa para el principio 1: si archivar rompe enlaces de bitácoras de hace dos años, el archivo histórico deja de ser legible. Como los links son rutas relativas al archivo, **el archivado recalcula la ruta de cada link** de lo que mueve a `bitacoras/` (epic 006; no se implementa todavía).

Las dos primeras son decisiones y se resuelven conversando. La tercera es trabajo, y es la que hace cara la operación.

## Cómo se enlaza un ámbito

El enlace a un ámbito es un link Markdown con ruta relativa al archivo que lo contiene ([README.md](README.md), "Decidido (2026-10-16)"). Se escribe `[nombre](ruta/hasta/nombre.md)` con la ruta desde el archivo donde va, por ejemplo `[personal](../personal/personal.md)` desde una página de ámbito hermana.

La transclusión de pendientes `![[../PENDIENTES-AMBITOS.md#^personal]]` es una extensión de Obsidian aceptada: es el único wikilink admitido y se reconoce por el `!` inicial.

**Renombrar un ámbito** actualiza el texto y la ruta de cada link que lo nombra.

## Nada se enlaza solo

Ni crear un ámbito ni sumarle keywords modifica lo que el autor ya escribió. Un registro lleva los links que se le escribieron al registrarlo, y el body queda como lo dijo el autor, con las palabras que usó. Si quiere enlazar una mención hacia atrás, lo hace él, a mano, o lo pide como una operación deliberada.

Lo que sí hace el comando es **reparar** lo que ya estaba enlazado: mover o renombrar un ámbito actualiza el texto y la ruta de cada link que lo nombra, y archivar una rama recalcula la ruta de los links de las bitácoras cerradas, porque lo contrario rompe el principio 1. Reparar un enlace existente no es enriquecer el pasado.

## No entra

- **La deliberación con el autor antes de archivar.** Acá se implementa la mecánica; decidir que una rama se cierra no es código.
- **El vocabulario de ámbitos como se inyecta a un agente** antes de interpretar un dictado. Eso es [`agente.md`](agente.md).
