# En qué orden implementar los tests

## Fases

Diez fases. **Cada una termina con un vault que alguien puede usar**, no con una capa que solo le sirve a la siguiente. Si una fase no se puede entregar sola, está mal cortada.

El LLM aparece en los dos extremos y el medio es determinista, que es el principio 4 convertido en plan de trabajo: primero lo que se verifica exacto, al final lo que solo se puede evaluar.

| Fase | Nombre | Qué se puede hacer al terminarla | LLM | Fixture |
| --- | --- | --- | --- | --- |
| 0 | El vault que se puede abrir | Empezar a escribir a mano | no | `vacio` |
| 1 | La entrada | Dictar y que quede bien escrito | sí | `primer-dia` |
| 2 | Pendientes | Que no se olvide nada | no | `ciclo-en-curso` |
| 3 | El árbol de ámbitos | Que cada cosa tenga su lugar | no | `ciclo-en-curso` |
| 4 | Cadencias | Que el sistema recuerde solo | no | `ciclo-en-curso` |
| 5 | Notas y enlaces | Que el tejido se mantenga | no | `ciclo-en-curso` |
| 6 | El ciclo | Abrir y cerrar sin perder nada | no | `ciclo-por-cerrar` |
| 7 | Plan y resumen | Que la propuesta valga la pena leerla | sí | `ciclo-por-cerrar` |
| 8 | Endurecimiento | Usarlo en serio | no | `historico` |
| 9 | Inferencia semántica | Que note cosas que nadie pidió | sí | `historico` |

Cada fase se describe igual, con una sección **No entra** que es lo mismo que TUKU le pide a un plan de ciclo: decir qué se deja fuera y por qué, para que no se arrastre sin darse cuenta.

### Fase 0. El vault que se puede abrir

**Pregunta.** ¿Alguien sin conocimientos de informática puede empezar sin ayuda?

**Se construye.** El árbol del estado cero y lo que lo copia a un directorio limpio. Nada más: no hay janitors, no hay agente, no hay LLM.

**Sale cuando.** Instalar en un directorio vacío produce byte a byte el fixture `vacio`, y una persona que no sabe qué es TUKU abre `AHORA.md`, escribe una línea a mano y no rompe nada.

**No entra.** Decidir el tipo de ciclo real de quien lo usa. Arranca en semanal y el tipo verdadero emerge después.

Es la única fase cuyo criterio de salida **no es técnico**. Se verifica con una persona, no con un diff. Y es la fase que hace verdadero el principio 1: si el vault recién instalado no se puede operar a mano, ninguna fase posterior lo va a arreglar.

### Fase 1. La entrada

**Pregunta.** ¿El dictado se convierte en una línea de bitácora bien formada?

**Se construye.** Inyección de contexto reciente y vocabulario, formateo a `- HH:MM - [[ambito]] ~~(Hecho)~~ **clasificacion**: cuerpo`, inserción en el día correcto y en orden cronológico, y lint.

**Janitors.** `jntr.contexto-reciente`, `jntr.vocabulario-ambitos`, `jntr.entrada-insertar`, `jntr.entrada-lint`

**Sale cuando.** El corpus se reproduce con la ontología cerrada exacta, marca y posición, y con el ámbito correcto. La clasificación abierta se mide aparte y no bloquea la fase, porque es vocabulario del autor y no del sistema.

**No entra.** Ninguna consecuencia. La entrada solo escribe en la bitácora. **Si en esta fase algo toca `PENDIENTES.md`, el corte está mal hecho.**

Esta fase es la que habilita todas las demás: a partir de acá, inyectar un caso de prueba es escribir una línea de texto.

### Fase 2. Pendientes

**Pregunta.** ¿La fuente de verdad se mantiene sola, sin que el autor la ordene?

**Se construye.** Abrir, cerrar, bajar de escalón, vencer, unicidad, sincronía de transclusiones y el reporte por actividad.

**Janitors.** `jntr.pendiente-abrir`, `jntr.pendiente-cerrar`, `jntr.pendiente-mover`, `jntr.pendientes-atrasados`, `jntr.pendientes-lint`, `jntr.transclusiones-sync`, `jntr.pendientes-por-actividad`

