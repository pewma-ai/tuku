# Plan de desarrollo de TUKU: Epics y Fases

> Única fuente de verdad de alto nivel sobre cómo se construye TUKU. Los epics son la unidad de entrega (cortan por estado del vault); las fases son el corte técnico interno por primitiva. Si un documento entra en contradicción con este, manda este archivo.

## Los epics mueven el diseño

El diseño lo dirige la experimentación, no al revés: [`spec/`](../spec/README.md) y [`docs/`](../docs/README.md) cambian por efecto de los epics. Cada epic entrega dos cosas: su producto y lo que le enseñó al diseño. Dentro de un epic la spec manda sobre el código; entre epics, el experimento manda sobre la spec.

El orden de trabajo es siempre el mismo:
1. **De lo determinista a lo agéntico:** un tramo determinista corre mil veces gratis; uno agéntico cuesta tokens y no repite resultado. El escenario con LLM va al final, nunca en la base de una cadena.
2. **De lo simple a lo complejo:** una primitiva antes que la combinación, un ámbito antes que un árbol, el mínimo de registros antes que el volumen con ruido.
3. **Del caso feliz al caso borde.**

Un epic se abre escribiendo dos cosas a la vez, antes de implementar nada: sus escenarios en [`tests/escenarios/`](../tests/escenarios/README.md) y su capítulo del [tutorial](../docs/tutorial/README.md). Los escenarios dicen qué se verifica; el capítulo dice qué se le promete a quien va a usarlo, y esa promesa es la que guía el epic. Así se abrió el 003, y el capítulo sirve además de prueba a mano mientras los escenarios agénticos todavía no corren.

## Epics y Fases: dos cortes perpendiculares

Las fases cortan **por primitiva** (registro, pendientes, ámbitos, cadencias, notas); los epics cortan **por el estado inicial del vault**. El motivo es el criterio de entrega: "los pendientes funcionan" no es una experiencia que alguien pueda usar; "el día uno funciona" sí lo es.

Un epic puede abarcar varias fases (el 002 hace la versión mínima de las fases 3 y 5, y el 005 las completa contra un vault poblado), fundir una fase con LLM y una sin él (el 006 junta la 6 y la 7), o una fase puede partirse entre varios epics (la fase 1 la construye el 002 a mano, el 003 dictada y el 004 conversada).

| Fase | Nombre | Qué se puede hacer al terminarla | LLM | Fixture | Epic |
| --- | --- | --- | --- | --- | --- |
| 0 | El vault que se puede abrir | Empezar a escribir a mano | no | `vacio` | 001 |
| 1 | El registro | Dictar y que quede bien escrito | parcial | `primer-dia` | 002 a mano, 003 dictado, 004 conversado |
| 2 | Pendientes | Que no se olvide nada | no | `ciclo-en-curso` | 002 |
| 3 | El árbol de ámbitos | Que cada cosa tenga su lugar | no | `ciclo-en-curso` | 002 mínimo, 005 completo |
| 4 | Cadencias | Que el sistema recuerde solo | no | `ciclo-en-curso` | 006 |
| 5 | Notas y enlaces | Que el tejido se mantenga | no | `ciclo-en-curso` | 002 mínimo, 005 completo |
| 6 | El ciclo | Abrir y cerrar sin perder nada | no | `ciclo-por-cerrar` | 006 |
| 7 | Plan y resumen | Que la propuesta valga la pena leerla | sí | `ciclo-por-cerrar` | 006 |
| 9 | Inferencia semántica | Que note cosas que nadie pidió | sí | `historico` | 007 |

La numeración salta la fase 8 porque el endurecimiento pasó a la Wishlist: no agrega capacidades, cierra huecos.

### Criterios transversales

- **Entregable solo:** cada fase deja algo usable para no quedar con un sistema a medio construir.
- **Un fixture nuevo por vez:** si necesita dos estados iniciales nuevos, está haciendo dos cosas.
- **El LLM se aísla:** las fases 1, 7 y 9 lo usan y las demás no.
- **Idempotencia:** correr cualquier operación dos veces da el mismo resultado (principio 9).
- **La ayuda como equivalente manual:** ningún comando entra sin una descripción que diga qué archivos toca y cómo, para garantizar el principio 1.
- **Contrato de [`spec/cli.md`](../spec/cli.md):** códigos de salida fijos, mensajes que nombran defecto y corrección, y ante la duda informar sin escribir.

