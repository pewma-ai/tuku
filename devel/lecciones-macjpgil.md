# Lecciones de mac-jpgil

> Qué resolvió ya el vault real del autor, y qué de eso sirve para el epic en curso. No es una especificación ni un inventario: [`epics.md`](epics.md) manda que el material se traiga **epic por epic, nunca por adelantado**, así que esto separa lo que el epic 002 puede usar hoy de lo que solo se anota para no perderlo.
>
> **Este repositorio manda.** `mac-jpgil` es lo que le funcionó al autor, y TUKU es el rediseño deliberado de eso, así que donde los dos difieren no hay contradicción que arbitrar: vale [`../spec/`](../spec/README.md). Lo de acá son lecciones y nada más. Una diferencia observada solo mueve la spec por el camino que ya define `epics.md`, cuando el experimento del epic la obliga, nunca porque el vault real lo haga distinto.

Levantado el 2026-09-06, contra [`../../mac-jpgil`](../../mac-jpgil) en su estado de ese día.

## De qué tamaño es la evidencia

2266 commits desde el 2026-03-18, 23 bitácoras de ciclo, 249 notas (38 de ellas de persona), 42 entidades vigentes en `org/` y 7 archivadas. Son casi seis meses de uso diario y no de un piloto, así que donde una regla está escrita tres veces en tres archivos distintos, lo razonable es leerlo como que se rompía tres veces.

Lo que se miró: `AGENTS.md` de la raíz y los locales de `actividad/`, `notas/` y `org/`; los procesos de `procesos/` que tocan registro, pendientes, ámbitos y notas; los comandos de `procesos/scripts/`; `org/_rules/`; y cuatro bitácoras reales de agosto y septiembre de 2026.

## Lo que aplica al epic 002

### 1. El registro real no lleva hora

`spec/bitacora.md` fija `- HH:MM - [[ambito]] ~~(Hecho)~~ **clasificacion**: cuerpo`. En las cuatro bitácoras revisadas, sobre 235 registros, prácticamente ninguna empieza con hora. La hora aparece **dentro del cuerpo** cuando el hecho la necesita ("Reunión con [una persona] (11:30) sobre gobernanza del grupo"), y en ningún otro caso.

`actividad/AGENTS.md` lo tiene resuelto de la única forma que se sostiene: orden estrictamente cronológico por hora del evento, y si no hay timestamp explícito, el registro se agrega al final del día sin reordenar nada de lo ya escrito.

La spec manda y `- HH:MM -` sigue siendo el formato. Lo que esto aporta es un riesgo conocido para el experimento del epic: si el dictado real llega sin hora, la única hora que el comando puede estampar es la de escritura y no la del hecho, que es información distinta. Si eso aparece en el epic, cambia [`../spec/bitacora.md`](../spec/bitacora.md) por el camino que `epics.md` ya define, y si no aparece, no cambia nada. La regla de inserción de mac-jpgil (sin timestamp, al final del día, sin reordenar) sirve como respuesta ya probada para ese caso.

### 2. La marca de cierre va antes del ámbito, no después

Real (con los identificadores de trabajo cambiados): `- ~~(Hecho)~~ [un-ambito](path): limpieza de tickets pendientes realizada durante la mañana.`

Spec: la marca de la ontología cerrada va después del ámbito, y eso es lo que vale.

Se anota porque el orden de mac-jpgil es el que el autor tiene incorporado de tanto leerlo, así que es el error de dictado y de redacción más probable del epic. Sirve como caso del linter, no como propuesta de cambio.

### 3. Los enlaces reales son Markdown relativo, no wikilinks

mac-jpgil escribe `[Nombre Apellido](../notas/Nombre%20Apellido%20-%20NAP.md)` y tiene un comando dedicado (`jntr.obsidian-links-to-markdown.py`, con umbral de madurez de 5 minutos para no pisar lo que el autor está escribiendo) que convierte `[[...]]` a Markdown estándar. El motivo es de portabilidad: publicación web y lectura en GitHub, donde el wikilink no resuelve.

