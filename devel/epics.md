# Plan de desarrollo de TUKU: Epics y Fases

> Única fuente de verdad de alto nivel sobre cómo se construye TUKU. Los epics son la unidad de entrega (cortan por estado del vault); las fases son el corte técnico interno por primitiva. Si un documento entra en contradicción con este, manda este archivo.

## Los epics mueven el diseño

El diseño lo dirige la experimentación, no al revés: [`spec/`](../spec/README.md) y [`docs/`](../docs/README.md) cambian por efecto de los epics. Cada epic entrega dos cosas: su producto y lo que le enseñó al diseño. Dentro de un epic la spec manda sobre el código; entre epics, el experimento manda sobre la spec.

El orden de trabajo es siempre el mismo:
1. **De lo determinista a lo agéntico:** un tramo determinista corre mil veces gratis; uno agéntico cuesta tokens y no repite resultado. El escenario con LLM va al final, nunca en la base de una cadena.
2. **De lo simple a lo complejo:** una primitiva antes que la combinación, un ámbito antes que un árbol, el mínimo de registros antes que el volumen con ruido.
3. **Del caso feliz al caso borde.**

## Epics y Fases: dos cortes perpendiculares

Las fases cortan **por primitiva** (registro, pendientes, ámbitos, cadencias, notas); los epics cortan **por el estado inicial del vault**. El motivo es el criterio de entrega: "los pendientes funcionan" no es una experiencia que alguien pueda usar; "el día uno funciona" sí lo es.

Un epic puede abarcar varias fases (el 002 hace la versión mínima de las fases 3 y 5, y el 004 las completa contra un vault poblado), fundir una fase con LLM y una sin él (el 005 junta la 6 y la 7), o una fase puede partirse entre dos epics (la fase 1 la construye el epic 002 a mano y el 003 dictado).

| Fase | Nombre | Qué se puede hacer al terminarla | LLM | Fixture | Epic |
| --- | --- | --- | --- | --- | --- |
| 0 | El vault que se puede abrir | Empezar a escribir a mano | no | `vacio` | 001 |
| 1 | El registro | Dictar y que quede bien escrito | parcial | `primer-dia` | 002 a mano, 003 dictado |
| 2 | Pendientes | Que no se olvide nada | no | `ciclo-en-curso` | 002 |
| 3 | El árbol de ámbitos | Que cada cosa tenga su lugar | no | `ciclo-en-curso` | 002 mínimo, 004 completo |
| 4 | Cadencias | Que el sistema recuerde solo | no | `ciclo-en-curso` | 005 |
| 5 | Notas y enlaces | Que el tejido se mantenga | no | `ciclo-en-curso` | 002 mínimo, 004 completo |
| 6 | El ciclo | Abrir y cerrar sin perder nada | no | `ciclo-por-cerrar` | 005 |
| 7 | Plan y resumen | Que la propuesta valga la pena leerla | sí | `ciclo-por-cerrar` | 005 |
| 9 | Inferencia semántica | Que note cosas que nadie pidió | sí | `historico` | 006 |

La numeración salta la fase 8 porque el endurecimiento pasó a la Wishlist: no agrega capacidades, cierra huecos.

### Criterios transversales

- **Entregable solo:** cada fase deja algo usable para no quedar con un sistema a medio construir.
- **Un fixture nuevo por vez:** si necesita dos estados iniciales nuevos, está haciendo dos cosas.
- **El LLM se aísla:** las fases 1, 7 y 9 lo usan y las demás no.
- **Idempotencia:** correr cualquier operación dos veces da el mismo resultado (principio 9).
- **El campo "A mano":** ningún comando entra sin él para garantizar el principio 1.
- **Contrato de [`spec/cli.md`](../spec/cli.md):** códigos de salida fijos, mensajes que nombran defecto y corrección, y ante la duda informar sin escribir.

## Estrategia de pruebas

Registrar un hecho produce texto en la bitácora. Todo lo demás (abrir o cerrar pendientes, emitir cadencias, enlazar, proponer) ocurre después, leyendo lo escrito. El sistema se organiza en tres tramos:

| Tramo | Naturaleza | Cómo se prueba |
| --- | --- | --- |
| Dictado a campos | Juicio: cuántos hechos, qué ámbito, qué clase, qué hora | LLM contra ground truth de [`referencia-faena.md`](../corpus/referencia/referencia-faena.md), comparando llamadas de comando `tuku`. Cuesta tokens |
| Campos a línea | Formato: línea canónica, día y orden cronológico | Determinista. `entry add` y `entry lint`, sin modelo |
| Línea a consecuencias | Mecánico: reacciona a lo escrito en el vault | Determinista. Inyección de líneas y verificación del vault |