## Estrategia de pruebas

Registrar un hecho produce texto en la bitácora. Todo lo demás (abrir o cerrar pendientes, emitir cadencias, enlazar, proponer) ocurre después, leyendo lo escrito. El sistema se organiza en tres tramos:

| Tramo | Naturaleza | Cómo se prueba |
| --- | --- | --- |
| Dictado a campos | Juicio: cuántos hechos, qué ámbito, qué clase, qué hora | LLM contra ground truth de [`referencia-faena.md`](../corpus/referencia/referencia-faena.md), comparando llamadas de comando `tuku`. Cuesta tokens |
| Campos a línea | Formato: línea canónica, día y orden cronológico | Determinista. `entry create` y `doctor entry`, sin modelo |
| Línea a consecuencias | Mecánico: reacciona a lo escrito en el vault | Determinista. Inyección de líneas y verificación del vault |

### Dos puntos de inyección

1. **Vía bitácora:** hechos de la vida del autor que derivan consecuencias (abrir/cerrar pendientes, emitir cadencias, enlazar). Toda consecuencia debe ser derivable del texto del registro.
2. **Vía comando directo:** operaciones de sistema o decisiones explícitas (mover pendiente de escalón, corregir plan, aprobar/rechazar propuesta) mediante `tuku <noun> <verb>`.

Ambas vías terminan en invocaciones de `tuku`. No hay una tercera forma de cambiar el vault.

> [!tip] Mirar en VAULT cuando se endurezca el parser
> [`VAULT/scratchpad/tuku-docs/corpus-regresion/contrato-de-regeneracion.md`](VAULT/scratchpad/tuku-docs/corpus-regresion/contrato-de-regeneracion.md) propone un subconjunto congelado con casos límite deliberados (viñetas malformadas, tipos desconocidos, enlaces rotos, entradas sin hora) contra el que corre todo cambio al parser. Hoy [`corpus/`](../corpus/README.md) tiene dictados de referencia, pero no casos adversarios del parser.

### Transiciones de estado y escalera de fixtures

Toda prueba afirma el diff (`delta`) entre el estado inicial y el resultante, nunca un árbol congelado. Dentro de un epic los escenarios se encadenan en [`playground/`](../playground/README.md).

| Fixture | Cómo se llega | Qué habilita probar |
| --- | --- | --- |
| `vacio` | recién instalado con `tuku init` | que se pueda empezar (Epic 001) |
| `primer-dia` | un registro inyectado en su día | el registro y consecuencias inmediatas (Epics 002 y 003) |
| `ciclo-en-curso` | varios días, pendientes en escalones, cadencias vigentes | casi todo el tejido (Epic 005) |
| `ciclo-por-cerrar` | ciclo completo sin cerrar | el cierre y apertura de ciclo (Epic 006) |
| `historico` | varios ciclos cerrados | archivado, enlaces antiguos e inferencia (Epic 007) |

### Superficie del CLI

Todo epic que añada comandos fija su superficie en un escenario propio: `tuku -h` nombra los nouns, cada subcomando nombra sus argumentos y opciones, ningún código de salida se pisa y todo error nombra defecto y corrección.

## Estado de los Epics

Actualizado el 2026-10-16.

| Epic | Nombre | Estado inicial | Estado | Qué falta para cerrarlo |
| --- | --- | --- | --- | --- |
| 001 | Un TUKU mínimo instalable | `vacio` | cerrado | cerrado el 2026-09-19; seis escenarios en verde y verificación humana de instalación limpia y siembra offline completada |
| 002 | El día uno, a mano | `vacio` → `primer-dia` | cerrado | cerrado el 2026-09-19; doce escenarios deterministas en verde y aceptación humana en playground/002-09 completada |
| 003 | El día uno, dictado | `vacio` → `primer-dia` | por cerrar | cinco escenarios: `003-01` determinista; `003-10`, el día uno entero en un turno (fundió del `003-02` al `003-07` el 2026-10-16), y `003-11`, el día derivado, en verde con `agy`; `003-08` (`hermes`) y `003-09` (`claude`) en verde el 2026-09-20, sin repetir desde entonces. Falta revisión a mano de los turnos de `playground/003-*/` contra criterio de salida |
| 004 | La conversación | `primer-dia` | sin empezar | depende del epic 003 |
| 005 | El día ciento cincuenta | `ciclo-en-curso` | escenarios escritos | siete documentos en `tests/escenarios/005-*`: 20 de 31 tests deterministas en verde y 11 en rojo, más 5 agénticos (3 en verde, 1 en rojo y 1 que se salta). Los rojos son hallazgos: cada uno está en la tabla de `005-00` (lista de hijos en dos órdenes, `doctor note`, atrasados, nota tipada, agente que adivina) |
| 006 | Abrir y cerrar el ciclo | `ciclo-por-cerrar` | sin empezar | depende del epic 005 |
| 007 | Que note lo que nadie pidió | `historico` | sin empezar | depende del epic 006 |
| 008 | MAINTENANCE MODE | por definir | por definir | sin detalles aún: tests del modo de mantenimiento del `AGENTS.md` del vault |