TUKU usa `[[ambito]]` y se queda con `[[ambito]]`. Lo que la lección aporta es que la forma del enlace es una decisión de publicación con costo diferido, y que la conversión ya está resuelta en una dirección si algún día se necesita. Deuda conocida, no descubrimiento pendiente.

### 4. La invariante de `~~(Hecho)~~` es el caso negativo más importante

Está escrita tres veces: en `actividad/AGENTS.md` (reglas y tabla de límites), en `pendientes-en-bitacora.MaC.md` como invariante formal, y en `tareas-pendientes.MaC.md` como límite. Dice siempre lo mismo: `~~(Hecho)~~` se genera si y solo si corresponde a un pendiente que **ya estaba registrado**. Una acción que ocurrió pero que nunca fue pendiente se registra como registro narrativo normal.

Que esté tres veces indica que el agente la rompía: convertía cualquier "ya hice X" en un cierre. En TUKU eso deja el sistema en un estado peor que en mac-jpgil, porque `PENDIENTES.md` es fuente de verdad y un cierre sin pareja no tiene qué borrar.

El epic 002 necesita el test negativo: un dictado de algo hecho que nunca fue pendiente no produce marca de cierre, y un `~~(Hecho)~~` que no empareja se **reporta**, nunca se rechaza ni se inventa el pendiente que falta.

### 5. El costo de no tener fuente única, medido

En mac-jpgil el mismo pendiente vive hasta en tres lugares: el callout del día, la caja semanal y el callout de la entidad en `org/`. Todo `tareas-pendientes.MaC.md` existe para conciliarlos, incluida una regla de desempate escrita a mano ("el estado de cierre manda: si hay una aparición abierta y otra resuelta, se eliminan todas las demás") y un comando de verificación (`--mode=verify-task`) que responde si una tarea quedó abierta en algún punto de seguimiento.

TUKU ya eligió lo contrario, así que esto no rediseña nada. Lo que sí se rescata es el comando: **la pregunta "¿este pendiente quedó abierto en algún lado?" sobrevive a la fuente única**, porque con transclusiones el pendiente sigue apareciendo en más de un archivo aunque solo se escriba en uno. Es literalmente el assert de cierre del epic 002.

### 6. Los horizontes reales del autor no son semanas, y conviven con fechas

En la bitácora del 11 de agosto los pendientes están etiquetados `(próximo turno)`, `(siguiente turno)`, `(próximo descanso)`, `(este turno)` y también `(15 sep)`, `(1 nov 2026)`, todos en la misma caja. Confirma dos decisiones de `spec/pendientes.md` que estaban tomadas sin evidencia: que los tres horizontes del medio son vocabulario del autor y se renombran de verdad, y que horizontes con nombre y fechas absolutas conviven.

Confirma una tercera, más fina: la caja "Postergados" **se crea cuando llega la primera tarea diferida** y no al abrir el ciclo (regla anotada por el autor el 2026-08-13). Es la misma distinción entre callouts permanentes y callouts efímeros, encontrada de forma independiente.

### 7. Fechar es mover, y la unicidad ya está escrita como prohibición

La tabla de `classify` en `tareas-pendientes.MaC.md` reparte por propiedades de la tarea, y cierra con un caso prohibido explícito: escribir una tarea fechada en el callout del día **y** en la caja semanal. El callout del día reemplaza el registro de la caja.

Es la regla 1 de `spec/pendientes.md` (un pendiente en un solo callout) escrita como error observado. El punto 3 del epic 002 ("escribir en un día actual o futuro fecha el pendiente") tiene que probar que fecha moviendo y no copiando.

### 8. Crear un ámbito no es crear un archivo

`org/_rules/alta-entidades.md` describe el alta de un proyecto en siete pasos, y solo el primero es crear el archivo. Los otros seis: fijar `tipo` en el frontmatter, enlazarlo desde el área padre en los dos sentidos, registrar el alta en la bitácora del ciclo en curso, registrarla en el log de largo plazo, y **poblar historial** revisando tres meses de bitácoras para destilar lo relevante a la entidad nueva.

