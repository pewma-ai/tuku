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

Todo directorio desde `ambitos/` hacia abajo, ese incluido, lleva dos archivos obligatorios:

```text
ambitos/
├── AGENTS.md
├── CADENCIAS.md
└── trabajo/
    ├── AGENTS.md
    ├── CADENCIAS.md
    ├── trabajo.md            <- página propia: esto lo hace ámbito
    └── clientes/
        ├── AGENTS.md
        ├── CADENCIAS.md      <- sin página propia: es categoría
        └── juanito_perez.md  <- actividad
```

Obligatorios aunque estén vacíos. El costo son dos archivos por carpeta. La ganancia es que ningún comando tiene que manejar el caso "no existe", y el autor siempre sabe dónde escribir una regla sin preguntar.

**`AGENTS.md` prevalece, `CADENCIAS.md` se acumula.** Una regla escrita más adentro afina la de arriba sin repetirla, que es el principio 7. Una cadencia no afina nada: es algo que vuelve, y que `trabajo/turnos/` declare la suya no cancela la de `trabajo/`. Estar más adentro acota a quién le toca, no a qué se hereda.

## `CAPACIDAD.md`, el tercero y el opcional

Un ámbito puede declarar lo que cuesta sostenerlo, en un `CAPACIDAD.md` propio. Es lo que permite dimensionar el trabajo del ciclo antes de planificarlo, y su formato y uso están en [`ciclo.md`](ciclo.md).

**Es opcional en todas partes, incluida `ambitos/personal/`.** Deseable donde ayude, como muchas cadencias: TUKU se opera sin ninguno de los dos. El estado cero siembra uno en `ambitos/personal/`, sin datos: dice que todavía no se declaró nada y por qué conviene, igual que hace con `CADENCIAS.md` de esa rama. Sin `CAPACIDAD.md` el plan se propone igual, solo que sin contraste de cuánto cabe, y el autor hace ese contraste en su cabeza como lo hacía antes. Degrada, no rompe. Es la misma relación que con las cadencias: sin ellas el sistema registra, con ellas además anticipa.

Cómo se comparan los tres archivos por directorio:

| | `AGENTS.md` | `CADENCIAS.md` | `CAPACIDAD.md` |
| --- | --- | --- | --- |
| Presencia | Obligatorio en cada directorio, aunque vacío | Obligatorio en cada directorio, aunque vacío | Solo donde hay algo que declarar |
| Combinación | La más cercana prevalece | Se acumulan | Se acumulan: el bruto menos la suma de los costos |

**Se acumula en vez de prevalecer** porque no es una regla, es una cantidad. Que `trabajo/` declare un costo no anula el que declaró `trabajo/turnos/`: los dos consumen del mismo día. Lo mismo vale para las cadencias por el mismo motivo, y por eso **solo `AGENTS.md` prevalece**: es el único de los tres que es una regla.

**Si se declara un bruto, va en `ambitos/personal/`**, porque el bruto es uno solo: el tiempo de la persona no se reparte por ámbito, se gasta en ellos. Un ámbito sin `CAPACIDAD.md` no cobra costo fijo, que es el caso por defecto. Y sin bruto declarado en ninguna parte, no hay dimensionamiento: los costos fijos quedan como advertencias sueltas en el plan, sin nada de qué restarse.

Se descartó la alternativa de que cada ámbito declare cuánto tiempo se le asigna y el total sea la suma: es más simétrica, pero obliga al autor a repartir por adelantado, antes de saber en qué se le va el ciclo, y deja con cero a un ámbito que no declaró nada. Cómo se suman las magnitudes sigue abierto ([README.md](README.md), "Decisiones abiertas").

## Transclusión de pendientes

Toda página de ámbito debe transcluir sus pendientes desde `PENDIENTES-AMBITOS.md` usando ruta relativa y ancla de bloque:

```markdown
![[../PENDIENTES-AMBITOS.md#^personal]]
```

`tuku scope create` siembra automáticamente esta transclusión al crear un nuevo ámbito, asegura su callout en `PENDIENTES-AMBITOS.md` y estampa una constancia cronológica en `AHORA.md`, con `--day` y `--hour` o, si faltan, HOY y AHORA en `TZ`:

```text
- 18:45 - [depto-centro](ambitos/depto-centro/depto-centro.md) **nota**: abrí el ámbito
```

La constancia la deja solo quien crea la carpeta. Un día fuera del ciclo abierto se rechaza antes de crear nada, igual que en `tuku note create`.

### Idempotencia y reparación con el comando original

`tuku scope create` es estrictamente idempotente: ejecutarlo sobre un ámbito ya existente no sobreescribe sus reglas ni duplica callouts en `PENDIENTES-AMBITOS.md`, y no escribe otra constancia en `AHORA.md`, ni en este ciclo ni en uno posterior.

El comando `tuku scope lint` (y `tuku doctor`) verifica estructuralmente:
1. Que ningún registro en `AHORA.md` apunte a una categoría.
2. Que toda página de ámbito del árbol contenga la transclusión a su bloque en `PENDIENTES-AMBITOS.md`.
3. Que en `ambitos/PENDIENTES-AMBITOS.md` exista el callout con su ancla `^<ambito>` correspondiente a cada ámbito del árbol.

Ante cualquier defecto, el linter informa y nunca repara por su cuenta: nombra la discrepancia e indica el comando original correspondiente para reparar la consistencia.

## El nombre de un ámbito

**Los espacios pasan a guion.** El autor dicta "depto centro" y el ámbito es `depto-centro`: carpeta, página y enlaces. Todo comando que recibe un ámbito (`scope create`, `scope rename`, `entry add`, `todo open`, `note create`) lo normaliza igual, así que la forma en que se dictó no crea un segundo frente.

**Un ámbito que no existe se rechaza.** `entry add`, `todo open` y `note create` salen con `RECHAZO` sin escribir nada, y el mensaje nombra `tuku scope create <nombre>` como corrección. Crear un ámbito cambia dónde cae todo lo que venga después, y esa decisión es del autor: se le ofrece, no se toma por él. Una categoría sí existe, y apuntarle un registro lo reporta `scope lint`, no lo impide el comando.

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

## El enlazado retroactivo llega hasta el ciclo en curso

Crear un ámbito convierte en enlaces las menciones sueltas que ya estaban escritas. Ese barrido alcanza **`AHORA.md` y nada más**: los ciclos cerrados de `bitacoras/` son inmutables y no se reescriben para agregarles enlaces que no tenían.

La distinción es entre reparar y agregar. Al archivar una rama, un enlace que ya existía y dejaría de resolver sí se repara en una bitácora cerrada, porque lo contrario rompe el principio 1. Lo que nunca ocurre solo es enriquecer el pasado: si el autor quiere que un ámbito nuevo enlace hacia atrás en la historia, lo pide explícitamente y es una operación deliberada, como archivar.

## No entra

- **La deliberación con el autor antes de archivar.** Acá se implementa la mecánica; decidir que una rama se cierra no es código.
- **El vocabulario de ámbitos como se inyecta a un agente** antes de interpretar un dictado. Eso es [`agente.md`](agente.md).