## Epic 001. Un TUKU mínimo instalable

Que una persona nueva instale TUKU con un comando, siembre un vault en un directorio vacío y empiece a escribir el mismo día, sin configurar nada y sin saber qué es TUKU. Cubre la fase 0.

- **Entregable:** `uv tool install git+https://github.com/pewma-ai/tuku.git@devel` deja `tuku` en PATH; `tuku init mi-vault` produce el estado cero sin tocar la red.
- **Detalle completo:** [`../tests/escenarios/001-00-un-tuku-minimo-instalable.md`](../tests/escenarios/001-00-un-tuku-minimo-instalable.md). Seis escenarios en verde (`001-01` a `001-04`, `001-06` y `001-07`). Cerrado tras verificación humana de instalación y siembra offline.

## Epic 002. El día uno, a mano

Alguien instala TUKU y empieza a usarlo el mismo día sobre un vault vacío. Todo lo que hace lo hace invocando `tuku` a mano: cada decisión del autor (`tuku entry create`, `tuku todo open`, `tuku note create`, etc.) deja huella cronológica en la bitácora del ciclo y aplica sus consecuencias de forma atómica e idempotente. Cubre las fases 1 y 2 completas, y la versión mínima de las fases 3 y 5.

- **Entregable:** ciclo abierto con plantilla completa, registros cronológicos, consecuencias aplicadas de forma atómica vía bitácora, fechado automático, ámbito creado con enlaces retroactivos y nota creada a petición.
- **Detalle completo:** [`../tests/escenarios/002-00-el-dia-uno-a-mano.md`](../tests/escenarios/002-00-el-dia-uno-a-mano.md). El día en cadena, un escenario por tramo ([`002-13`](../tests/escenarios/002-13-el-dia.md)), y sus casos borde sobre el vault final ([`002-14`](../tests/escenarios/002-14-casos-borde.md)); lo que no necesita el día está en unitarios. Se salda el principio 9 mediante `tuku regenerate`. Cerrado el 2026-09-19 tras verificación humana de notas y bitácora en Obsidian.

## Epic 003. El día uno, dictado

El mismo día uno del epic 002, dictado en lenguaje natural en vez de invocado a mano. El agente compila el dictado en llamadas `tuku` en vez de escribir archivos, reproduciendo el vault del 002.

Replica, y nada más. Un turno, un dictado, el mismo vault de salida. La conversación de ida y vuelta es el epic 004, y meterla acá haría que un fallo pudiera venir de dos sitios a la vez.

- **Entregable:** el `AGENTS.md` del vault que hace que cualquier arnés opere igual ([`../spec/despacho.md`](../spec/despacho.md)), la evidencia de que con él un agente vivo reproduce el día uno, y **el método para probarlo**. El arnés no es andamiaje de este epic: es lo que permite que el 004 y los siguientes afirmen algo sobre un agente en vez de mirarlo funcionar, y un método frágil no da un resultado dudoso, da uno falso.
- **Detalle completo:** [`../tests/escenarios/003-00-el-dia-uno-dictado.md`](../tests/escenarios/003-00-el-dia-uno-dictado.md).

> [!tip] Mirar en VAULT al cerrar el epic
> - [`VAULT/agentes.md`](VAULT/agentes.md), sección "Motores": lista de arneses validados y umbral de referencia por modelo. El brief sacó esa lista y dejó un `#REVISAR` pidiendo destino; este epic es el momento de moverla a [`entorno-devel.md`](entorno-devel.md) o a [`spec/agente.md`](../spec/agente.md).
> - [`VAULT/agentes.md`](VAULT/agentes.md), sección "Economía de contexto": contexto pertinente, sesión nueva tras una hora de inactividad y degradación entre 100 y 300 reglas. Sirve para medir el piso de la cascada de `AGENTS.md` (ver [`TODO.md`](../TODO.md)).
> - [`VAULT/scratchpad/Comportamiento esperado de TUKU.md`](VAULT/scratchpad/Comportamiento%20esperado%20de%20TUKU.md): Hermes necesita configuración base (SOUL, lectura de `AGENTS.md`) que debe sembrar `tuku init`.

