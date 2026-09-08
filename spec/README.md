# spec

> **Qué es este directorio.** Qué hace el sistema, con nombres de archivo, formatos e invariantes. Es la única capa que puede nombrar rutas y herramientas, y la única que cambia cuando cambia el layout. Los otros dos documentos del marco: [`../docs/brief.md`](../docs/brief.md) dice qué problema resuelve y para quién, y [`../docs/principios.md`](../docs/principios.md) da el criterio para decidir lo que aún no está escrito.

> Especificaciones normativas de TUKU. Se justifican por referencia a [`../docs/principios.md`](../docs/principios.md) y [`../docs/brief.md`](../docs/brief.md). Lo que aquí se afirma es normativo para el motor: el código no inventa reglas, implementa lo que dice este directorio. Cuando código y spec discrepan, el defecto está en el código, salvo que la spec no se derive de [`../docs/principios.md`](../docs/principios.md), en cuyo caso el defecto está en la spec.
> [!question] Referencia rota #REVISAR
> Esta nota citaba "el contrato en `../devel/README.md`", archivo que no existe en el repositorio. No hay ningún documento que hoy desarrolle ese contrato; decidir si se escribe o si la frase se borra.

Este directorio reemplaza al contenido normativo que antes vivía mezclado dentro del plan de fases. La especificación de "qué hace el sistema" vive aquí; el orden y estado de implementación vive en [`../devel/epics.md`](../devel/epics.md).

## Normativo no quiere decir definitivo

Estas specs se van a corregir con el uso. Están escritas desde lo que ya se probó, y cada experimento sobre el sistema real puede mover lo que aquí dice. Eso es el método, no una deuda.

Las dos escalas de tiempo no se contradicen:

- **Dentro de un epic**, la spec manda sobre el código. Si al implementar aparece un caso que la spec no cubre, no se decide en el código: se escribe primero aquí.
- **Entre epics**, el experimento manda sobre la spec. Lo que el uso demuestre distinto se corrige en este directorio, y esa corrección es un resultado del epic, no un fallo.

Corolario: una spec que lleva mucho sin tocarse no está madura necesariamente. Puede ser que esa parte todavía no se haya usado.

## Orden de lectura

Igual que las fases de implementación, se lee de lo que no depende de nada a lo que compone todo lo anterior.

| # | Documento | Qué especifica |
| --- | --- | --- |
| 1 | [flujo-informacion.md](flujo-informacion.md) | El marco: la frontera entre registrar y aplicar consecuencias, los cinco pasos, y la segunda vía de entrada (sin bitácora) |
| 2 | [bitacora.md](bitacora.md) | El registro: formato de línea, ontología cerrada (`**pendiente**`, `~~(Hecho)~~`, `**cadencia**`) y abierta, reglas de redacción |
| 3 | [pendientes.md](pendientes.md) | `PENDIENTES.md`: tabla única, escalera de horizontes, y cómo llega cada vista (propagación y transclusión) |
| 4 | [ambitos.md](ambitos.md) | El árbol de ámbitos: los tres roles, qué carga cada directorio, qué prevalece y qué se acumula, archivado |
| 5 | [cadencias.md](cadencias.md) | `CADENCIAS.md`: ciclo de vida de una cadencia, qué puede emitir, el trigger que conoce el tipo de ciclo, idempotencia |
| 6 | [notas.md](notas.md) | El zettelkasten, las notas tipadas y el procedimiento de destilado |
| 7 | [ciclo.md](ciclo.md) | `AHORA.md`, su frontmatter, apertura y cierre, qué se aplana y qué queda siempre como enlace |
| 8 | [cli.md](cli.md) | El contrato del comando `tuku`: qué garantiza, códigos de salida, forma de la salida. Independiente de quién invoque |
| 9 | [agente.md](agente.md) | Lo que cambia cuando el ejecutor es un agente de IA y no una persona con el flujo a mano |

## Árbol de directorios

