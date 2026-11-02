# Plan de desarrollo de TUKU: Epics y Fases

> Única fuente de verdad de alto nivel sobre cómo se construye TUKU. Los epics son la unidad de entrega (cortan por estado del vault); las fases son el corte técnico interno por primitiva. Si un documento entra en contradicción con este, manda este archivo.

## Los epics mueven el diseño

El diseño lo dirige la experimentación, no al revés: el [libro de estilo](../template/vanilla/LIBRO-DE-ESTILO.md), [`spec/tuku.md`](../spec/tuku.md) y [`docs/`](../docs/README.md) cambian por efecto de los epics. Cada epic entrega dos cosas: su producto y lo que le enseñó al diseño. El libro manda sobre los comandos y `spec/tuku.md` sobre su código; el experimento manda sobre los dos.

El orden de trabajo es siempre el mismo:
1. **De lo determinista a lo agéntico:** un tramo determinista corre mil veces gratis; uno agéntico cuesta tokens y no repite resultado. El escenario con LLM va al final, nunca en la base de una cadena.
2. **De lo simple a lo complejo:** una primitiva antes que la combinación, un ámbito antes que un árbol, el mínimo de registros antes que el volumen con ruido.
3. **Del caso feliz al caso borde.**

Un epic se abre escribiendo dos cosas a la vez, antes de implementar nada: sus escenarios en [`tests/escenarios/`](../tests/escenarios/README.md) y su capítulo del [tutorial](../docs/tutorial/README.md). Los escenarios dicen qué se verifica; el capítulo dice qué se le promete a quien va a usarlo, y esa promesa es la que guía el epic. Así se abrió el 003, y el capítulo sirve además de prueba a mano mientras los escenarios agénticos todavía no corren.

## Epics y Fases: dos cortes perpendiculares

Las fases cortan **por primitiva** (registro, pendientes, ámbitos, cadencias, notas); los epics cortan **por el estado inicial del vault**. El motivo es el criterio de entrega: "los pendientes funcionan" no es una experiencia que alguien pueda usar; "el día uno funciona" sí lo es.

Un epic puede abarcar varias fases (el 002 hace la versión mínima de las fases 3 y 5, y el 005 las completa contra un vault poblado), fundir una fase con LLM y una sin él (el 006 junta la 4 y la 7), o una fase puede partirse entre varios epics (la fase 1 la construye el 002 a mano, el 003 dictada y el 004 conversada).

| Fase | Nombre | Qué se puede hacer al terminarla | LLM | Fixture | Epic |
| --- | --- | --- | --- | --- | --- |
| 0 | El vault que se puede abrir | Empezar a escribir a mano | no | `vacio` | 001 |
| 1 | El registro | Dictar y que quede bien escrito | parcial | `primer-dia` | 002 a mano, 003 dictado, 004 conversado |
| 2 | Pendientes | Que no se olvide nada | no | `poblado` | 002 |
| 3 | El árbol de ámbitos | Que cada cosa tenga su lugar | no | `poblado` | 002 mínimo, 005 completo |
| 4 | Cadencias | Que el sistema recuerde solo | no | `poblado` | 006 |
| 5 | Notas y enlaces | Que el tejido se mantenga | no | `poblado` | 002 mínimo, 005 completo |
| 6 | La ventana | `AHORA.md` muestra lo reciente y se archiva solo en `bitacoras/` | no | `poblado` | 005 |
| 7 | Foco y resumen | Que lo que se propone para la semana valga la pena leerlo | sí | `poblado` | 006 |
| 9 | Inferencia semántica | Que note cosas que nadie pidió | sí | `historico` | 007 |

La numeración salta la fase 8 porque el endurecimiento pasó a la Wishlist: no agrega capacidades, cierra huecos.

### Criterios transversales