## Epic 004. La conversación

El autor deja de dictar y conversa: el agente delibera, pregunta, cambia de rumbo a media sesión y solo al final ejecuta. Es donde los `AGENTS.md` del vault se refinan contra fricción real, y donde se construye el conductor que sostiene una sesión de varios turnos con un adaptador por arnés.

Se prueba con dos agentes, uno del lado del autor y otro del lado de TUKU. No agrega fixture: sigue siendo el día uno.

- **Entregable:** conductor de sesión multi-turno reutilizable, límites del vault verificables como diff vacío, y los `AGENTS.md` corregidos por lo que la conversación rompa.
- **Criterio de salida:** una conversación en que el autor se contradice y rectifica deja el vault en el estado que pidió al final, y ninguna prohibición de la tabla de límites se rompe en el camino.

> [!tip] Mirar en VAULT al construir el conductor
> - [`VAULT/research/Configuraciones de Tools.md`](VAULT/research/Configuraciones%20de%20Tools.md), sección "Hermes": perfiles paralelos, un gateway por perfil, y el API Server con `conversation` fijo para sostener una misma sesión entre llamadas. Es un adaptador ya probado a mano.
> - [`VAULT/old/decisiones/0018-hermes-subproceso-por-perfil.md`](VAULT/old/decisiones/0018-hermes-subproceso-por-perfil.md): aislamiento de estado por perfil con `HERMES_HOME`.
> - [`VAULT/agentes.md`](VAULT/agentes.md), sección "Modelos del autor": la voz solo se destila de lo que el autor le dice al agente, no de la bitácora. Obliga a que el historial conversacional persista en Markdown; conviene decidirlo aquí, porque desde este epic hay conversaciones que guardar.

## Epic 005. El día ciento cincuenta

Lo mismo del epic 002 sobre un vault que ya tiene meses encima con activo acumulado (ámbitos poblados, notas escritas, historial de pendientes). Segunda vuelta de capacidades donde aparecen enlaces automáticos desde el primer día, autoasignación de pendientes, notas con "Ver además" y versiones completas de ámbitos y destilados. Cubre fases 3 y 5 completas, y resto de la 4.

- **Criterio de salida:** inyectar un ciclo de `mac-jpgil` sobre un vault poblado produce registros con su ámbito, enlazados a las notas que `tuku context` ofrece, y notas tejidas, sin intervención del autor.

> [!tip] Mirar en VAULT al abrir el epic
> - [`VAULT/scratchpad/tuku-docs/corpus-regresion/contrato-de-regeneracion.md`](VAULT/scratchpad/tuku-docs/corpus-regresion/contrato-de-regeneracion.md): tabla de artefactos con su criterio de igualdad (idéntico si lo produce un proceso determinista, equivalente si lo redacta un agente). Es la base para convertir el principio 9 en un test sobre un vault poblado.
> - [`VAULT/spec/notas.md`](VAULT/spec/notas.md): las tres clases de nota (libre, de estructura, de inducción) y la pregunta que decide el "Ver además": ¿la página se revisita y se cura, o se escribe una vez?
> - [`VAULT/spec/entidades.md`](VAULT/spec/entidades.md): prácticas heredadas por tipo, y el patrón de proponer una página en blanco cuando un nombre se repite.

## Epic 006. Abrir y cerrar el ciclo

Que un ciclo se abra y se cierre sin perder nada, y que lo propuesto al abrirlo valga la pena leerlo. Las cadencias entran acá porque emiten en la apertura del ciclo. Cubre fases 6 y 7, más lo restante de la 4. La mecánica determinista (abrir, promover pendientes, aplanar transclusiones, archivar ciclos, ramas de ámbitos y notas) se prueba con archivos inyectados antes de conectar el LLM para plan y resumen.

- **Criterio de salida:** abrir dos veces no duplica; cerrar dos veces no vuelve a mover; prueba que falla a propósito si se aplana antes del resumen. Plan calcula capacidad contra lo declarado.

