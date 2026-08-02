# Pendientes de consistencia

> Cambios que la reescritura de `docs/brief.md` deja pendientes en otros archivos. **No ejecutar todavía**: mientras el brief esté en obra, se edita solo el brief. Esta lista se vacía en una pasada posterior.

## Numeración y referencias al brief

El capítulo "Para quién" fue absorbido como §1.1 y todo lo demás corrió un número. Estructura actual: 1 Qué es · 2 El modelo · 3 Principios · 4 Forma del sistema · 5 Lo que TUKU no es · 6 Criterios de éxito · 7 Restricciones de construcción.

- `spec/nota.md:106` cita "el brief §3.5". Esa sección ya no existe; el contenido sobre reporte y memoria vive hoy en §2.3.

## Principios

- Ahora son **siete**, no seis, y viven solo en el brief. Cualquier documento que hable de "los seis principios" está desactualizado.
- P4 se llamaba "Sembrar y corregir" y hoy es **P4, La autoría es del usuario**. Cualquier cita por el título viejo queda rota.
- P5 se llamaba "Dirección del flujo" y hoy es **P5, La gobernanza es del usuario**. La definición de *Gate* en `docs/glosario.md:99` sigue siendo correcta de fondo, pero conviene revisar cómo nombra el principio.

## Vocabulario

- **reporte** vs. **informe**: el brief y el glosario dicen ahora *reporte*. `docs/arquitectura.md` y los specs siguen diciendo *informe*.
- **sembrar / siembra** salió del brief y del glosario a favor de *proponer / propuesta*. Probablemente sobrevive en `spec/` y en `docs/deployment.md`.
- **humano** vs. **usuario**: el brief usa *usuario* cuando el contraste es con el sistema, y *humano* solo cuando el contraste es con el agente. Queda por decidir si se unifica en el resto de la documentación.

## Interfaces

`docs/brief.md` §4.2 nombra ahora las puertas concretas: Obsidian en local, Quartz en la web, Telegram en el bolsillo, y Hermes como el agente detrás de las tres.

- `docs/arquitectura.md` no describe canales ni la relación entre el agente y los janitors. Falta al menos un párrafo.
- Puede ameritar ADR: adoptar Hermes como agente de referencia de las fases iniciales y Quartz como publicación web, ambos declarados reemplazables.

## Contenido que sale del brief

La antigua §4.3 "Los artefactos del ciclo" se reemplazó por una sección sobre lo que el sistema genera. El detalle que se retiró pertenece a los specs, hay que verificar que esté cubierto allí:

- nombres y estructura de `plan_FECHA_tipo` y `resultados_FECHA_tipo` (`spec/artefactos-ciclo.md`);
- partición mensual de `entradas/` y el prefijo estructurado de cada entrada (`spec/entradas.md`);
- las clasificaciones `hito`, `decision`, `senal` y su extensibilidad.

Dos afirmaciones de esa sección **no** eran implementación y hay que confirmar que sobrevivan en algún lado: que no exista ninguna zona donde el usuario pueda escribir sobre una proyección, y que no haya clasificación de fricción porque nadie rotula sus propios fracasos mientras trabaja.

## Contenido eliminado del brief

El capítulo 7, "Restricciones de construcción", se reemplazó por "Por dónde se empieza", que declara el primer incremento: Hermes como interfaz, Obsidian como visor, `AGENTS.md` y janitors en medio. Quedó fuera la priorización anterior, que ponía como núcleo cadencias, backlog canónico de tareas y captura conversacional; verificar que siga siendo compatible con lo que digan los specs y las decisiones.

El criterio de éxito "Foco conversacional" también salió, porque dependía del modelo de secciones, que ya no aparece en el brief. Exigía que modificar una entidad conversando fuera una llamada al agente con el path de la sección como contexto restringido, y que si requería arquitectura adicional el modelo de secciones estaba mal planteado. Verificar que quede escrito en algún spec.

El bullet "No es un ejército de agentes" salió de §5, así que la definición de *Agente* en `docs/glosario.md:92` ("una sola interfaz conversacional visible") ya no tiene respaldo en el brief. Queda abierto si TUKU es uno o varios agentes.

## Rescatado del documento de principios (eliminado)

El documento de principios se eliminó: duplicaba la §3 del brief y se desincronizaba solo. La regla de precedencia ("gana el principio de número más bajo") se descartó a propósito. Esto es lo que hay que reubicar antes de darlo por cerrado.

**Ejemplos de violación**, material de revisión de código, probablemente a los specs de cada primitiva o a una guía de revisión:

- P1: la interfaz necesita lógica propia para que los archivos tengan sentido; entender el estado de una tarea exige ejecutar el motor; borrar la caché pierde información.
- P2: un proceso dice "el agente decide" sin especificar el criterio, o una operación no tiene forma manual descrita.
- P3: un artefacto que podría producirse por regla se produce por inferencia. El síntoma es que el mismo insumo da resultados distintos en dos ejecuciones.
- P4: el agente regenera algo que el usuario ya corrigió, o corregir exige más esfuerzo que escribir desde cero.
- P5: el sistema ajusta la capacidad declarada del usuario porque observó que no cumple sus planes.
- P6: aparece una lista cerrada de tipos permitidos, un campo obligatorio fuera del núcleo, o una pantalla de configuración de esquemas.

**Reglas duras que ningún otro documento recoge:**

- Un artefacto propuesto por el agente se genera **una vez** y después pertenece al usuario: ningún janitor vuelve a pisarlo. Aplica al plan del ciclo y a la retrospectiva una vez corregidos.
- El agente propone en la forma más corregible posible: opciones concretas y no preguntas abiertas, una palabra de respuesta y no un formulario.
- El motor de cadencias es Python leyendo front matter: corre sin API, sin red y sin créditos.
- Toda acción del agente tiene un equivalente manual documentado.
- Verificación de P6: modelar un dominio ajeno al del autor, una PyME o una junta de vecinos, sin tocar `src/`.
- Verificación de P5: auditar el historial de Git, todo commit que toque `estrategia/` debe tener aprobación humana registrada.
- Verificación de P4: medir el delta entre lo propuesto y lo que queda tras la corrección. Un delta grande y sostenido no es fallo del usuario, es señal de que la propuesta está mal calibrada.

**Curiosidad acotada**, que es diseño de producto y no un principio, y hay que llevar a donde se describa el comportamiento del agente: cuando detecta una anomalía, no cualquier desviación sino la que un humano responsable notaría de inmediato, la señala en voz activa en vez de esperar a que se le pregunte. El límite es la alarma: como máximo unas pocas preguntas por apertura o cierre, reservadas para lo que genuinamente sorprendería a un especialista del dominio. Ya está citada desde `corpus/simulaciones/flujo-turno.md:206` y `spec/artefactos-ciclo.md` §3.2.

## Enlaces rotos por la eliminación del documento de principios

- `README.md:30`
- `docs/README.md:16`
- `docs/arquitectura.md:3`
- `docs/quick_start.md:177`
- `docs/decisiones/README.md:5`
- `docs/decisiones/0001-id-estable.md:57` (cita P3)
- `docs/decisiones/0005-derivadas-no-readonly.md:16` (cita P2)
- `corpus/simulaciones/flujo-turno.md:206` y `:379` (citan P4)

Todos deben apuntar ahora a `docs/brief.md` §3.

## Revisión pendiente dentro del brief

- §5 "Lo que TUKU no es", primer bullet: conserva registro de ingeniería ("primitiva de primera clase").
- §6 "Criterios de éxito", criterio de Replay: bloque denso con "primitivas canónicas", "diff exactamente cero" y "equivalencia semántica".