- **Entregable solo:** cada fase deja algo usable para no quedar con un sistema a medio construir.
- **Un fixture nuevo por vez:** si necesita dos estados iniciales nuevos, está haciendo dos cosas.
- **El LLM se aísla:** las fases 1, 7 y 9 lo usan y las demás no.
- **Idempotencia:** correr cualquier operación dos veces da el mismo resultado (principio 9).
- **La ayuda como equivalente manual:** ningún comando entra sin una descripción que diga qué archivos toca y cómo, para garantizar el principio 1.
- **Contrato de [`spec/cli.md`](VAULT/spec-anterior/cli.md):** códigos de salida fijos, mensajes que nombran defecto y corrección, y ante la duda informar sin escribir.

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
| `poblado` | dos semanas de uso, la primera ya en `bitacoras/`, pendientes en escalones | casi todo el tejido y la ventana de `AHORA.md` (Epic 005), las cadencias y el foco (Epic 006) |
| `historico` | varias semanas en `bitacoras/` | enlaces antiguos e inferencia (Epic 007) |

### Superficie del CLI

Todo epic que añada comandos fija su superficie en un escenario propio: `tuku -h` nombra los nouns, cada subcomando nombra sus argumentos y opciones, ningún código de salida se pisa y todo error nombra defecto y corrección.

## Estado de los Epics

Actualizado el 2026-11-02.

| Epic | Nombre | Estado inicial | Estado | Qué falta para cerrarlo |
| --- | --- | --- | --- | --- |
| 001 | Un TUKU mínimo instalable | `vacio` | cerrado | reescrito y cerrado el 2026-11-03 para `AHORA.md` sin ciclos; seis escenarios en verde (`001-01` instala de verdad y va marcado `red`) |
| 002 | El día uno, a mano | `vacio` → `primer-dia` | cerrado | reescrito y cerrado el 2026-11-03; doce escenarios deterministas en verde (diez en `002-13`, dos en `002-14`) y el recorrido entero ejecutado a mano en un vault aparte |
| 003 | El día uno, dictado | `vacio` → `primer-dia` | cerrado | cerrado el 2026-11-02 por decisión del autor; cinco escenarios: `003-01` determinista; `003-10`, el día uno entero en un turno (fundió del `003-02` al `003-07` el 2026-10-16), y `003-11`, el día dicho por su nombre («el viernes pasado»), reescrito para `AHORA.md` sin ciclos y sin volver a correr con agente; `003-08` (`hermes`) y `003-09` (`claude`) en verde el 2026-09-20, sin repetir desde entonces. Sin la revisión a mano de `playground/003-*/` |
| 004 | La conversación | `primer-dia` | cerrado | cerrado el 2026-11-02 por decisión del autor; cinco escenarios agénticos (`004-01` a `004-05`) con el conductor [`conversacion.py`](../tests/scripts/conversacion.py), en verde el 2026-10-20; el vault de partida (`004-00`) se reescribió para `AHORA.md` sin ciclos y es determinista. Sin la revisión a mano de `playground/004-*` |
| 005 | El día ciento cincuenta | `poblado` | escenarios reescritos | ocho documentos en `tests/escenarios/005-*` rehechos para `AHORA.md` sin ciclos el 2026-11-03: 34 tests deterministas en verde y 7 agénticos sin volver a correr. Solo queda abierto B4 de la tabla de `005-00` (bajar un pendiente por la escalera de horizontes), que está en `TODO.md` |
| 006 | Lo que vuelve solo | `poblado` | sin empezar | el diseño de las cadencias sin apertura de ciclo, sus escenarios y su capítulo del tutorial |
| 007 | Que note lo que nadie pidió | `historico` | sin empezar | depende del epic 006 |
| 010 | El tutorial entero | `vacio` → `poblado` | en curso | el arnés `test-tui tutorial` ya corre los capítulos. En el último recorrido (anterior a `AHORA.md` sin ciclos) pasaron 1, 2, 3, 6 y 7; 4, 5 y 8 fallan por el modelo barato y el sandbox de `agy`, no por el texto. Los capítulos 1, 2, 3, 5, 8 y 10 se ajustaron y el 9 es nuevo (`09-pasar-de-semana.md`), sin recorrer todavía; el 10 promete lo del epic 007 |

## Epic 001. Un TUKU mínimo instalable