**Sale cuando.** Abrir es copiar texto literal y cerrar es borrarlo, sin LLM, gracias a la regla del infinitivo. Ningún pendiente aparece en dos callouts. Correr los janitors dos veces da lo mismo.

**No entra.** Promover entre ciclos. Eso pertenece a abrir un ciclo y no tiene sentido antes de que exista el ciclo siguiente.

Primera fase de inyección pura. Las transclusiones se pueden probar acá porque el estado cero ya trae los días sembrados.

### Fase 3. El árbol de ámbitos

**Pregunta.** ¿Dónde aterriza cada entrada y qué regla manda?

**Se construye.** Los tres roles (ámbito, categoría, actividad), la creación, la obligatoriedad de `AGENTS.md` y `CADENCIAS.md`, la resolución de reglas por cercanía, el archivado y la reescritura de enlaces.

**Janitors.** `jntr.ambito-crear`, `jntr.ambitos-lint`, `jntr.reglas-resolver`, `jntr.paginas-index`, `jntr.archivar`, `jntr.enlaces-reescribir`, `jntr.ambitos-inactivos`

**Sale cuando.** Con un fixture de tres niveles se comprueba que la regla más cercana gana. Una entrada nunca apunta a una categoría. Archivar deja resolviendo los enlaces desde bitácoras ya cerradas.

**No entra.** La deliberación con el autor antes de archivar. Acá se implementa la mecánica; decidir que una rama se cierra no es código.

### Fase 4. Cadencias

**Pregunta.** ¿El sistema sabe recordar por su cuenta?

**Se construye.** Alta desde una entrada, colecta desde el árbol, resolución del trigger (calendario más tipo de ciclo), inyección en el día que corresponde y el reporte del autor.

**Janitors.** `jntr.cadencia-alta`, `jntr.cadencias-colectar`, `jntr.cadencias-resolver`, `jntr.cadencia-inyectar`, `jntr.cadencias-reporte`

**Sale cuando.** Las cadencias reales de `mac-jpgil` se expresan en el formato sin perder información, incluidas las de rango que cruzan el borde de mes y las tres que caen el día 10. Inyectar dos veces no duplica lo emitido.

**No entra.** Inferir cadencias implícitas del histórico. Eso es fase 9.

Primera fase con un banco de pruebas real y no inventado. **Si una cadencia del autor no cabe en el formato, el formato está incompleto**, y eso se descubre acá o no se descubre.

### Fase 5. Notas y enlaces

**Pregunta.** ¿El tejido se mantiene sin que el autor lo teja a mano?

**Se construye.** Notas tipadas, conversión de menciones en enlaces, `index.md` desde los frontmatter, detección de enlaces rotos y notas huérfanas.

**Janitors.** `jntr.menciones-enlazar`, `jntr.notas-index`, `jntr.notas-lint`, `jntr.enlaces-lint`

**Sale cuando.** Crear una nota tipada y enlazarla desde una entrada es determinista. Todo `[[enlace]]` resuelve. El index se regenera igual dos veces.

**No entra.** Destilar el histórico y proponer notas nuevas. Ambas son inferencia y van a la fase 9. Acá solo la mecánica del tejido.

### Fase 6. El ciclo

**Pregunta.** ¿Se puede abrir y cerrar un ciclo sin perder nada?

**Se construye.** Las dos secuencias ordenadas completas, la promoción de pendientes entre ciclos, el aplanado de transclusiones y el archivo.

**Janitors.** `jntr.ciclo-abrir`, `jntr.pendientes-promover`, `jntr.transclusiones-aplanar`, `jntr.ciclo-cerrar`

**Sale cuando.** Abrir dos veces no duplica días, pendientes ni emisiones. Cerrar dos veces no vuelve a mover. Y hay una prueba que **falla a propósito** si se aplana antes de generar el resumen, porque ese es el orden que importa y sin prueba se pierde.

**No entra.** Generar el plan y el resumen. Entran como archivos inyectados, no producidos.

Ese es el truco de corte de esta fase: **el cierre se prueba entero antes de que exista quien escriba el resumen**, y la fase 7 reemplaza los archivos falsos por los de verdad sin tocar la mecánica. Además, el ciclo compone todo lo anterior, así que es acá donde van a aparecer los defectos de las fases 2 a 5.

