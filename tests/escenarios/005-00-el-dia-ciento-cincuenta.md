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

## Lo que el epic encontró en las specs

Cada fila es algo que el diseño dice y no se cumple, o que dos documentos dicen distinto. Los marcados **falla** tienen un test rojo que lo prueba; el resto queda para decidir.

| # | Hallazgo | Dónde | Test |
| --- | --- | --- | --- |
| 1 | La lista de hijos de un ámbito sale en orden de creación con `scope create` y `scope move`, y alfabético con `tuku regenerate`. Dos caminos, dos resultados: se rompe el principio 9 | `scope.py` contra `spec/ambitos.md` | **falla** `005-01`, `005-02`, `005-03` |
| 2 | `tuku note lint` sin archivo sale con error en un vault recién sembrado: revisa `notas/AGENTS.md`, que es del sistema y no una nota | `note.py` | **falla** `005-05` |
| 3 | `note lint` no mira los enlaces del cuerpo: la spec pide que la nota cierre con la lista de sus enlaces salientes, cada uno con motivo, y un enlace del cuerpo ausente de esa lista pasa | `spec/notas.md` | **falla** `005-05` |
| 4 | Ningún comando informa los atrasados. `spec/pendientes.md` dice «un comando lo informa» sin nombrarlo, y `todo lint` y `doctor` no saben de fechas | `spec/pendientes.md` | **falla** `005-04` |
| 5 | No existe una nota tipada: `note create` no tiene `--subtype`, y `reglas/tipos/persona.md` que `spec/notas.md` promete («lo crea el epic que escriba la primera nota tipada») no se siembra | `spec/notas.md`, `note.py` | **falla** `005-05` |
| 6 | Ante «le mandé el catálogo a la Paula», con dos candidatas, el agente eligió una sin preguntar | `AGENTS.md` del template | **falla** `005-06` |
| 7 | `spec/pendientes.md` nombra «postergaciones» como comandos de `tuku todo` y `todo` solo tiene `open`, `close` y `lint`: la escalera de horizontes no se puede bajar con un comando | `spec/pendientes.md` | sin test: el nombre del comando no está en la spec |
| 8 | La página de un ámbito muestra solo el ciclo abierto: al archivar la primera semana, el hilo de la cotización de Los Robles desaparece de la página. `## Esta semana` y `## Actividad reciente` ni siquiera están en una spec | `scope.py`, `spec/ambitos.md` | se mira a mano |
| 9 | Un ámbito padre lista a sus hijos directos y los clientes de `negocio` cuelgan de la categoría `clientes`: ninguna página dice dónde están | `spec/ambitos.md` | se mira a mano |
| 10 | [`devel/epics.md`](../../devel/epics.md) describe el epic con «enlaces automáticos desde el primer día» y asignación de ámbito «sin intervención». [`spec/ambitos.md`](../../spec/ambitos.md), «Nada se enlaza solo», dice que el cuerpo nunca se modifica ni se enlaza, y la asignación de ámbito la hace quien interpreta, leyendo las keywords | `devel/epics.md` | el `005-06` prueba la versión de la spec |
| 11 | El epic dice «resto de la fase 4» (cadencias) y «destilados». La tabla de fases pone las cadencias en el 006, y `spec/notas.md` deja el destilado fuera, para la fase 9 | `devel/epics.md` | ninguno: nada de eso es determinista hoy |
| 12 | El corpus de la Pyme contradice a la spec en cuatro puntos: `AGENTS.md` y `CADENCIAS.md` «obligatorios en cada directorio» (la spec: ausente es vacío), registros sobre categorías y personas, 17 de 29 `(Hecho)` sin pendiente abierto, y un horizonte `sin fecha` que la spec descarta | `corpus/referencia/referencia-pyme.md` | `005-01` documenta cómo se lee |
| 13 | El capítulo 4 del tutorial dice que ante dos Paulas el agente pregunta, y [`flujo-informacion.md`](../../spec/flujo-informacion.md) dice que la ambigüedad se deja escrita sin interrumpir al autor | `docs/tutorial/04-...`, `spec/flujo-informacion.md` | `005-06` acepta las dos y rechaza adivinar |

## Decisiones tomadas al escribir los escenarios

- **`todo lint` informa los atrasados como aviso, con código 0.** Es la forma que menos inventa: un comando que ya existe, y el patrón de `entry lint`, que informa preguntas sin fallar. Si el autor prefiere un comando propio, se cambia en `005-04` y en `spec/pendientes.md`.
- **`note create --subtype persona`** para la nota tipada, con el campo que `spec/notas.md` ya llama `subtype`.
- **El cierre de la primera semana reescribe los links con `../`.** Un link es una ruta relativa al archivo que lo contiene, y `bitacoras/` está un nivel más adentro: `spec/ambitos.md` dice que archivar recalcula la ruta de cada link, y el escenario lo hace con `sed` como lo haría Andrea.

## Escenario: preparar el ambiente del epic

Dado el directorio de corridas
Cuando se borran las corridas anteriores del epic
```bash
rm -rf 005-*
```
Entonces el epic parte de cero

## Criterio de salida

Las dos semanas del corpus sobre un vault que ya tiene historia dejan el vault sano, regenerable byte a byte, reorganizable sin romper un link, con los atrasados informados por un comando y con una nota tipada. El agente elige el ámbito por las palabras que lo delatan y, cuando dos candidatos calzan, no adivina.