Que una persona nueva instale TUKU con un comando, siembre un vault en un directorio vacío y encuentre `AHORA.md` listo con su foco para escribir el mismo día, sin configurar nada y sin saber qué es TUKU. Cubre la fase 0.

- **Entregable:** `uv tool install git+https://github.com/pewma-ai/tuku.git@devel` deja `tuku` en PATH; `tuku init mi-vault` produce el estado cero sin tocar la red ni leer el reloj: `AHORA.md` con su foco y ningún día, `PENDIENTES.md` con su tabla vacía y `reglas/config.tuku.md` con `window_days` y `archive_weeks`.
- **Criterio de salida:** el árbol sembrado es idéntico a `template/vanilla/` salvo lo que `init` resuelve (`AHORA.md`, la configuración y el manual de comandos), un destino con contenido se rechaza salvo `--force`, `--author` deja el nombre en `reglas/autor.user.md` y `tuku doctor` da el vault por sano.
- **Detalle completo:** [`../tests/escenarios/001-00-un-tuku-minimo-instalable.md`](../tests/escenarios/001-00-un-tuku-minimo-instalable.md). Seis escenarios (`001-01` a `001-04`, `001-06` y `001-07`).

## Epic 002. El día uno, a mano

Alguien instala TUKU y vive sus primeras dos semanas sobre un vault recién sembrado, todo a mano con `tuku`: registra, promete pendientes, abre un ámbito con su jerarquía y escribe una nota. `AHORA.md` ordena los días del más nuevo al más viejo; al pasar al lunes que deja una semana fuera de la ventana, esa semana se archiva sola en `bitacoras/bitacora-AAAAMMDD-AAAAMMDD.md` (con `from` y `to`), y un registro de fecha antigua va a la bitácora que le toca. Cubre las fases 1 y 2 completas, y la versión mínima de las fases 3 y 5.

- **Entregable:** registros que caen en su día y orden, pendientes con `Creado` y su ventana de `AHORA.md`, ámbito con jerarquía, nota enlazada, foco del autor conservado, autoarchivado en bitácoras semanales y registros antiguos enrutados.
- **Criterio de salida:** la historia entera corre con el reloj inyectado (`TUKU_NOW`), cada paso sobre el vault del anterior y afirmando su `diff`; repetirla da `diff` vacío, `tuku regenerate` dice que todo estaba al día y `tuku doctor` dice que el vault está sano. Un derivado editado a mano se regenera idéntico y un pendiente abierto y cerrado a mano lo repara `tuku fix todo`. Las reglas deterministas viven en unitarios.
- **Detalle completo:** [`../tests/escenarios/002-00-el-dia-uno-a-mano.md`](../tests/escenarios/002-00-el-dia-uno-a-mano.md). El día en cadena en [`002-13`](../tests/escenarios/002-13-el-dia.md) y sus reparaciones a mano en [`002-14`](../tests/escenarios/002-14-casos-borde.md). Se salda el principio 9 mediante `tuku regenerate`.

## Epic 003. El día uno, dictado

El mismo día uno del epic 002, dictado en lenguaje natural en vez de invocado a mano. El agente compila el dictado en llamadas `tuku` en vez de escribir archivos, reproduciendo el vault del 002.

Replica, y nada más. Un turno, un dictado, el mismo vault de salida. La conversación de ida y vuelta es el epic 004, y meterla acá haría que un fallo pudiera venir de dos sitios a la vez.

- **Entregable:** el `AGENTS.md` del vault (invocación y límites) con la skill del asistente y el libro de estilo por capítulos, que hacen que cualquier arnés opere igual ([`VAULT/spec-anterior/despacho.md`](VAULT/spec-anterior/despacho.md)), la evidencia de que con él un agente vivo reproduce el día uno, y **el método para probarlo**. El arnés no es andamiaje de este epic: es lo que permite que el 004 y los siguientes afirmen algo sobre un agente en vez de mirarlo funcionar, y un método frágil no da un resultado dudoso, da uno falso.
- **Detalle completo:** [`../tests/escenarios/003-00-el-dia-uno-dictado.md`](../tests/escenarios/003-00-el-dia-uno-dictado.md).