### Fase 7. Plan y resumen

**Pregunta.** ¿La propuesta que hace el sistema vale la pena leerla?

**Se construye.** Cálculo de capacidad, plan con sus cuatro secciones, "no entra" con su efecto sobre pendientes y alertas, registro del delta, y resumen con sus cinco secciones y su veredicto por intención.

**Janitors.** `jntr.capacidad-calcular`, `jntr.plan-no-entra`, `jntr.plan-delta`, `jntr.ciclo-extracto`

**Sale cuando.** La capacidad se calcula restando el costo fijo y no sobre horas brutas. El veredicto sale de comparar plan contra ejecución, lo que se verifica con un caso doble: la misma actividad contra un plan cumplido y contra uno incumplido tiene que dar veredictos distintos. El delta queda registrado, incluso cuando es cero.

**No entra.** Juzgar la calidad de la prosa.

Primera fase donde el criterio de salida **se parte en dos**: lo que se verifica con script (secciones presentes, veredicto correcto, capacidad bien restada) y lo que solo se evalúa. Conviene decirlo en vez de fingir que todo se puede afirmar.

### Fase 8. Endurecimiento

**Pregunta.** ¿Aguanta el uso real y el error humano?

**Se construye.** Los casos de error, la reconstrucción completa y la idempotencia medida sobre todo el sistema junto y no janitor por janitor.

**Janitors.** `jntr.reconstruir`, y todos los lint corriendo a la vez.

**Sale cuando.** Borrar todo lo derivado y regenerarlo devuelve byte a byte lo mismo. El conjunto canónico (`AHORA.md`, `bitacoras/`, `PENDIENTES.md`, `ambitos/`, `notas/`) no se toca nunca. Y cada caso de error produce un reporte, no una excepción.

**No entra.** Nada nuevo. Esta fase no agrega capacidades, cierra huecos.

La regla que gobierna la fase: **un error del autor nunca se rechaza, se reporta.** Rechazar lo que alguien acaba de dictar es la forma más rápida de que deje de usar TUKU.

### Fase 9. Inferencia semántica

**Pregunta.** ¿El sistema nota cosas que el autor no pidió?

**Se construye.** Detección de recurrencias, destilado de notas tipadas desde el histórico en contexto aislado, inferencia de cadencias implícitas, prioridades por ámbito y el ciclo de propuesta y aprobación.

**Janitors.** `jntr.recurrencias`, `jntr.nota-destilar`, `jntr.periodicidad`

**Sale cuando.** No hay criterio byte a byte para lo que propone. Se mide por la proporción de propuestas que el autor acepta, y esa medición solo tiene sentido después de varios ciclos de uso real.

**No entra.** Ejecutar cualquier cosa sin aprobación.

**La única prueba dura de esta fase es negativa:** rechazar una propuesta no deja rastro en ninguna primitiva, y eso sí se verifica con diff. Es la traducción a prueba del principio 3, y es lo que permite que el resto de la fase sea difuso sin ser peligroso.

### Qué corta las fases

Tres criterios, en este orden:

1. **Entregable solo.** Cada fase deja algo usable. Es lo que permite parar en cualquier punto sin quedarse con un sistema a medio construir.
2. **Un fixture nuevo por vez.** Una fase que necesita dos estados iniciales nuevos está haciendo dos cosas.
3. **El LLM se aísla.** Las fases 1, 7 y 9 lo usan y las demás no. Que estén separadas es lo que deja medir cuánto del sistema depende de un modelo, y ese número debería ser chico.

### Lo que atraviesa todas las fases

- **Idempotencia.** Ninguna fase cierra sin que correr sus operaciones dos veces dé el mismo resultado.
- **Diff byte a byte.** Es la verificación del principio 9 y sale gratis en cada prueba.
- **El campo "A mano".** Ningún janitor entra sin él. Un janitor sin ese campo es una dependencia disfrazada.

## Estructura y janitors

El árbol de directorios completo, la convención de mayúsculas y dónde vive la especificación de cada janitor (`reglas/janitors.tuku.md` en el repo, código en `~/.tuku/janitors`) ya no están aquí: viven en [`../spec/README.md`](../spec/README.md), que es normativo. Este archivo solo dice en qué orden se construye lo que ahí se especifica.