### Dos puntos de inyección

1. **Vía bitácora:** hechos de la vida del autor que derivan consecuencias (abrir/cerrar pendientes, emitir cadencias, enlazar). Toda consecuencia debe ser derivable del texto del registro.
2. **Vía comando directo:** operaciones de sistema o decisiones explícitas (mover pendiente de escalón, corregir plan, aprobar/rechazar propuesta) mediante `tuku <noun> <verb>`.

Ambas vías terminan en invocaciones de `tuku`. No hay una tercera forma de cambiar el vault.

### Transiciones de estado y escalera de fixtures

Toda prueba afirma el diff (`delta`) entre el estado inicial y el resultante, nunca un árbol congelado. Dentro de un epic los escenarios se encadenan en [`playground/`](../playground/README.md).

| Fixture | Cómo se llega | Qué habilita probar |
| --- | --- | --- |
| `vacio` | recién instalado con `tuku init` | que se pueda empezar (Epic 001) |
| `primer-dia` | un registro inyectado en su día | el registro y consecuencias inmediatas (Epics 002 y 003) |
| `ciclo-en-curso` | varios días, pendientes en escalones, cadencias vigentes | casi todo el tejido (Epic 004) |
| `ciclo-por-cerrar` | ciclo completo sin cerrar | el cierre y apertura de ciclo (Epic 005) |
| `historico` | varios ciclos cerrados | archivado, enlaces antiguos e inferencia (Epic 006) |

### Superficie del CLI

Todo epic que añada comandos fija su superficie en un escenario propio: `tuku -h` nombra los nouns, cada subcomando nombra sus argumentos y opciones, ningún código de salida se pisa y todo error nombra defecto y corrección.

## Estado de los Epics

Actualizado el 2026-09-07.

| Epic | Nombre | Estado inicial | Estado | Qué falta para cerrarlo |
| --- | --- | --- | --- | --- |
| 001 | Un TUKU mínimo instalable | `vacio` | reabierto, mecanismo hecho | `tuku init` implementado y los siete `001-0X` en verde; falta re-verificación con persona sobre `uv tool install` + `tuku init` |
| 002 | El día uno, a mano | `vacio` → `primer-dia` | por cerrar | diez escenarios deterministas en verde (`002-01` a `002-10`). Falta revisión a mano de `playground/002-09-crear-nota/` contra criterio de salida |
| 003 | El día uno, dictado | `vacio` → `primer-dia` | sin empezar | desbloqueado. Replica el 002 con entrada en lenguaje natural |
| 004 | El día ciento cincuenta | `ciclo-en-curso` | sin empezar | depende del epic 003 |
| 005 | Abrir y cerrar el ciclo | `ciclo-por-cerrar` | sin empezar | depende del epic 004 |
| 006 | Que note lo que nadie pidió | `historico` | sin empezar | depende del epic 005 |

## Epic 001. Un TUKU mínimo instalable

Que una persona nueva instale TUKU con un comando, siembre un vault en un directorio vacío y empiece a escribir el mismo día, sin configurar nada y sin saber qué es TUKU. Cubre la fase 0.

- **Entregable:** `uv tool install git+https://github.com/pewma-ai/tuku.git@devel` deja `tuku` en PATH; `tuku init mi-vault` produce el estado cero sin tocar la red.
- **Detalle completo:** [`../tests/escenarios/001-00-un-tuku-minimo-instalable.md`](../tests/escenarios/001-00-un-tuku-minimo-instalable.md). Los siete escenarios (`001-01` a `001-07`) están en verde.

## Epic 002. El día uno, a mano

Alguien instala TUKU y empieza a usarlo el mismo día sobre un vault vacío. Todo lo que hace lo hace invocando `tuku` a mano: cada cosa que necesita la crea al escribirla. Cubre las fases 1 y 2 completas, y la versión mínima de las fases 3 y 5.

- **Entregable:** ciclo abierto con plantilla completa, registros cronológicos, pendientes que abren y cierran, fechado automático, ámbito creado con enlaces retroactivos y nota creada a petición.
- **Detalle completo:** [`../tests/escenarios/002-00-el-dia-uno-a-mano.md`](../tests/escenarios/002-00-el-dia-uno-a-mano.md). Los diez escenarios (`002-01` a `002-09` en cadena más `002-10` fuera de ella) están en verde.