> [!tip] Mirar en VAULT al cerrar el epic
> - [`VAULT/agentes.md`](VAULT/agentes.md), sección "Motores": lista de arneses validados y umbral de referencia por modelo. El brief sacó esa lista y dejó un `#REVISAR` pidiendo destino; este epic es el momento de moverla a [`entorno-devel.md`](entorno-devel.md) o a [`spec/agente.md`](VAULT/spec-anterior/agente.md).
> - [`VAULT/agentes.md`](VAULT/agentes.md), sección "Economía de contexto": contexto pertinente, sesión nueva tras una hora de inactividad y degradación entre 100 y 300 reglas. Sirve para medir el piso de la cascada de `AGENTS.md` (ver [`TODO.md`](../TODO.md)).
> - [`VAULT/scratchpad/Comportamiento esperado de TUKU.md`](VAULT/scratchpad/Comportamiento%20esperado%20de%20TUKU.md): Hermes necesita configuración base (SOUL, lectura de `AGENTS.md`) que debe sembrar `tuku init`.

## Epic 004. La conversación

El autor deja de dictar y conversa: el agente delibera, pregunta, cambia de rumbo a media sesión y solo al final ejecuta. Es donde los `AGENTS.md` del vault se refinan contra fricción real, y donde se construye el conductor que sostiene una sesión de varios turnos con un adaptador por arnés.

Se prueba con dos agentes, uno del lado del autor y otro del lado de TUKU. No agrega fixture: sigue siendo el día uno, con el vault de partida armado a mano por el `004-00` bajo un reloj fijado (`export TUKU_NOW`).

- **Entregable:** conductor de sesión multi-turno reutilizable, límites del vault verificables como diff vacío, y el `AGENTS.md`, la skill y el libro corregidos por lo que la conversación rompa.
- **Criterio de salida:** una conversación en que el autor se contradice y rectifica deja el vault en el estado que pidió al final, y ninguna prohibición de la tabla de límites se rompe en el camino.

> [!tip] Mirar en VAULT al construir el conductor
> - [`VAULT/research/Configuraciones de Tools.md`](VAULT/research/Configuraciones%20de%20Tools.md), sección "Hermes": perfiles paralelos, un gateway por perfil, y el API Server con `conversation` fijo para sostener una misma sesión entre llamadas. Es un adaptador ya probado a mano.
> - [`VAULT/old/decisiones/0018-hermes-subproceso-por-perfil.md`](VAULT/old/decisiones/0018-hermes-subproceso-por-perfil.md): aislamiento de estado por perfil con `HERMES_HOME`.
> - [`VAULT/agentes.md`](VAULT/agentes.md), sección "Modelos del autor": la voz solo se destila de lo que el autor le dice al agente, no de la bitácora. Obliga a que el historial conversacional persista en Markdown; conviene decidirlo aquí, porque desde este epic hay conversaciones que guardar.

## Epic 005. El día ciento cincuenta

Lo mismo del epic 002 sobre un vault que ya tiene meses encima con activo acumulado (ámbitos poblados, notas escritas, historial de pendientes y una bitácora semanal archivada sola). Segunda vuelta de capacidades donde aparecen las notas con "Ver además" que el agente enlaza desde el primer día a partir de `tuku context`, los pendientes asignados a su ámbito y las versiones completas de los ámbitos. Cubre fases 3 y 5 completas, y la 6: la ventana de `AHORA.md` que conserva dos semanas y el lunes en que la primera pasa a `bitacoras/` sin que nadie lo pida. Los horizontes vencidos se calculan desde `Creado` y `tuku context todo --late` los informa. Las cadencias van en el 006 y los destilados en el 007 (fase 9).

- **Criterio de salida:** inyectar las dos semanas de la Pyme con el reloj fijado deja el vault sano: registros con su ámbito, enlazados a las notas que `tuku context` ofrece, notas tejidas, la primera semana en `bitacoras/` y los atrasados informados, sin intervención del autor.
- **Detalle completo:** [`../tests/escenarios/005-00-el-dia-ciento-cincuenta.md`](../tests/escenarios/005-00-el-dia-ciento-cincuenta.md).