## Estrategia de pruebas

Registrar una entrada produce **una sola cosa**: texto escrito en la bitácora. Todo lo demás, abrir un pendiente, cerrar otro, emitir cadencias, enlazar, proponer, ocurre **después**, leyendo lo que quedó escrito.

Eso parte el sistema en dos mitades con costos de prueba muy distintos.

**La entrada.** Es lo único que necesita LLM: dictado a línea bien formada. Se prueba contra ground truth, comparando la salida con entradas ya redactadas.

**Todo lo demás.** Reacciona a la bitácora, así que no necesita LLM. Un script inyecta líneas y se observa qué hace el sistema. Determinista, repetible, sin tokens.

El corpus sirve para las dos mitades: la Parte 1 es el dictado de entrada, la Parte 2 es el fixture de inyección.

### Dos puntos de inyección, no uno

Algunas operaciones no se disparan desde la bitácora, porque no son hechos de la vida del autor sino del sistema, y ya decidimos no registrarlas:

| Operación | Cómo se prueba |
| --- | --- |
| Abrir y cerrar pendientes, emitir cadencias, enlazar | Inyectando líneas de bitácora |
| Mover un pendiente de escalón | Invocando el janitor con argumentos |
| Corregir el plan | Idem |
| Aprobar o rechazar una propuesta | Idem |

Las dos vías son scriptables y ninguna necesita LLM.

### Lo que esto le da a la tabla de fases

- **Fase 1**: la entrada. Único punto con LLM y con ground truth.
- **Fases intermedias**: todo lo que reacciona a lo escrito. Inyección, sin LLM.
- **Fase 9**: inferencia semántica. Vuelve el LLM, y ya sin respuesta única.

El LLM aparece en los dos extremos y el medio es determinista. Es el principio 4 convertido en plan de trabajo: primero lo que se verifica exacto, al final lo que solo se puede evaluar.

### El requisito que esto impone

Para que la inyección funcione, **cada consecuencia tiene que ser derivable del texto de la entrada**. Si el contenido de una cadencia sale de la conversación y no de lo escrito, esa vía queda fuera de la plataforma de pruebas.

Es una prueba de diseño además de una de implementación. Si algo no se puede reconstruir desde la bitácora, entonces o a la entrada le falta información, o esa operación pertenece a la segunda vía y hay que decirlo.

### Cada prueba es una transición de estado

Toda prueba tiene la misma forma: un estado inicial de archivos, una operación, y un estado final esperado. La comparación es un diff de directorios y no hace falta más andamiaje.

```text
fixtures/<nombre>/
  inicial/          # el vault antes
  operacion.txt     # la línea a inyectar, o el comando a invocar
  esperado/         # el vault después
```

Que la comparación sea byte a byte no es rigor de más: es la verificación del principio 9. Si un janitor no produce el mismo resultado dos veces, el diff lo delata sin que nadie lo busque.

### El estado cero

El primero y el más importante: **el vault recién instalado**, antes de la primera palabra.

Importa más que los demás porque no es solo un fixture, es el producto. Alguien sin conocimientos de informática tiene que poder abrirlo y empezar sin configurar nada. Es lo que promete el principio 2 y lo que dice el brief: una bitácora en blanco y una pregunta.

```text
AGENTS.md                 # dice dónde viven los janitors
LIBRO-DE-ESTILO.md        # el que trae TUKU, con los vocabularios de partida
AHORA.md                  # días sembrados, sin entradas
PENDIENTES.md             # los cinco callouts de horizonte, vacíos
ambitos/
  AGENTS.md
  CADENCIAS.md
  personal/
    AGENTS.md
    CADENCIAS.md
    personal.md
notas/
reglas/                   # los que trae TUKU
```

Acá se cobra la decisión de que `AGENTS.md` y `CADENCIAS.md` sean obligatorios aunque estén vacíos. En el estado cero **están todos vacíos**, y aun así ningún janitor tiene que manejar el caso "no existe".