Para el epic 002 esto no se trae entero, y es correcto que no: sobre un vault vacío no hay historia que barrer, y el epic declara la versión mínima. Lo que sí se trae es que el alta deja constancia en la bitácora (el paso 5), porque eso sí ocurre el día uno y es la misma exigencia que el punto 5 del epic le pone a la nota.

El paso 7 es del epic 004, y ahí conviene contrastarlo con `spec/ambitos.md`, que hoy limita el enlazado retroactivo a `AHORA.md` y deja enriquecer el pasado como operación deliberada del autor. Los dos son compatibles si se lee que en mac-jpgil ese barrido ocurre porque el autor pidió el alta, que es exactamente la petición explícita que la spec exige.

### 9. El parentesco vive en el frontmatter, no en el árbol

En mac-jpgil el padre de una entidad es el campo `area:` de su frontmatter, y el dashboard de la ORG se **regenera** desde ahí con `jntr.org-frontpage-update.py`. En TUKU el parentesco es el árbol de directorios.

Lo aprovechable no es la elección sino su costo: `org/AGENTS.md` declara ese comando como "post-condición no negociable" tras cualquier escritura en `VIGENTES/`, con ejemplo del fallo incluido ("editar, responder al usuario, olvidar el comando"). Escribir "obligatorio" en mayúsculas es la señal de que se olvidaba igual. Ver la lección 11.

### 10. La nota a petición ya tiene arnés probado, y es aislamiento

`persona-note.MaC.md` establece que la creación o enriquecimiento de una nota **nunca corre en el contexto principal del chat**: se despacha a un subagente con contexto limpio, que barre cuatro semanas de bitácoras y `org/`, sintetiza, escribe y reporta una confirmación corta.

`spec/notas.md` de TUKU aísla solo el destilado (`jntr.nota-destilar`). La decisión 1 del epic 003 ("qué arnés de agente se usa y cómo se aísla para no gastar tokens por accidente") tiene acá una respuesta que ya lleva meses funcionando, con el matiz de que la nota del día uno es chica y probablemente no necesite el aislamiento todavía. Lo que sí conviene copiar desde ya es la forma del contrato: el subproceso devuelve una confirmación concisa, no el contenido.

Del mismo archivo se rescata algo que `spec/notas.md` no dice y debería: el frontmatter obligatorio es `created` y `topic`, y los valores válidos de `topic`, `org` y `area` **se obtienen ejecutando un comando** (`grep "^## " notas/notas.md`, `ls -d org/*/`), con prohibición explícita de inventarlos. Es `jntr.vocabulario-ambitos` funcionando, y confirma que el vocabulario se genera y no se materializa.

### 11. El post-write hook que depende de la memoria del agente no se ejecuta

Es la lección más transferible del repositorio, y se ve en su evolución. Primero la regla en prosa ("ejecutar el comando tras cada escritura"), después la regla en mayúsculas con tabla de límites, y finalmente la solución real, en `notes-index-update.MaC.md`: sacarlo del agente y ponerlo en un cron cada diez minutos (`notes-index-auto.sh`), con `flock` compartido, filtro por archivos modificados en los últimos 30 minutos, umbral de madurez de 5 minutos para el fix de enlaces, y cero tokens cuando no hay nada que hacer. La regla en `notas/AGENTS.md` pasó a decir lo contrario de lo que decía: el agente **no** ejecuta los comandos tras escribir notas.

Para TUKU: los comandos de consecuencia que `spec/flujo-informacion.md` cuelga del paso 5 no deberían depender de que el agente se acuerde de invocarlos. No hace falta resolverlo en el epic 002, pero sí saber que la solución probada es sacarlos del turno.

### 12. El comando devuelve un estado, no un código de salida

