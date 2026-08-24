# ADR 0001 — Identidad estable independiente del path

## Contexto

En un sistema de archivos Markdown, la forma obvia de identificar una cosa es su ruta:
`entidades/trabajo/sw-responsible.md` **es** la entidad `sw-responsible`. Las referencias se
escriben como enlaces relativos, Obsidian navega solo, y no hace falta inventar nada.

Esa obviedad no sobrevive al uso real:

- **La jerarquía se reorganiza.** Una entidad que colgaba del ámbito se agrupa después en un
  subdirectorio; un proyecto cambia de área. Es una operación normal, no excepcional.
- **El ciclo de vida cambia.** El sistema anterior movía las entidades a un directorio
  `VIGENTES/` y de ahí al archivo, lo que producía renombres masivos en el historial de Git
  y rompía de golpe todos los enlaces entrantes.
- **Los objetos migran de archivo por diseño.** Una tarea nace en `tareas/tareas.md` y
  termina en `tareas/tareas-2026-08.md`; un mes de entradas vive en `entradas/entradas.md` y luego
  pasa a `entradas/entradas-2026-08.md`. La partición por mes y el archivado por año son parte del modelo
  ([`spec/tarea.md`](../../spec/tarea.md) §2, [`spec/entradas.md`](../../spec/entradas.md) §2).
- **La federación entre perfiles, aunque aparcada, ya condiciona hoy.** Dos perfiles tienen
  árboles distintos; una referencia por ruta no cruza la frontera del perfil.

La alternativa viable —identidad por path, con un janitor que reescribe todas las referencias
en cada movimiento— es real y tiene una ventaja genuina: cero campos extra, cero ruido visual.
Su costo es que **cada movimiento se vuelve una transacción global sobre el perfil**: si el
janitor falla a medias, el repositorio queda inconsistente y no hay forma de detectarlo,
porque no queda rastro de cuál era la identidad anterior.

## Decisión

**Todo objeto del sistema tiene un `id` estable, único en el perfil e independiente de su
ruta. El path expresa jerarquía y partición; nunca identidad ni estado.**

- Entidades, planes, resultados y los archivos de entradas y tareas llevan `id` en front
  matter.
- Las tareas llevan su `id` como *block id* nativo de Obsidian al final de la línea
  (`^t-2026-0143`), de modo que es a la vez identificador del motor y ancla de enlace real.
- El `id` lo asigna el motor en el alta y **no cambia nunca**: ni al mover, ni al archivar,
  ni al migrar de esquema. Un `id` no se reutiliza tras una eliminación.
- Las referencias entre objetos se escriben como enlace Markdown donde **el texto es el `id`
  y la ruta es navegación**: `[sw-responsible](../entidades/trabajo/sw-responsible.md)`. El
  motor lee el texto; un janitor mantiene la ruta.
- El estado va en front matter, no en el path: `lifecycle: vigente | archivada`
  ([`spec/entidad.md`](../../spec/entidad.md) §2.3). Archivar es cambiar una palabra.
- `parent` **se deriva del path**, no se declara. Declararlo además sería garantía de
  desincronización.

## Consecuencias

**A favor.**

- Mover una entidad, archivarla o cambiar la partición de un archivo no rompe ninguna
  referencia. El janitor de rutas es una comodidad de navegación, no una garantía de
  integridad: si se atrasa, el motor sigue resolviendo bien.
- Los renombres masivos desaparecen del historial de Git, que queda legible como historial
  de la gestión y no del refactor de carpetas.
- El test de replay ([`docs/brief.md`](devel/VAULT/old/brief.md#3-principios) P3) se vuelve posible: sin
  identidad estable no hay forma de afirmar que un objeto reconstruido es *el mismo* objeto.
- La federación vía MCP queda abierta sin rediseño.

**En contra, y aceptado.**

- Redundancia deliberada: la referencia lleva `id` y ruta, y las dos pueden divergir. Se
  resuelve por precedencia explícita —**el `id` gana siempre**— y por invariantes que
  detectan la divergencia (N9, T3, E4).
- Ruido visual en el canónico: `^t-2026-0143` al final de cada tarea. Se mitiga porque
  Obsidian renderiza los block id de forma discreta y porque el resto de la trazabilidad va
  en comentarios HTML invisibles ([`spec/tarea.md`](../../spec/tarea.md) §3.1).
- El motor debe garantizar unicidad en el alta, lo que exige conocer los `id` existentes: es
  un índice reconstruible, nunca una fuente de verdad (P1).

**Referencia colgante.** Consecuencia no obvia y central: como el `id` es independiente, una
referencia puede sobrevivir a la desaparición de su destino. Se decide que `origin` —el
puntero de una tarea a la cadencia que la emitió— es una referencia **blanda**: un `origin`
colgante no viola ninguna invariante (K7). La regla muere, lo emitido no
([`spec/cadencia.md`](../../spec/cadencia.md) §7.1). En un sistema cuya promesa es recordar,
borrar una regla no puede borrar compromisos en silencio.

## Estado

`aceptado`