## Epic 003. El día uno, dictado

El mismo día uno del epic 002 con la misma entrada de [`referencia-faena.md`](../corpus/referencia/referencia-faena.md), pero dictada en lenguaje natural. El agente compila el dictado en llamadas `tuku` en vez de escribir archivos, reproduciendo el vault del 002.

- **Entregable:** agente LLM que infiere campos y emite comandos deterministas; vault resultante idéntico al producido a mano.
- **Detalle completo:** [`../tests/escenarios/003-00-el-dia-uno-dictado.md`](../tests/escenarios/003-00-el-dia-uno-dictado.md). Desbloqueado para comenzar; stubs `003-01` y `003-02` creados.

## Epic 004. El día ciento cincuenta

Lo mismo del epic 002 sobre un vault que ya tiene meses encima con activo acumulado (ámbitos poblados, notas escritas, historial de pendientes). Segunda vuelta de capacidades donde aparecen enlaces automáticos desde el primer día, autoasignación de pendientes, notas con "Ver además" y versiones completas de ámbitos y destilados. Cubre fases 3 y 5 completas, y resto de la 4.

- **Criterio de salida:** inyectar un ciclo de `mac-jpgil` sobre un vault poblado produce enlaces, asignación a ámbitos y notas tejidas sin intervención.

## Epic 005. Abrir y cerrar el ciclo

Que un ciclo se abra y se cierre sin perder nada, y que lo propuesto al abrirlo valga la pena leerlo. Las cadencias entran acá porque emiten en la apertura del ciclo. Cubre fases 6 y 7, más lo restante de la 4. La mecánica determinista (abrir, promover pendientes, aplanar transclusiones, archivar) se prueba con archivos inyectados antes de conectar el LLM para plan y resumen.

- **Criterio de salida:** abrir dos veces no duplica; cerrar dos veces no vuelve a mover; prueba que falla a propósito si se aplana antes del resumen. Plan calcula capacidad contra lo declarado.

## Epic 006. Que note lo que nadie pidió

El agente deja de responder y empieza a observar: infiere ámbitos y notas tipadas desde el histórico, detecta recurrencias que nadie declaró como cadencia y propone sin ejecutar. Cubre fase 9.

- **Criterio de salida:** la prueba dura es negativa: rechazar una propuesta no deja rastro en ninguna primitiva (principio 3).

## Wishlist

Lo que hay que hacer y no bloquea a nadie:
- **Endurecimiento:** casos de error, reconstrucción completa (`tuku rebuild`) e idempotencia global sobre el sistema entero. Un error del autor nunca se rechaza, se reporta.
- **Prueba con usuario ajeno:** verificar instalación y primer registro leyendo solo `AGENTS.md`.
- **Publicación web:** visor estático con Quartz.
- **Captura móvil:** integración ligera por Telegram.

## Apéndice: referencia de mac-jpgil

Referencia histórica de lo que funcionaba en `mac-jpgil`. Lo que allá era script es formalizable a determinismo; lo que era proceso de agente requería juicio.

### Scripts deterministas (`procesos/scripts/`)
- `jntr.bitacora-tail.py`: contexto reciente de últimos ciclos.
- `jntr.tareas-pendientes.py`: pendientes (linter, scan, transfer, validate).
- `jntr.org-categories-summary.py`: vocabulario controlado desde `keywords`.
- `jntr.org-frontpage-update.py`: front pages de áreas.
- `jntr.notes-index-update.py`: mantención de índice de notas.
- `jntr.check-broken-links.py`: enlaces rotos y notas huérfanas.
- `jntr.obsidian-links-to-markdown.py`: conversión de wikilinks a markdown estándar.
- `jntr.find-tags.py`: búsqueda y agrupación de etiquetas.
- `jntr.persona.py`: notas de personas.

### Procesos de agente (`procesos/*.MaC.md`)
- `apertura-semanal` y `cierre-semanal`: ciclo, días y resumen.
- `transferencia-pendientes`: arrastre entre ciclos.
- `pendientes-en-bitacora`: detección y cierre desde dictado.
- `radar`: consulta en vivo del estado presente.
- `propagate-local-activity-to-org`: propagación de hitos y decisiones a páginas de área.
