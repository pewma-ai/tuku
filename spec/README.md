# spec

> Especificaciones normativas de TUKU. Se justifican por referencia a `../docs/principios.md` y `../docs/brief.md`. Lo que aquí se afirma es normativo para el motor: el código no inventa reglas, implementa lo que dice este directorio. Cuando código y spec discrepan, el defecto está en el código, salvo que la spec no se derive de `../docs/principios.md`, en cuyo caso el defecto está en la spec (ver el contrato en `../devel/README.md`).

Este directorio reemplaza al contenido normativo que antes vivía mezclado dentro de `../devel/que_implementar.md`. Ese archivo sigue existiendo, pero ahora responde solo "en qué orden se implementa"; lo que responde "qué hace el sistema" vive aquí.

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
| 2 | [bitacora.md](bitacora.md) | La entrada única: formato de línea, ontología cerrada (`**pendiente**`, `~~(Hecho)~~`, `**cadencia**`) y abierta, reglas de redacción |
| 3 | [pendientes.md](pendientes.md) | `PENDIENTES.md`: callouts con ancla, escalera de horizontes, sincronía de transclusiones |
| 4 | [ambitos.md](ambitos.md) | El árbol de ámbitos: los tres roles, qué carga cada directorio, resolución de reglas por cercanía, archivado |
| 5 | [cadencias.md](cadencias.md) | `CADENCIAS.md`: ciclo de vida de una cadencia, el trigger que conoce el tipo de ciclo, idempotencia |
| 6 | [notas.md](notas.md) | El zettelkasten, las notas tipadas y el procedimiento de destilado |
| 7 | [ciclo.md](ciclo.md) | `AHORA.md`, apertura y cierre, qué se aplana y qué queda siempre como enlace |
| 8 | [agente.md](agente.md) | Lo que cambia cuando el ejecutor es un agente de IA y no una persona con el flujo a mano |

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
  personal/
    AGENTS.md
    CADENCIAS.md
    personal.md               # página propia: es ámbito
  trabajo/
    AGENTS.md
    CADENCIAS.md
    trabajo.md
    clientes/                 # sin página: es categoría
      AGENTS.md
      CADENCIAS.md
      juanito_perez.md        # hoja: recibe entradas

notas/                        # zettelkasten, formato libre

reglas/                       # una regla por consecuencia
  pendientes.tuku.md
  enlaces.tuku.md
  cadencias.tuku.md
  propuestas.tuku.md
  janitors.tuku.md            # qué hace cada janitor
  config.tuku.md              # zona horaria, tipos de ciclo
  tipos/                      # una por tipo de nota
    persona.tuku.md

planes/                       # un plan por ciclo
  plan-2026-08-25-turno.md

reportes/                     # generados, el autor los lee
  resumen-2026-08-25-turno.md
  pendientes-por-actividad.md
  cadencias.md                # todas, colectadas del árbol

archivado/                    # ramas cerradas, enlaces vivos
```

**MAYÚSCULAS es de TUKU**, minúsculas es del autor. Se lee del árbol sin explicación.

Y no hay nada más en el disco. **Todo lo que existe, el autor lo puede abrir y leer.** No hay carpeta de cache ni archivos de máquina.

El contexto reciente y el vocabulario de ámbitos no son archivos: son la **salida de un janitor**, que se calcula cuando hace falta y se inyecta. Materializarlos solo agregaría copias que envejecen, porque una cola de bitácora queda vieja apenas se escribe la entrada siguiente. Calcularla en el momento es más simple y además más correcto.

Lo que sí se materializa, aunque sea generado, es lo que alguien mira o transcluye: `reportes/pendientes-por-actividad.md` lo transcluyen las páginas de actividad, y `reportes/cadencias.md` es donde el autor ve qué se le viene.

## Dónde viven los janitors

La **especificación** vive en el repositorio del autor: `reglas/janitors.tuku.md` describe en prosa qué debe hacer cada janitor, para que alguien pueda implementarlo en el futuro aunque el código de hoy ya no exista.

El **código** vive fuera, instalado, en `~/.tuku/janitors`. El `AGENTS.md` de la raíz lo declara, así que quien opere el libro lo encuentra en el primer archivo que abre.

La división es la de siempre: **la especificación sobrevive, la implementación se reemplaza.** Un script de 2026 no va a correr en 2046, pero la descripción de lo que hacía sí se va a leer. Y así el repositorio del autor no se vuelve una copia del código de TUKU que después diverge por su cuenta.

Cada janitor se especifica igual:

```markdown
## pendientes-atrasados

**Qué hace:** mueve a `^atrasados` los pendientes con fecha anterior a HOY, estampando el vencimiento.
**Cuándo:** a diario.
**Lee:** `PENDIENTES.md`
**Escribe:** `PENDIENTES.md`
**Regla:** pendientes.tuku.md, vencimiento
**A mano:** mover el ítem al callout `^atrasados` y anotar entre paréntesis la fecha en que vencía.
```

El campo **A mano** no es cortesía documental, es lo que sostiene el principio 1. Si un janitor no se puede ejecutar, el trabajo se hace igual, solo que cuesta más. Un janitor sin ese campo es una dependencia disfrazada.

## Qué está fuera de alcance

Cada spec declara su propio "no entra" en la sección correspondiente. A nivel de directorio:

- **Los janitors reales, en código.** Este directorio especifica su contrato (qué leen, qué escriben, el campo "A mano"); la implementación vive fuera del repositorio del autor, en `~/.tuku/janitors`, y su plan de construcción vive en `../devel/que_implementar.md`.
- **El orden de implementación y la estrategia de pruebas.** Eso es `../devel/que_implementar.md`, no este directorio: aquí se especifica qué hace el sistema, no en qué fase se construye ni cómo se verifica.
- **La deliberación con el autor** (archivar una rama, aprobar una propuesta). Se especifica la mecánica que la rodea, nunca el criterio para decidir.

## Decisiones abiertas

- Si el ciclo es una primitiva propia o se compone sobre bitácora, pendientes y notas. Hoy `../docs/principios.md` lo lista entre las primitivas pero lo describe como composición temporal.
- Dónde vive la capacidad del ciclo (costo fijo a restar de las horas brutas): un archivo global, o repartida por ámbito como las cadencias.
- Qué declara `reglas/config.tuku.md` y con qué formato. El árbol lo nombra (zona horaria, tipos de ciclo) pero nada lo especifica todavía.