> [!tip] Mirar en VAULT al abrir el epic
> - [`VAULT/scratchpad/tuku-docs/corpus-regresion/contrato-de-regeneracion.md`](VAULT/scratchpad/tuku-docs/corpus-regresion/contrato-de-regeneracion.md): tabla de artefactos con su criterio de igualdad (idéntico si lo produce un proceso determinista, equivalente si lo redacta un agente). Es la base para convertir el principio 9 en un test sobre un vault poblado.
> - [`VAULT/spec/notas.md`](VAULT/spec/notas.md): las tres clases de nota (libre, de estructura, de inducción) y la pregunta que decide el "Ver además": ¿la página se revisita y se cura, o se escribe una vez?
> - [`VAULT/spec/entidades.md`](VAULT/spec/entidades.md): prácticas heredadas por tipo, y el patrón de proponer una página en blanco cuando un nombre se repite.

## Epic 006. Lo que vuelve solo

Que lo que el autor declaró una vez vuelva sin que lo pida, y que lo propuesto para la semana valga la pena leerlo. Ya no hay un ciclo que abrir ni cerrar: `AHORA.md` se archiva solo (epic 005) y lo que falta es lo que se emite. Cubre la fase 4 y la 7.

- **Cadencias.** Un `CADENCIAS.md` emite un pendiente con fecha por cada vez que la regla cae en la ventana de `AHORA.md` (`window_days`). No hay apertura que lo dispare: lo evalúa el primer comando que escribe, como el archivado, y emitir es idempotente (dos pasadas no duplican). El diseño decide qué hace con una cadencia de día exacto que cae fuera de la ventana, y con las que emiten algo distinto de un pendiente (el foco, la revisión de la semana, que siembra [`ambitos/CADENCIAS.md`](../template/vanilla/ambitos/CADENCIAS.md)).
- **Capacidad.** El plan de la ventana se calcula contra lo declarado en `ambitos/personal/CAPACIDAD.md`; la traducción de «el próximo turno» a un `--due` la hace el agente con ese ritmo ([`TODO.md`](../TODO.md), «Pendientes que no son una ventana de días»).
- **Foco y resumen (con LLM).** El foco de `AHORA.md` lo escribe solo el autor. El agente puede proponerlo leyendo la ventana, los atrasados y la bitácora recién archivada, y también un resumen de la semana que salió; ambos esperan el sí del autor, y TUKU no escribe ninguno por su cuenta.
- **Criterio de salida:** emitir dos veces no duplica; borrar una cadencia o su ámbito deja lo ya emitido; el foco no cambia sin el sí del autor; una propuesta rechazada no deja rastro (principio 3). Se abre, como todo epic, escribiendo sus escenarios y su capítulo del tutorial.
- **Ya resuelto.** Un pendiente cuyo horizonte pasó se marca atrasado y no se mueve de escalón: lo calcula `tuku context todo --late` desde `Creado` ([`005-04`](../tests/escenarios/005-04-los-atrasados-se-calculan.md)), y el autor decide si lo posterga.

> [!tip] Mirar en VAULT al diseñar cadencias y foco
> - [`VAULT/spec/cadencias.md`](VAULT/spec/cadencias.md): los cinco disparadores, en particular la cadencia por ausencia de actividad ("un cliente sin contacto hace cuatro semanas"), la más valiosa y la única que ningún cuaderno tiene. Y "el reporte es la memoria": lo que se conserva de un período largo es su relato.
> - [`VAULT/old/decisiones/0006-regla-muere-emitido-sobrevive.md`](VAULT/old/decisiones/0006-regla-muere-emitido-sobrevive.md): al borrar una cadencia o su ámbito, lo ya emitido sobrevive y la referencia colgante no es error. Verificar que [`spec/cadencias.md`](borradores/cadencias.md) lo diga.
> - [`VAULT/old/decisiones/0010-friccion-no-se-declara.md`](VAULT/old/decisiones/0010-friccion-no-se-declara.md): la fricción no se etiqueta al escribir, se descubre en el cierre contrastando plan y actividad. Evidencia: 59 hitos, 22 decisiones y 0 fricciones en 8 ciclos reales. Útil para el resumen del cierre.
> - [`VAULT/old/decisiones/0007-plan-es-calendario.md`](VAULT/old/decisiones/0007-plan-es-calendario.md) y [`VAULT/spec/old/artefactos-ciclo.md`](VAULT/spec/old/artefactos-ciclo.md): plan y reporte del ciclo en el modelo anterior.