`jntr.notes-index-update.py` responde `CURRENT`, `UPDATED`, `MISSING_SUMMARY` o `ERROR`, y el proceso define qué hace el agente con cada uno, incluido un bucle: el comando dice qué falta, el agente rellena lo que solo él puede (el resumen inferido leyendo la nota), y se vuelve a correr hasta `CURRENT`. En `ERROR` se reporta al autor y se detiene, sin arreglo manual.

Es el reparto de `spec/agente.md` ya operativo: el script decide qué falta, el LLM lo llena. Vale como contrato de salida para todos los comandos de TUKU, y hace verificable el bucle sin LLM (se puede probar que un estado incompleto produce `MISSING_*` y que completarlo produce `CURRENT`).

Un detalle que se pierde si no se anota: `summary` es obligatorio y **vacío es un estado válido y declarado** (la nota es un stub de menos de diez líneas). Un campo obligatorio con estado vacío legítimo es lo que evita que el linter mienta.

## Lo que se observó y no se trae todavía

- **La consecuencia atada a vocabulario abierto.** `actividad/AGENTS.md` propaga un registro a la página de la entidad en `org/` **si y solo si** lleva `**Hito:**`, `**Decisión:**` o `**Señal:**`. Eso es una consecuencia mecánica disparada por la ontología **abierta**, mientras que `spec/bitacora.md` reserva las consecuencias para la cerrada. Vale la spec; queda la pregunta de si el uso vuelve a pedir lo mismo. No pega en el epic 002 (en un vault vacío no hay a dónde propagar) y es una de las cosas a vigilar en el 004.
- **El ciclo real del autor no es semanal ni de largo fijo.** Los archivos de `actividad/` alternan dos tipos de bloque (trabajo en terreno y descanso) con largos de 5 a 9 días, y `estrategia/Capacidad.md` describe el ritmo con detalle: día de viaje, disponibilidad parcial en los bordes del bloque, roles operativos que se asignan a última hora. Material del epic 005.
- **Las cadencias reales ya están en formato tabla** en `estrategia/Cadencias.md`, con dieciséis registros y cuatro clases de trigger: día exacto, rango, evento y reactivo. Tres caen el día 10 y hay rangos que cruzan el borde de mes, que es exactamente el banco de pruebas que pide la fase 4. Se trae en el epic 005, sin tocarlo antes.
- **Capacidad con costo fijo por rol operativo**, cobrado por cada día que dura el rol, más el reparto bruto de la persona. `estrategia/Capacidad.md` es el caso real contra el que se valida la propuesta abierta de `spec/ambitos.md` sobre dónde vive el bruto. Epic 005.
- **El archivado con cascada** existe y está escrito (`org/_rules/baja-entidades.md`, 7 entidades ya archivadas). Epic 004 o wishlist.
- **`CONTEXTO-RECIENTE.md` arrastra los días sembrados vacíos** (`- ...`) dentro de la cola, así que el agente recibe agenda futura mezclada con actividad ocurrida. Ya estaba anotado en [`epics.md`](epics.md); queda confirmado en vivo, y afecta al paso 1 del flujo.

## Qué hay que decidir en el epic 002, con lo que aporta esto

De las cinco decisiones que [`epics.md`](epics.md) pone antes de empezar el epic:

| Decisión | Qué aporta mac-jpgil |
| --- | --- |
| 1. Qué registros componen el día uno | El corpus ya existe y la forma real de los registros también, con la salvedad de las lecciones 1 y 2 |
| 2. Cómo se verifica lo que depende del agente | Nada directo: mac-jpgil no tiene suite, y esa ausencia es parte de por qué existe TUKU |
| 3. Qué arnés de agente y cómo se aísla | Lección 10: subagente con contexto limpio, contrato de confirmación corta |
| 4. Dónde vive el código y cómo se ejecuta | Lección 11 y 12: fuera del turno del agente, con contrato de estado |
| 5. Dónde se especifica el comportamiento al dirigirse al autor | `AGENTS.md` de la raíz lo tiene en dos líneas de estilo (terso, sin voseo, no narrar), no en un documento propio |