**Falta decidir el ciclo del estado cero.** `AHORA.md` necesita `ciclo`, `desde` y `hasta`, pero quien recién parte no tiene turnos ni sabe qué es un ciclo. Lo más razonable es arrancar en semanal, que es el ritmo menos sorprendente, y que el tipo real emerja después. Rotar necesita alguna regla, y esa regla no puede ser una pregunta el primer día.

### La escalera de fixtures

Los estados siguientes no se escriben a mano, se generan reproduciendo operaciones desde el estado cero:

| Fixture | Cómo se llega | Qué habilita probar |
| --- | --- | --- |
| `vacio` | recién instalado | que se pueda empezar |
| `primer-dia` | una entrada | la entrada y sus consecuencias |
| `ciclo-en-curso` | varios días, pendientes en varios escalones, cadencias vigentes | casi todo |
| `ciclo-por-cerrar` | ciclo completo sin cerrar | el cierre |
| `historico` | varios ciclos cerrados | archivado y enlaces viejos |

Generarlos por reproducción en vez de escribirlos tiene un efecto lateral útil: **la escalera es en sí misma una prueba de integración.** Si construir `ciclo-en-curso` desde `vacio` falla, hay un defecto, y aparece antes de correr ninguna prueba individual.

## Orden de las pruebas

De abajo hacia arriba: primero lo que no depende de nada, al final lo que compone todo lo anterior. **Abrir y cerrar un ciclo van al final a propósito**, porque tocan todas las primitivas y su orden interno importa.

Casi ninguna prueba se sostiene sola: la mayoría necesita un janitor que inyecte contexto, busque información o corrija inconsistencias. Van anotados al lado con `→`. Los nombres son la entrada de `reglas/janitors.tuku.md`.

### Entrada
- Inyectar contexto reciente y vocabulario antes de interpretar nada → `jntr.contexto-reciente`, `jntr.vocabulario-ambitos`
- Formatear la entrada. Ambito y clasificacion opcionales según el contexto.
  `- HH:MM - [[ambito]] **clasificacion**: cuerpo`
- La marca de la ontología cerrada va en la misma posición, antes de la clasificación:
  `- HH:MM - [[ambito]] ~~(Hecho)~~ **clasificacion**: cuerpo`
- Inferir ámbitos según el texto → `jntr.vocabulario-ambitos`
- Un dictado con varios hechos produce varias entradas
- Insertar en el día correcto y en orden cronológico, sin reordenar lo ya escrito → `jntr.entrada-insertar`
- Lint → `jntr.entrada-lint`
	- Ontología cerrada estricta, ontología abierta permisiva
	- Un tipo desconocido se reporta para preguntar después, nunca se rechaza

### Pendientes
- Abrir un pendiente desde la bitácora → `jntr.pendiente-abrir`
	- Cae en `^sin-fecha`, con el cuerpo copiado literal de la entrada
- Cerrar un pendiente desde la bitácora → `jntr.pendiente-cerrar`
	- Desaparece del callout donde esté, sin importar el escalón
- Bajar de escalón → `jntr.pendiente-mover`
	- `sin-fecha` → horizonte → fecha exacta, sin registrar el movimiento en la bitácora
- Vencer → `jntr.pendientes-atrasados`
	- Lo fechado antes de HOY pasa a `^atrasados` con el vencimiento estampado
- Unicidad → `jntr.pendientes-lint`
	- Ningún pendiente aparece en dos callouts
- Sincronía de transclusiones → `jntr.transclusiones-sync`
	- Crear, mover o borrar un pendiente deja `AHORA.md` sin cajas de error
	- Y sin pendientes fechados que falten en su día
- Generar `reportes/pendientes-por-actividad.md` desde `PENDIENTES.md` → `jntr.pendientes-por-actividad`
	- Esto permite hacer transclusiones dentro de las paginas de ambito/actividad

### Cadencias
- Especifica una cadencia
	- Se registra como entrada `**cadencia**`
	- Se escribe la cadencia en el ámbito que corresponde → `jntr.cadencia-alta`
	- Se verifica la bitácora actual y se modifica si es necesario, para incluir la nueva cadencia en el día que corresponde → `jntr.cadencia-inyectar`
