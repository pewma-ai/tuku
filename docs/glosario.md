# TUKU: glosario

> Vocabulario de TUKU, una línea por término. Sirve para orientarse, no para decidir: la definición completa de cada cosa vive en [`../spec/`](../spec/README.md), y el porqué en [`principios.md`](principios.md).

## Lo básico

| Término | Qué es |
|---|---|
| **Vault** | El repositorio completo del autor: bitácoras, pendientes, notas, ámbitos y sus reglas. Es todo el directorio, no un archivo. |
| **TUKU** | El software que mantiene ese vault: las reglas, los comandos y el agente. No es el vault. |
| **MaC** | *Management as Code*, la metodología de PEWMA.AI de la que TUKU es la variante personal. |
| **Estado cero** | El vault recién instalado, antes de la primera palabra: infraestructura vacía y un ciclo semanal abierto. |
| **Primitiva** | Cada uno de los tipos de cosa que el sistema guarda: bitácora, pendientes, notas, ámbitos, cadencias, ciclos. |

## Los archivos

| Archivo o carpeta | Qué guarda |
|---|---|
| `AHORA.md` | El ciclo en curso: los registros del día, más plan y pendientes por transclusión. |
| `bitacoras/` | Los ciclos ya cerrados, inmutables y autocontenidos. |
| `PENDIENTES.md` | Todos los compromisos abiertos. Fuente de verdad, nunca derivado. |
| `ambitos/` | El árbol de frentes de actividad de la vida del autor. |
| `notas/` | El zettelkasten: notas libres y notas tipadas. |
| `reglas/` | La especificación en prosa de cada consecuencia y de cada comando. |
| `planes/` | Un plan por ciclo, escrito antes de empezarlo. |
| `reportes/` | Lo generado que el autor lee: resúmenes de ciclo, cadencias, pendientes por actividad. |
| `archivado/` | Ramas cerradas, con sus enlaces todavía resolviendo. |
| `AGENTS.md` | Reglas que aplican a un directorio y a todo lo que cuelga de él. Uno por carpeta. |
| `CADENCIAS.md` | Las cadencias de un directorio. Uno por carpeta. |
| `CAPACIDAD.md` | Lo que cuesta sostener un ámbito. Opcional y deseable: solo donde hay algo que declarar. El bruto, si se declara, va en `ambitos/personal/`. |
| `LIBRO-DE-ESTILO.md` | Un archivo único con las reglas de escritura y organización del autor, en prosa. De aquí nacen los comandos. No confundir con el vault, que es el repositorio entero. |

**MAYÚSCULAS es de TUKU, minúsculas es del autor.** Se distingue de un vistazo sin abrir nada.

## Lo que se escribe

| Término | Qué es |
|---|---|
| **Registro** | Una línea de bitácora: un hecho, con hora, ámbito y clasificación. La única forma de registrar algo. |
| **Hecho** | La unidad del registro. Una sola frase dictada puede contener varios y produce varios registros. |
| **Ontología cerrada** | Las tres marcas de TUKU que disparan consecuencias deterministas: `**pendiente**`, `~~(Hecho)~~`, `**cadencia**`. El autor no las puede extender. |
| **Ontología abierta** | Las clasificaciones del autor (`**progreso**`, `**decisión**`, `**fricción**`, `**señal**`, `**nota**`). Sirven para leer y filtrar, ningún comando actúa sobre ellas. Crece con el uso. |
| **Clasificación** | El tipo abierto de un registro, elegido del vocabulario del libro de estilo. |
| **Consecuencia** | Lo que se aplica *después* de escribir el registro, releyendo el texto: abrir un pendiente, enlazar, dar de alta una cadencia, proponer. |
| **Propuesta** | Lo que el sistema sugiere y no ejecuta. Espera aprobación del autor y, si se rechaza, no deja rastro. |

## Pendientes y tiempo