```text
AGENTS.md                     # reglas de todo el repo
LIBRO-DE-ESTILO.md            # reglas del autor, canónico
AHORA.md                      # ciclo en curso
PENDIENTES.md                 # fuente de verdad
log.md                        # generado, OKF compliant
index.md                      # generado, OKF compliant

bitacoras/                    # ciclos cerrados, inmutables
  bitacora-2026-08-25-2026-09-01.md

ambitos/                      # el árbol de la vida
  AGENTS.md                   # reglas de toda la rama
  CADENCIAS.md                # cadencias de toda la rama
  PENDIENTES-AMBITOS.md       # generado, un callout por ámbito, se transcluye
  personal/
    AGENTS.md
    CADENCIAS.md
    CAPACIDAD.md              # el bruto, si se declara. Opcional
    personal.md               # página propia: es ámbito
  trabajo/
    AGENTS.md
    CADENCIAS.md
    CAPACIDAD.md              # costo fijo de este ámbito. Opcional
    trabajo.md
    clientes/                 # sin página: es categoría
      AGENTS.md
      CADENCIAS.md
      juanito_perez.md        # hoja: recibe registros

notas/                        # zettelkasten, formato libre

reglas/                       # una regla por consecuencia
  pendientes.tuku.md
  enlaces.tuku.md
  cadencias.tuku.md
  propuestas.tuku.md
  comandos.tuku.md            # qué hace cada comando
  config.tuku.md              # TZ, cycle_type, tuku_template
  types.md                    # los `type` que el vault reconoce
  plantilla/
    AHORA.md                  # de aquí sale un ciclo nuevo
  tipos/                      # una por tipo de nota
    persona.tuku.md

planes/                       # un plan por ciclo
  plan-2026-08-25-turno.md

reportes/                     # generados, el autor los lee
  resumen-2026-08-25-turno.md
  cadencias.md                # todas, colectadas del árbol

archivado/                    # ramas cerradas, enlaces vivos
```

**MAYÚSCULAS es de TUKU**, minúsculas es del autor. Se lee del árbol sin explicación.

Y no hay nada más en el disco. **Todo lo que existe, el autor lo puede abrir y leer.** No hay carpeta de cache ni archivos de máquina.

El contexto reciente y el vocabulario de ámbitos no son archivos: son la **salida de un comando**, que se calcula cuando hace falta y se inyecta. Materializarlos solo agregaría copias que envejecen, porque una cola de bitácora queda vieja apenas se escribe el registro siguiente. Calcularla en el momento es más simple y además más correcto.

Lo que sí se materializa, aunque sea generado, es lo que alguien mira o transcluye: `ambitos/PENDIENTES-AMBITOS.md` lo transcluyen las páginas de ámbito, y `reportes/cadencias.md` es donde el autor ve qué se le viene.

## El frontmatter

Todo archivo del vault que guarde conocimiento **declara `type`** en un bloque YAML arriba. Es el único campo obligatorio, y es lo que hace que un vault lo entienda algo que nunca oyó hablar de TUKU.

El formato es [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format), el Open Knowledge Format de Google: markdown con frontmatter, un concepto por archivo, sin herramientas obligatorias ni registro central de esquemas. Se adopta porque describe lo que el diseño ya hacía, no porque agregue algo.

**Los nombres de campo van en inglés**, como los comandos `tuku`: son superficie experta, la lee una máquina o alguien que sabe lo que busca. El cuerpo sigue en castellano, que es donde escribe el autor.

**La lista de `type` vive en [`reglas/types.md`](../template/vanilla/reglas/types.md)**, no en el libro de estilo. Es contrato: renombrar `Logbook` rompe los comandos y deja el vault ilegible para cualquier herramienta que hable OKF, al revés de las tablas del libro de estilo, que el autor cambia a gusto. Los tipos que hay hoy son `Logbook`, `Pending`, `Scope`, `Note`, `Cadence`, `Capacity`, `Config` y `Style Guide`. Agregar uno es agregar una fila.

**Los `AGENTS.md` quedan fuera** y no llevan frontmatter: son reglas de operación, no conocimiento.

Un `type` puede pedir campos propios, y los declara la spec de esa primitiva: `Logbook` lleva además `status`, `from` y `to` ([ciclo.md](ciclo.md)).

Que se cumpla lo verifica `tuku doctor`, que lee los tipos válidos de `reglas/types.md` en tiempo de ejecución y recorre el vault entero.

**Se documenta lo que se usa.** OKF permite más campos de los que TUKU escribe hoy; los que no se escriben todavía no se declaran, para que la spec no prometa lo que el vault no trae.

## Dónde viven los comandos

La **especificación** vive en el repositorio del autor: `reglas/comandos.tuku.md` describe en prosa qué debe hacer cada comando, para que alguien pueda implementarlo en el futuro aunque el código de hoy ya no exista.

El **código** vive fuera del vault, en el paquete `tuku` que instala `pipx` o `uv tool install` (epic 001 de [`../devel/epics.md`](../devel/epics.md)). En el vault no hay código. El `AGENTS.md` de la raíz lo declara, así que quien opere el libro lo encuentra en el primer archivo que abre.

La división es la de siempre: **la especificación sobrevive, la implementación se reemplaza.** Un script de 2026 no va a correr en 2046, pero la descripción de lo que hacía sí se va a leer. Y así el repositorio del autor no se vuelve una copia del código de TUKU que después diverge por su cuenta.