- El trigger conoce el tipo de ciclo, no solo el calendario → `jntr.cadencias-resolver`
- Colectar las cadencias vigentes desde el árbol → `jntr.cadencias-colectar`
- Publicar la vista del autor en `reportes/cadencias.md` → `jntr.cadencias-reporte`
- Idempotencia
	- Inyectar dos veces la misma cadencia no duplica lo emitido

### Ambitos
- Crear un nuevo ámbito → `jntr.ambito-crear`
- Crear una nueva actividad dentro del ambito
- Crear una nueva categoria dentro de ambito (por ejemplos, trabajo/clientes/juanito_perez.md)
- Todo directorio nace con `AGENTS.md` y `CADENCIAS.md`, aunque vacíos → `jntr.ambitos-lint`
- Agregar reglas específicas por ámbito o categoría
	- La más cercana prevalece → `jntr.reglas-resolver`
- Una entrada nunca apunta a una categoría → `jntr.ambitos-lint`
- Detectar ámbitos activos sin actividad hace mucho → `jntr.ambitos-inactivos`
- Archivar una actividad (terminé el proyecto de streamlit) → `jntr.archivar`
	- Caro.. requiere deliberación con el autor
	- Los enlaces desde bitácoras ya cerradas siguen resolviendo → `jntr.enlaces-reescribir`
- Archivar un ámbito (ya no trabajo en Calzones Bendek) → `jntr.archivar`
	- Caro.. requiere deliberación con el autor

### Notas
- Crear una nota y enlazarla desde una entrada
- Destilar una nota tipada desde el histórico, en contexto aislado → `jntr.nota-destilar`
- Convertir menciones sueltas en enlaces → `jntr.menciones-enlazar`
- Mantener `index.md` desde los frontmatter, OKF compliant → `jntr.notas-index`
- Detectar enlaces rotos y notas huérfanas → `jntr.enlaces-lint`
- "Ver además": presencia de la sección y de texto de motivo → `jntr.notas-lint`

### Enlaces y propuestas
- Enlazar a páginas que ya existen, en el momento de escribir la entrada → `jntr.paginas-index`
- Una propuesta se muestra y espera aprobación, no se ejecuta sola
- Rechazar una propuesta no deja rastro en las primitivas
	- Sin janitor a propósito: una propuesta rechazada no escribe nada, así que no hay nada que limpiar

### Abrir un ciclo
En este orden:

1. Crear `AHORA.md` con frontmatter (`ciclo`, `desde`, `hasta`) → `jntr.ciclo-abrir`
2. Sembrar los días con `## Día, DD de MM` → `jntr.ciclo-abrir`
3. Rodar y promover pendientes: `este-turno` sin fecha rueda, `proximo-turno` promueve → `jntr.pendientes-promover`
4. Colectar cadencias desde el árbol y emitir lo que corresponda → `jntr.cadencias-colectar`, `jntr.cadencias-resolver`, `jntr.cadencia-inyectar`
5. Generar el plan en `planes/` y transcluirlo → `jntr.capacidad-calcular` lo alimenta
6. Transcluir los pendientes de cada día → `jntr.transclusiones-sync`

- Idempotencia: abrir dos veces no duplica días, ni pendientes, ni emisiones

### Cerrar un ciclo
En este orden:

1. Generar el resumen en `reportes/`, que necesita el plan y las entradas todavía vivos → `jntr.ciclo-extracto` lo alimenta
2. Aplanar el plan y los pendientes de cada día → `jntr.transclusiones-aplanar`
3. Dejar el enlace al resumen → `jntr.ciclo-cerrar`
4. Mover a `bitacoras/bitacora-DESDE-HASTA.md` → `jntr.ciclo-cerrar`
5. Dejar `AHORA.md` limpio para el ciclo siguiente → `jntr.ciclo-cerrar`

- El orden importa: aplanar antes de generar el resumen lo deja sin de dónde leer
- Idempotencia: cerrar dos veces no vuelve a mover ni a duplicar

### Planes
- Estructura del plan
	- **Intención del ciclo**: lista corta, cada punto es un ámbito y su acción principal
	- **No entra, y por qué**: la razón es parte del plan, no un comentario
	- **Restricciones y contexto**: lo que acota el ciclo antes de empezar
	- **Señales a vigilar**: qué observar durante el ciclo sin que sea tarea
