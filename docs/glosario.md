# TUKU: glosario

> Vocabulario de TUKU, una línea por término. Sirve para orientarse, no para decidir: la definición completa de cada cosa vive en [`../spec/`](../spec/README.md), y el porqué en [`principios.md`](principios.md).

## Lo básico

| Término | Qué es |
|---|---|
| **Vault** | El repositorio completo del autor: bitácoras, pendientes, notas, ámbitos y sus reglas. Es todo el directorio, no un archivo. |
| **TUKU** | El software que mantiene ese vault: las reglas, los janitors y el agente. No es el vault. |
| **MaC** | *Management as Code*, la metodología de PEWMA.AI de la que TUKU es la variante personal. |
| **Estado cero** | El vault recién instalado, antes de la primera palabra: infraestructura vacía y un ciclo semanal abierto. |
| **Primitiva** | Cada uno de los tipos de cosa que el sistema guarda: bitácora, pendientes, notas, ámbitos, cadencias, ciclos. |

## Los archivos

| Archivo o carpeta | Qué guarda |
|---|---|
| `AHORA.md` | El ciclo en curso: las entradas del día, más plan y pendientes por transclusión. |
| `bitacoras/` | Los ciclos ya cerrados, inmutables y autocontenidos. |
| `PENDIENTES.md` | Todos los compromisos abiertos. Fuente de verdad, nunca derivado. |
| `ambitos/` | El árbol de frentes de actividad de la vida del autor. |
| `notas/` | El zettelkasten: notas libres y notas tipadas. |
| `reglas/` | La especificación en prosa de cada consecuencia y de cada janitor. |
| `planes/` | Un plan por ciclo, escrito antes de empezarlo. |
| `reportes/` | Lo generado que el autor lee: resúmenes de ciclo, cadencias, pendientes por actividad. |
| `archivado/` | Ramas cerradas, con sus enlaces todavía resolviendo. |
| `AGENTS.md` | Reglas que aplican a un directorio y a todo lo que cuelga de él. Uno por carpeta. |
| `CADENCIAS.md` | Las cadencias de un directorio. Uno por carpeta. |
| `LIBRO-DE-ESTILO.md` | Un archivo único con las reglas de escritura y organización del autor, en prosa. De aquí nacen los janitors. No confundir con el vault, que es el repositorio entero. |

**MAYÚSCULAS es de TUKU, minúsculas es del autor.** Se distingue de un vistazo sin abrir nada.

## Lo que se escribe

| Término | Qué es |
|---|---|
| **Entrada** | Una línea de bitácora: un hecho, con hora, ámbito y clasificación. La única forma de registrar algo. |
| **Hecho** | La unidad de la entrada. Una sola frase dictada puede contener varios y produce varias entradas. |
| **Ontología cerrada** | Las tres marcas de TUKU que disparan consecuencias deterministas: `**pendiente**`, `~~(Hecho)~~`, `**cadencia**`. El autor no las puede extender. |
| **Ontología abierta** | Las clasificaciones del autor (`**progreso**`, `**decisión**`, `**fricción**`, `**señal**`, `**nota**`). Sirven para leer y filtrar, ningún janitor actúa sobre ellas. Crece con el uso. |
| **Clasificación** | El tipo abierto de una entrada, elegido del vocabulario del libro de estilo. |
| **Consecuencia** | Lo que se aplica *después* de escribir la entrada, releyendo el texto: abrir un pendiente, enlazar, dar de alta una cadencia, proponer. |
| **Propuesta** | Lo que el sistema sugiere y no ejecuta. Espera aprobación del autor y, si se rechaza, no deja rastro. |

## Pendientes y tiempo

| Término | Qué es |
|---|---|
| **Pendiente** | Un compromiso abierto. Nace de una entrada `**pendiente**` y muere en una entrada `~~(Hecho)~~`. |
| **Horizonte** | El plazo al que está asignado un pendiente: sin fecha, este turno, próximo turno, fin de mes. |
| **Escalera de horizontes** | El recorrido de un pendiente al concretarse: sin fecha, horizonte, fecha exacta, cerrado. |
| **Atrasado** | Un pendiente cuya fecha ya pasó. Se mueve solo a `^atrasados` con su vencimiento estampado. |
| **Callout** | El bloque `> [!TODO]` que agrupa los pendientes de un horizonte o de una fecha en `PENDIENTES.md`. |
| **Ancla** | El identificador de un callout (`^sin-fecha`, `^2026-04-02`), que es lo que permite transcluirlo. |
| **Transclusión** | Mostrar un texto en otro archivo sin copiarlo, con `![[archivo#^ancla]]`. Al cerrar el ciclo se aplana a texto. |
| **Ciclo** | La ventana de tiempo que se abre, se planifica y se cierra. Semanal por defecto, o el turno real del autor. |
| **Cadencia** | Una regla que emite un pendiente con fecha cada cierto tiempo. Vive en el `CADENCIAS.md` del ámbito al que pertenece. |
| **Capacidad** | Las horas reales que quedan en un ciclo, después de restar el costo fijo. Es contra eso que se planifica. |

## El árbol de ámbitos

| Término | Qué es |
|---|---|
| **Ámbito** | Un frente de actividad con identidad propia. Es un directorio **con** página propia. |
| **Categoría** | Un agrupador sin identidad propia. Es un directorio **sin** página propia, y ninguna entrada apunta a él. |
| **Actividad** | La hoja donde ocurren las cosas. Es un archivo `.md` en minúsculas. |
| **Regla más cercana** | Ante dos reglas aplicables gana la del directorio más profundo, la que está más cerca del hecho. |
| **Archivar** | Cerrar una rama del árbol. Es caro, porque hay que resolver pendientes, cadencias y enlaces viejos, así que el sistema propone y nunca lo hace solo. |

## Notas

| Término | Qué es |
|---|---|
| **Nota libre** | Zettelkasten puro: una idea que vale mientras conserve sentido, sin pertenecer a un momento. |
| **Nota tipada** | Una nota sobre algo recurrente que declara `tipo:` en su frontmatter y por eso tiene plantilla y procedimiento. |
| **Destilar** | Barrer el histórico en contexto aislado para escribir una nota tipada a partir de lo ya registrado. |

## Quién ejecuta

| Término | Qué es |
|---|---|
| **Janitor** | Un proceso determinista que mantiene el vault. Se nombran `jntr.*`, se especifican en `reglas/` y su código vive fuera, en `~/.tuku/janitors`. |
| **"A mano"** | El campo que declara cómo hacer a mano lo que hace un janitor. Un janitor sin ese campo es una dependencia disfrazada. |
| **Agente** | El LLM que conversa con el autor, interpreta el dictado y propone. Secretario, nunca dueño. |
| **Conjunto canónico** | Lo que el autor escribió y nunca se regenera: `AHORA.md`, `bitacoras/`, `PENDIENTES.md`, `ambitos/`, `notas/`. |
| **Derivado** | Todo lo demás: se puede borrar y regenerar desde el conjunto canónico sin perder nada. |
| **Idempotencia** | Correr una operación dos veces da el mismo resultado. Sin eso, ninguna operación de janitor es válida. |