El nombre canónico de cada comando es su invocación, `tuku <noun> <verb>`, y ese es el encabezado con que se especifica. Cada uno se especifica igual:

```markdown
## todo propagate

**Qué hace:** regenera las dos vistas derivadas de `PENDIENTES.md`, la región del día dentro de cada `## <día>` de `AHORA.md` y el archivo `ambitos/PENDIENTES-AMBITOS.md`. Es idempotente, y sobre un vault cuadrado no cambia nada.
**Cuándo:** cada vez que `PENDIENTES.md` cambia.
**Lee:** `PENDIENTES.md`, el árbol de `ambitos/`
**Escribe:** `AHORA.md`, `ambitos/PENDIENTES-AMBITOS.md`
**Regla:** pendientes.tuku.md
**A mano:** recorrer `PENDIENTES.md` y reescribir a mano las dos vistas: bajo cada día de `AHORA.md`, entre el encabezado y el primer registro, los pendientes con fecha de ese día; y en `PENDIENTES-AMBITOS.md`, un callout por ámbito del árbol, con sus pendientes o con `SIN PENDIENTES`.
```

El campo **A mano** no es cortesía documental, es lo que sostiene el principio 1. Si un comando no se puede ejecutar, el trabajo se hace igual, solo que cuesta más. Un comando sin ese campo es una dependencia disfrazada.

## Qué está fuera de alcance

Cada spec declara su propio "no entra" en la sección correspondiente. A nivel de directorio:

- **Los comandos reales, en código.** Este directorio especifica su contrato (qué leen, qué escriben, el campo "A mano", y en [cli.md](cli.md) lo que vale para todos); la implementación vive fuera del vault, en el paquete que instala `pipx`, y su plan de construcción vive en [`../devel/epics.md`](../devel/epics.md).
- **El orden de implementación y la estrategia de pruebas.** Eso es [`../devel/epics.md`](../devel/epics.md), no este directorio: aquí se especifica qué hace el sistema, no en qué fase se construye ni cómo se verifica.
- **La deliberación con el autor** (archivar una rama, aprobar una propuesta). Se especifica la mecánica que la rodea, nunca el criterio para decidir.

## Decidido

- **La capacidad vive repartida por ámbito**, en archivos `CAPACIDAD.md` opcionales: el bruto, si se declara, una sola vez en `ambitos/personal/`; los costos fijos en el ámbito que los causa. Se acumulan en vez de prevalecer, igual que las cadencias: de los tres archivos por directorio, `AGENTS.md` es el único que es una regla y el único que prevalece. Es deseable, no requisito: el sistema se opera sin capacidad y sin cadencias. Formato y cálculo en [ciclo.md](ciclo.md), ubicación en el árbol en [ambitos.md](ambitos.md).

- **`reglas/config.tuku.md` es una tabla**, y es lo único que leen las automatizaciones de ese archivo. Tres campos hoy: `TZ`, la zona horaria con su nombre IANA, que decide qué día es HOY y por lo tanto qué está atrasado; `cycle_type`, el ritmo con que se abre y se cierra; y `tuku_template`, la variante de la que salió el vault. Los nombres de campo van en inglés, como el resto del frontmatter. La escribe `tuku init`, que toma la zona horaria de la máquina, y un callout en el archivo lo dice. Ningún dato nuevo destinado a una automatización se agrega al libro de estilo (ver [bitacora.md](bitacora.md), "dónde vive cada una"): va a esta tabla, y quien necesite mostrarlo la transcluye en vez de copiarla.

## Decisiones abiertas

- **Cómo se especifica una cadencia que se gatilla por un evento y no por una fecha.** El caso que lo destapó es el cierre del ciclo: la cadencia sembrada dice `Cuándo: viernes, semanal`, pero lo que la gatilla es que el ciclo termine, y el viernes deja de significar nada si el ciclo pasa a ser quincenal. La fecha es un síntoma del evento. La propuesta sobre la mesa es que `Cuándo` acepte dos gramáticas distinguidas por la primera palabra (todo lo que empieza con `al ` es evento, lo demás es calendario), que los eventos sean vocabulario cerrado en un `reglas/eventos.md` verificable por `tuku doctor`, porque cada evento es código que mira el vault, y que un evento que dura varios días emita una sola vez reusando la idempotencia del pendiente en vez de llevar un registro de eventos vistos. Queda por decidir, y lo decide el epic 005, que es donde entran las cadencias.
- Si el ciclo es una primitiva propia o se compone sobre bitácora, pendientes y notas. Hoy [`../docs/principios.md`](../docs/principios.md) lo lista entre las primitivas pero lo describe como composición temporal.