- Calcular la capacidad antes de planificar → `jntr.capacidad-calcular`
	- Partir de las horas del ciclo y restar el costo fijo: roles operativos, viajes, días con los niños
	- Un rol operativo cuesta horas **por día**, no una vez
	- Se planifica contra lo que queda. Planificar contra las horas brutas es la forma más común de fallar
- Traer al plan
	- Pendientes heredados del ciclo anterior → `jntr.pendientes-promover`
	- Cadencias que caen dentro del ciclo → `jntr.cadencias-resolver`
	- Qué quedó abierto y sin cerrar en el ciclo anterior → `jntr.ciclo-extracto`
- El plan se propone al autor y no se escribe sin su aprobación
- Mover algo a "No entra" pospone sus pendientes y silencia sus alertas de ausencia → `jntr.plan-no-entra`
- Registrar cuánto corrigió el autor el plan propuesto → `jntr.plan-delta`
	- Sin correcciones también es información: dice que la propuesta estuvo bien calibrada

### Análisis
- Al cerrar un ciclo
	- Generar el resumen del ciclo en `reportes/`, y dejar solo el enlace en la bitácora → `jntr.ciclo-extracto`
	- Estructura del resumen
		- **Resumen ejecutivo**: tema dominante del ciclo, qué se logró, dónde está el foco urgente
		- **Veredicto por intención**: cumplida, parcial, en riesgo o sin avance, cada una con su acción siguiente
		- **Desglose por ámbito**: estado, pendientes que siguen abiertos, actividad realizada
		- **Emergente**: lo que ocurrió sin estar en el plan
		- **Momentum y señales**: pocos logros que cambian la trayectoria, y señales que merecen atención más allá del ciclo
	- El veredicto sale de comparar plan contra ejecución, no de resumir la actividad
- Prioridades por ámbito / dir / dir

### Integridad
- Borrar todo lo derivado y regenerarlo devuelve lo mismo → `jntr.reconstruir`
- El conjunto canónico no se regenera: `AHORA.md`, `bitacoras/`, `PENDIENTES.md`, `ambitos/`, `notas/`
- Todo `[[enlace]]` resuelve a una página existente → `jntr.enlaces-lint`
- Archivar no rompe enlaces desde bitácoras ya cerradas → `jntr.enlaces-lint`

### Inferencias
- Detectar que algo recurrente merece nota propia, y de qué tipo → `jntr.recurrencias`
	- Proponer al autor, nunca crearla sola
	- Barrer el histórico en contexto aislado, no en la conversación → `jntr.nota-destilar`
	- Si el tipo es `persona`, no escribir nada que no se le podría mostrar
- Inferir cadencias implícitas estudiando las bitácoras anteriores → `jntr.periodicidad`
- Detectar ámbitos y actividades → `jntr.recurrencias`
- Prioridades por ámbito

### Casos de error
- El ámbito no existe → `jntr.ambitos-lint`
- Se cierra un pendiente que no está abierto, o se cierra dos veces → `jntr.pendientes-lint`
- El dictado es ambiguo y no se puede situar
- Una cadencia emite algo que ya está en el día → `jntr.cadencia-inyectar`
- La entrada cae fuera del rango del ciclo abierto → `jntr.entrada-lint`

## Qué especifica cada primitiva

El flujo de la información, el formato de bitácora y sus dos ontologías, `PENDIENTES.md` y su escalera de horizontes, el árbol de ámbitos, `CADENCIAS.md` y su ciclo de vida, las notas tipadas y su destilado, y la anatomía de `AHORA.md` (apertura y cierre de ciclo) ya no están aquí: son normativos y viven en `../spec/`, un archivo por primitiva. Ver [`../spec/README.md`](../spec/README.md) para el orden de lectura.

Este archivo conserva solo el plan de implementación: en qué fase se construye cada pieza y con qué fixture se prueba.

## Apéndice: janitors de mac-jpgil

Referencia de lo que funcionaba en `mac-jpgil`, no un diseño para TUKU. Se listan para no perder lo aprendido, pero **deben repensarse desde cero** cuando toque, contra las primitivas y las reglas de arriba, no contra la estructura de `mac-jpgil`.