| Término | Qué es |
|---|---|
| **Pendiente** | Un compromiso abierto. Nace de un registro `**pendiente**` y muere en un registro `~~(Hecho)~~`. |
| **Horizonte** | El plazo al que está asignado un pendiente: sin fecha, este turno, próximo turno, fin de mes. |
| **Escalera de horizontes** | El recorrido de un pendiente al concretarse: sin fecha, horizonte, fecha exacta, cerrado. |
| **Atrasado** | Un pendiente cuya fecha ya pasó. Se mueve solo a la tabla de `atrasados`, conservando su fecha. |
| **Callout** | El bloque `> [!TODO]` que agrupa los pendientes de un horizonte o de una fecha en `PENDIENTES.md`. |
| **Horizonte** | Cada encabezado de `PENDIENTES.md` con su tabla debajo: `atrasados`, `sin fecha`, los tres del autor, y `con fecha`. Un pendiente está bajo exactamente uno. |
| **Transclusión** | Mostrar un texto en otro archivo sin copiarlo, con `![[archivo#seccion]]`. Se usa cuando el origen ya agrupa contiguo lo que el destino muestra. |
| **Propagación** | Escribir una copia derivada donde hace falta, cuando el origen no agrupa contiguo lo que el destino muestra. Un comando la produce y la regenera; si discrepa de la fuente, la que está mal es la copia. |
| **Ciclo** | La ventana de tiempo que se abre, se planifica y se cierra. Semanal por defecto, o el turno real del autor. |
| **Cadencia** | Una regla que emite un pendiente con fecha cada cierto tiempo. Vive en el `CADENCIAS.md` del ámbito al que pertenece. |
| **Bruto** | Lo que rinde un día del autor antes de restar nada. Se declara una sola vez, en `ambitos/personal/CAPACIDAD.md`. |
| **Costo fijo** | Lo que un ámbito consume del ciclo antes de que se planifique nada: un turno, un traslado, un rol operativo. Se resta del bruto, y varios se acumulan. |
| **Capacidad** | Lo que queda del bruto después de restar los costos fijos. Es contra eso que se planifica, no contra el ciclo entero. |
| **Vocabulario de magnitud** | Las cuatro etiquetas cerradas con que se declara cuánto consume un bruto o un costo fijo: `el día entero`, `casi todo el día`, `media jornada`, `un rato`. Nunca horas: pedir un número es la fricción que este vocabulario evita. |

## El árbol de ámbitos

| Término | Qué es |
|---|---|
| **Ámbito** | Un frente de actividad con identidad propia. Es un directorio **con** página propia. |
| **Categoría** | Un agrupador sin identidad propia. Es un directorio **sin** página propia, y ningún registro apunta a él. |
| **Actividad** | La hoja donde ocurren las cosas. Es un archivo `.md` en minúsculas. |
| **Regla más cercana** | Ante dos reglas aplicables gana la del directorio más profundo, la que está más cerca del hecho. |
| **Archivar** | Cerrar una rama del árbol. Es caro, porque hay que resolver pendientes, cadencias y enlaces viejos, así que el sistema propone y nunca lo hace solo. |

## Notas

| Término | Qué es |
|---|---|
| **Nota libre** | Zettelkasten puro: una idea que vale mientras conserve sentido, sin pertenecer a un momento. |
| **Nota tipada** | Una nota sobre algo recurrente que declara `subtype` en su frontmatter y por eso tiene plantilla y procedimiento. |
| **Destilar** | Barrer el histórico en contexto aislado para escribir una nota tipada a partir de lo ya registrado. |

## Quién ejecuta

| Término | Qué es |
|---|---|
| **`tuku`** | El comando, y la capa determinista del sistema. Es dueño de la forma (dónde va cada cosa, con qué estructura, en qué orden), nunca del juicio. Nada automático toca el vault fuera de una invocación suya. |
| **Comando** | Cada operación determinista de `tuku`, nombrada `tuku <noun> <verb>`. Se especifica en prosa en `reglas/` y su código vive fuera del vault, en el paquete que instala `pipx`. |
| **"A mano"** | El campo que declara cómo hacer a mano lo que hace un comando. Un comando sin ese campo es una dependencia disfrazada. |
| **Agente** | El LLM que conversa con el autor, interpreta el dictado y propone. Secretario, nunca dueño. |
| **Conjunto canónico** | Lo que el autor escribió y nunca se regenera: `AHORA.md`, `bitacoras/`, `PENDIENTES.md`, `ambitos/`, `notas/`. |
| **Derivado** | Todo lo demás: se puede borrar y regenerar desde el conjunto canónico sin perder nada. |
| **Idempotencia** | Correr una operación dos veces da el mismo resultado. Sin eso, ninguna operación de comando es válida. |
