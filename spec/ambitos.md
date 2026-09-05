# spec · ámbitos

> El árbol donde aterriza cada entrada. Se justifica por el principio 7 de [`../docs/principios.md`](../docs/principios.md) (la regla más cercana prevalece).

## Tres roles, no tres niveles

El árbol crece orgánicamente y la profundidad no está fijada. Lo que distingue a cada nodo es qué carga, no dónde está:

| Rol | Qué es | Cómo se reconoce |
| --- | --- | --- |
| **Ámbito** | Frente de actividad con naturaleza propia | Directorio **con página propia** |
| **Categoría** | Agrupador, sin identidad propia | Directorio **sin página propia** |
| **Actividad** | La hoja, lo que efectivamente ocurre | Archivo `.md` en minúscula |

Regla operativa y verificable por janitor: **las entradas apuntan a una actividad o a un ámbito, nunca a una categoría.** Una categoría no tiene de qué hablar, solo agrupa.

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

Obligatorios aunque estén vacíos. El costo son dos archivos por carpeta. La ganancia es que ningún janitor tiene que manejar el caso "no existe", y el autor siempre sabe dónde escribir una regla sin preguntar.

En ambos, **la más cercana prevalece**.

## `CAPACIDAD.md`, el tercero y el opcional

Un ámbito puede declarar lo que cuesta sostenerlo, en un `CAPACIDAD.md` propio. Es lo que permite dimensionar el trabajo del ciclo antes de planificarlo, y su formato y uso están en [`ciclo.md`](ciclo.md).

**Es opcional en todas partes, incluida `ambitos/personal/`.** Deseable donde ayude, como muchas cadencias: TUKU se opera sin ninguno de los dos. El estado cero siembra uno en `ambitos/personal/`, sin datos: dice que todavía no se declaró nada y por qué conviene, igual que hace con `CADENCIAS.md` de esa rama. Sin `CAPACIDAD.md` el plan se propone igual, solo que sin contraste de cuánto cabe, y el autor hace ese contraste en su cabeza como lo hacía antes. Degrada, no rompe. Es la misma relación que con las cadencias: sin ellas el sistema registra, con ellas además anticipa.

Se aparta de los otros dos en dos cosas:

| | `AGENTS.md`, `CADENCIAS.md` | `CAPACIDAD.md` |
| --- | --- | --- |
| Presencia | Obligatorio en cada directorio, aunque vacío | Solo donde hay algo que declarar |
| Combinación | La más cercana prevalece | Se acumulan: el bruto menos la suma de los costos |

**Se acumula en vez de prevalecer** porque no es una regla, es una cantidad. Que `trabajo/` declare un costo no anula el que declaró `trabajo/turnos/`: los dos consumen del mismo día. Es la única pieza del árbol que se lee sumando en lugar de eligiendo la más cercana.

**Si se declara un bruto, va en `ambitos/personal/`**, porque el bruto es uno solo: el tiempo de la persona no se reparte por ámbito, se gasta en ellos. Un ámbito sin `CAPACIDAD.md` no cobra costo fijo, que es el caso por defecto. Y sin bruto declarado en ninguna parte, no hay dimensionamiento: los costos fijos quedan como advertencias sueltas en el plan, sin nada de qué restarse.

> [!question] Propuesta de diseño, no decisión tomada #REVISAR
> El reparto bruto en `personal/` más costos fijos acumulables en el resto es propuesta mía, derivada de lo que ya dice `ciclo.md`. La alternativa sería que cada ámbito declare su capacidad asignada y el total sea la suma, que es más simétrico pero obliga al autor a repartir por adelantado, antes de saber en qué se le va el ciclo.

## Convención de mayúsculas

Los archivos de TUKU van en MAYÚSCULAS: `AHORA.md`, `PENDIENTES.md`, `AGENTS.md`, `CADENCIAS.md`, `CAPACIDAD.md`. El contenido del autor va en minúsculas: `trabajo.md`, `juanito_perez.md`, las notas.

Se ve de un vistazo qué es del sistema y qué es del autor, sin abrir nada.

## Archivar es caro

Archivar una actividad o un ámbito no es mover archivos, es una operación con cascada. Por eso **el sistema nunca la inicia solo**: propone, y el autor delibera.

Lo que hay que resolver en cada archivado:

- **Pendientes abiertos de esa rama.** Se cierran, se mueven a otro ámbito, o expiran dejando el motivo escrito.
- **Cadencias vigentes.** Dejan de emitir, pero hay que decidir si se archivan con la rama o se reasignan.
- **Enlaces desde bitácoras ya cerradas.** Este es el que pesa para el principio 1: si archivar rompe enlaces de bitácoras de hace dos años, el archivo histórico deja de ser legible. O `archivado/` preserva rutas resolubles, o el archivado reescribe los enlaces.

## El enlazado retroactivo llega hasta el ciclo en curso

Crear un ámbito convierte en enlaces las menciones sueltas que ya estaban escritas. Ese barrido alcanza **`AHORA.md` y nada más**: los ciclos cerrados de `bitacoras/` son inmutables y no se reescriben para agregarles enlaces que no tenían.

La distinción es entre reparar y agregar. Al archivar una rama, un enlace que ya existía y dejaría de resolver sí se repara en una bitácora cerrada, porque lo contrario rompe el principio 1. Lo que nunca ocurre solo es enriquecer el pasado: si el autor quiere que un ámbito nuevo enlace hacia atrás en la historia, lo pide explícitamente y es una operación deliberada, como archivar.

Las dos primeras son decisiones y se resuelven conversando. La tercera es trabajo, y es la que hace cara la operación.

## No entra

- **La deliberación con el autor antes de archivar.** Acá se implementa la mecánica; decidir que una rama se cierra no es código.
- **El vocabulario de ámbitos como se inyecta a un agente** antes de interpretar un dictado. Eso es [`agente.md`](agente.md).