La división es en sí misma el dato más útil: lo que allá quedó como script es lo que resultó formalizable, y lo que quedó como proceso de agente es lo que nunca terminó de bajar a determinismo.

### Scripts deterministas (`procesos/scripts/`)

| Script | Qué hace |
| --- | --- |
| `jntr.bitacora-tail.py` | Genera `CONTEXTO-RECIENTE.md` con las últimas N líneas de días y entradas de los últimos ciclos |
| `jntr.tareas-pendientes.py` | Pendientes en cuatro modos: linter, scan, transfer, validate |
| `jntr.org-categories-summary.py` | Vocabulario controlado de categorías desde el campo `keywords` del frontmatter de cada área |
| `jntr.org-frontpage-update.py` | Regenera las front pages de cada ORG desde los frontmatters |
| `jntr.notes-index-update.py` | Mantiene `notas.md` desde los frontmatters |
| `jntr.check-broken-links.py` | Enlaces rotos y archivos huérfanos |
| `jntr.obsidian-links-to-markdown.py` | Convierte `[[..]]` a enlaces Markdown estándar |
| `jntr.find-tags.py` | Busca y agrupa tags (`#TODO`, `#WISH`, `#IDEA`) |
| `jntr.persona.py` | Notas de persona |
| `jntr.git-commit-context.py` | State machine para commits semánticos |
| `jntr.serendipia-context.py`, `jntr.serendipia-queries.py` | Mecanismo Serendipia |
| `jntr.filter-logs.py`, `chispazos-snapshot.py`, `find_missing_summaries.py` | Utilitarios menores |
| `bitacora-tail-auto.sh`, `git-janitor-auto.sh`, `notes-index-auto.sh` | Wrappers de cron |

### Procesos de agente (`procesos/*.MaC.md`)

| Proceso | Qué hace |
| --- | --- |
| `apertura-semanal` | Abre el ciclo, siembra días y arma el plan |
| `cierre-semanal` | Cierra el ciclo y genera el resumen |
| `transferencia-pendientes` | Arrastra pendientes al ciclo nuevo |
| `pendientes-en-bitacora` | Abre y cierra pendientes desde lo dictado |
| `inicio-sesion` | Reconstruye contexto al abrir sesión |
| `radar` | Consulta en vivo del estado presente |
| `resumen-dia`, `avance-semana`, `reporte-fin-turno` | Destilados por ventana de tiempo |
| `propagate-local-activity-to-org` | Propaga hitos, decisiones y señales a las páginas de área |
| `persona-note`, `notes-index-update` | Mantención de notas |
| `serendipia`, `serendipia-hint`, `modo-brainstorm`, `ai-foco-sugerido`, `amigo` | Comportamiento del agente |
| `git-commit`, `git-janitor-install`, `personal-preferences`, `readme` | Infraestructura |

### Observaciones que conviene no perder

- `CONTEXTO-RECIENTE.md` arrastra hoy los días sembrados vacíos (`- ...`) dentro de la cola, así que el agente recibe agenda futura mezclada con actividad ocurrida. Excluirlos es trivial y evita el error de raíz.
- `apertura-semanal`, `cierre-semanal`, `transferencia-pendientes` y `pendientes-en-bitacora` son procesos de agente casi enteramente deterministas. Ahí está el ahorro grande de tokens y de latencia, que es la fricción anotada el 11 de agosto sobre Hermes tardando demasiado con las reglas de MaC.
- La regla "Ver además con motivo" está asignada al agente, pero la **presencia** de la sección y de texto tras el enlace es verificable por script. Solo la **calidad** del motivo necesita juicio. Sirve como ejemplo de regla que conviene partir en dos.
- `jntr.org-categories-summary.py` es el que produce el vocabulario que se inyecta al abrir sesión. Es la pieza que más rinde por línea de código y la primera que vale la pena rehacer.

---

## Apéndice: indicaciones para agentes

Movido a [`../spec/agente.md`](../spec/agente.md): qué se inyecta y cuándo, la carga diferida de reglas, el reparto entre LLM y script, y la conducta esperada. Es normativo, no un detalle de implementación, así que no vive en este plan.