## Epic 007. Que note lo que nadie pidió

El agente deja de responder y empieza a observar: infiere ámbitos y notas tipadas desde el histórico (las bitácoras semanales de `bitacoras/`, con sus enlaces a los ámbitos), detecta recurrencias que nadie declaró como cadencia y propone sin ejecutar. Cubre fase 9; parte del estado `historico` y sigue al epic 006 por las cadencias que propone.

- **Criterio de salida:** la prueba dura es negativa: rechazar una propuesta no deja rastro en ninguna primitiva (principio 3).

> [!tip] Mirar en VAULT al diseñar la inferencia
> - [`VAULT/agentes.md`](VAULT/agentes.md), "Autonomía calibrada": medir la tasa de aceptación y corrección de las propuestas pasadas, por tipo de entidad, en un archivo que el autor pueda leer y editar (aceptable que el agente cree solo la página de un proyecto, no la de una persona).
> - [`VAULT/agentes.md`](VAULT/agentes.md), "El agente silencioso": un proceso de fondo con silencio absoluto (`[SILENT]`) salvo que la conclusión madure y aporte valor.
> - [`VAULT/spec/entidades.md`](VAULT/spec/entidades.md): "sembrar y corregir" y nunca decirle "entidad" al autor.
> - [`VAULT/spec/corpus.md`](VAULT/spec/corpus.md), "Autoría y procedencia": toda inferencia externa lleva modelo y fecha, y la marca se reclasifica cuando el autor edita a mano.

## Epic 010. El tutorial entero

Que alguien pueda seguir el [tutorial](../docs/tutorial/README.md) de principio a fin sobre un vault vacío y que cada paso haga lo que el capítulo dice. El tutorial es la promesa a quien va a usar TUKU; este epic es la prueba de que se cumple, y marca qué capítulos faltan construir: hoy solo el 10, que promete lo del epic 007.

- **Los pasos no se copian.** Cada capítulo es un escenario (`010-NN`, con `NN` el número del capítulo). Su fuente es el capítulo: los bloques `> [!tip]` son lo que el autor dicta, tal cual y en orden, y los `> [!check]` son lo que se afirma después de cada paso. Los escenarios solo nombran el capítulo y su estado inicial; si el tutorial cambia, la prueba cambia con él.
- **Qué se verifica sin leer:** las invariantes de siempre en cada paso (cada cambio del vault tiene su comando `tuku`, el agente no sale del vault, `tuku doctor` sano). Cada `check` se juzga contra el delta del vault del paso; lo que ningún archivo muestra, como la pregunta del agente, lo juzga quien lee.
- **Entregable:** el arnés que extrae pasos y `check` de un capítulo y los corre con `test-tui`, y la corrida completa en cadena de los diez capítulos, con el vault de cada uno archivado en `playground/`.
- **Los relojes:** cada capítulo corre con su `TUKU_NOW` (`tests/scripts/tutorial.py`), y un paso titulado «el lunes» salta al lunes siguiente. El capítulo 9 usa dos lunes (el 24 y el 31) para que la semana del 17 salga de la ventana y se archive sola.
- **Criterio de salida:** los diez capítulos en verde con un agente real sobre un vault que parte del `tuku init` del capítulo 1.
- **Detalle completo:** [`../tests/escenarios/010-00-el-tutorial.md`](../tests/escenarios/010-00-el-tutorial.md).

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
