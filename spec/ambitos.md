# spec · ámbitos

> El árbol donde aterriza cada entrada. Se justifica por el principio 7 de `../docs/principios.md` (la regla más cercana prevalece).

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

## Convención de mayúsculas

Los archivos de TUKU van en MAYÚSCULAS: `AHORA.md`, `PENDIENTES.md`, `AGENTS.md`, `CADENCIAS.md`. El contenido del autor va en minúsculas: `trabajo.md`, `juanito_perez.md`, las notas.

Se ve de un vistazo qué es del sistema y qué es del autor, sin abrir nada.

## Archivar es caro

Archivar una actividad o un ámbito no es mover archivos, es una operación con cascada. Por eso **el sistema nunca la inicia solo**: propone, y el autor delibera.

Lo que hay que resolver en cada archivado:

- **Pendientes abiertos de esa rama.** Se cierran, se mueven a otro ámbito, o expiran dejando el motivo escrito.
- **Cadencias vigentes.** Dejan de emitir, pero hay que decidir si se archivan con la rama o se reasignan.
- **Enlaces desde bitácoras ya cerradas.** Este es el que pesa para el principio 1: si archivar rompe enlaces de bitácoras de hace dos años, el archivo histórico deja de ser legible. O `archivado/` preserva rutas resolubles, o el archivado reescribe los enlaces.

Las dos primeras son decisiones y se resuelven conversando. La tercera es trabajo, y es la que hace cara la operación.

## No entra

- **La deliberación con el autor antes de archivar.** Acá se implementa la mecánica; decidir que una rama se cierra no es código.
- **El vocabulario de ámbitos como se inyecta a un agente** antes de interpretar un dictado. Eso es `agente.md`.