> [!tip] Mirar en VAULT al diseñar cadencias y cierre
> - [`VAULT/spec/cadencias.md`](VAULT/spec/cadencias.md): los cinco disparadores, en particular la cadencia por ausencia de actividad ("un cliente sin contacto hace cuatro semanas"), la más valiosa y la única que ningún cuaderno tiene. Y "el reporte es la memoria": lo que se conserva de un período largo es su relato.
> - [`VAULT/old/decisiones/0006-regla-muere-emitido-sobrevive.md`](VAULT/old/decisiones/0006-regla-muere-emitido-sobrevive.md): al borrar una cadencia o su ámbito, lo ya emitido sobrevive y la referencia colgante no es error. Verificar que [`spec/cadencias.md`](../spec/cadencias.md) lo diga.
> - [`VAULT/old/decisiones/0010-friccion-no-se-declara.md`](VAULT/old/decisiones/0010-friccion-no-se-declara.md): la fricción no se etiqueta al escribir, se descubre en el cierre contrastando plan y actividad. Evidencia: 59 hitos, 22 decisiones y 0 fricciones en 8 ciclos reales. Útil para el resumen del cierre.
> - [`VAULT/old/decisiones/0007-plan-es-calendario.md`](VAULT/old/decisiones/0007-plan-es-calendario.md) y [`VAULT/spec/old/artefactos-ciclo.md`](VAULT/spec/old/artefactos-ciclo.md): plan y reporte del ciclo en el modelo anterior.

## Epic 007. Que note lo que nadie pidió

El agente deja de responder y empieza a observar: infiere ámbitos y notas tipadas desde el histórico, detecta recurrencias que nadie declaró como cadencia y propone sin ejecutar. Cubre fase 9.

- **Criterio de salida:** la prueba dura es negativa: rechazar una propuesta no deja rastro en ninguna primitiva (principio 3).

> [!tip] Mirar en VAULT al diseñar la inferencia
> - [`VAULT/agentes.md`](VAULT/agentes.md), "Autonomía calibrada": medir la tasa de aceptación y corrección de las propuestas pasadas, por tipo de entidad, en un archivo que el autor pueda leer y editar (aceptable que el agente cree solo la página de un proyecto, no la de una persona).
> - [`VAULT/agentes.md`](VAULT/agentes.md), "El agente silencioso": un proceso de fondo con silencio absoluto (`[SILENT]`) salvo que la conclusión madure y aporte valor.
> - [`VAULT/spec/entidades.md`](VAULT/spec/entidades.md): "sembrar y corregir" y nunca decirle "entidad" al autor.
> - [`VAULT/spec/corpus.md`](VAULT/spec/corpus.md), "Autoría y procedencia": toda inferencia externa lleva modelo y fecha, y la marca se reclasifica cuando el autor edita a mano.

## Epic 008. MAINTENANCE MODE

Tests del modo de mantenimiento: un prompt que empieza con `MAINTENANCE MODE` en mayúsculas no carga nada extra y sigue las instrucciones directas, y cualquier otro es una interacción natural con el autor ([`../spec/despacho.md`](../spec/despacho.md)). Sin detalles aún; se define cuando el `AGENTS.md` del vault diga el modo.

## Wishlist

Lo que hay que hacer y no bloquea a nadie vive en [`TODO.md`](../TODO.md).

> [!tip] Mirar en VAULT para lo que ya tiene investigación
> - Publicación web con Quartz: [`VAULT/research/Herramientas para TUKU.md`](VAULT/research/Herramientas%20para%20TUKU.md) y [`VAULT/research/Configuraciones de Tools.md`](VAULT/research/Configuraciones%20de%20Tools.md) (ocultar carpetas con prefijo, vault como submódulo de git).
> - Captura móvil por Telegram: la misma nota, sección "Gateway con API y Telegram" (variables, allowlist y un bot token por perfil).
> - Transclusión editable en Obsidian: [`VAULT/research/obsidian_notes.md`](VAULT/research/obsidian_notes.md). Es una prueba de concepto frágil; sirve para saber qué no apoyar encima.
> - Sincronización entre máquinas: [`VAULT/scratchpad/tuku-docs/decisiones/0001-fuente-de-verdad-y-sincronizacion.md`](VAULT/scratchpad/tuku-docs/decisiones/0001-fuente-de-verdad-y-sincronizacion.md). Git manda y se asume un único escritor concurrente.

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
