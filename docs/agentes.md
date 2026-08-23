# Agentes

Ver `principios.md` para las tres leyes del agente y la cadena de descarga cognitiva.

## Ecosistema y canal único

No hay *un* agente: hay varios, y comparten **un solo canal** con el autor. Cambian las personalidades, no el canal.

| Rol | Qué hace |
|---|---|
| Escribiente | Escucha y redacta en la bitácora. Es el caso habitual. |
| Observador | Detecta entidades emergentes y toma el canal para proponer. |
| Vigía | Revisa pendientes y alerta de los críticos cuando se acerca la hora. |
| Secretario | Abre y cierra ciclos: redacta la intención, sintetiza el reporte. |


> [!NOTE]
> Esto hay que revisarlo, necesito un enjambre de agentes en paralelo y un canal común de comunicación con el autor

El patrón de implementación validado es **delegación de tareas desde un orquestador**, no procesos independientes compitiendo por el canal. El orquestador decide quién actúa, lo que evita negociar turnos entre agentes.

El **arbitraje de turnos** (*¿el observador interrumpe al escribiente o espera una pausa?*) es determinista: decidir quién habla es exactamente el tipo de decisión aburrida que corresponde al janitor.

Esta arquitectura acota además el gasto: sesiones separadas por rol impiden que un contexto único crezca sin control.

## Economía de contexto

500 millones de tokens en ocho días por no controlar el efecto. Ya me pasó.

- Contexto pertinente únicamente, nunca el repositorio entero.
- Tras una hora de inactividad, sesión nueva con solo un resumen del estado anterior.
- Umbral de densidad de instrucciones: la degradación comienza entre 100 y 300 reglas. Ese es el límite real para reglas y cadencias expuestas simultáneamente al modelo.
- Frugalidad (criterio de éxito 8): una sesión normal de registro no invoca ningún modelo caro. El juicio, que se paga, aparece en la apertura, en el cierre y cuando el autor lo pide.

## El agente silencioso

Separación estricta entre análisis y entrega. Un proceso de fondo lee pendientes, bitácora y estado de las entidades buscando conexiones o anomalías. Si no hay nada crítico, guarda **silencio absoluto** (`[SILENT]`). Solo cuando una conclusión madura y aporta valor estratégico real, se deposita en el canal.

## Autonomía calibrada

El grado de autonomía no se infiere: se mide y se declara. Tasa de aceptación y corrección de sugerencias pasadas, desagregada por tipo de entidad. Puede ser aceptable que un agente cree solo la página de un proyecto y no la de una persona.

**Vive en un archivo legible y editable por el autor.**

## Modelos del autor

No es una lista cerrada: es una **categoría de página** que cualquier fuente puede alimentar. Se prevé que crezcan.

| Modelo | Fuente | Mecanismo |
|---|---|---|
| Voz | Interacciones con los agentes | LLM sobre prosa conversacional |
| Hábitos | Timestamps de bitácora | Determinista |
| Prácticas | Lo que el autor hizo con entidades similares | Determinista + agente |
| Contexto organizacional | Conocimiento general del modelo, anclado en notas de inducción | LLM, prior externo |

**La voz no se destila de la bitácora**: lo escrito allí ya fue tratado lingüísticamente y homogeneizado; no es cómo habla el autor. Sí lo es cómo le habla a los agentes.

**Requisito abierto.** El historial conversacional tiene que persistir en texto plano, bajo el mismo régimen de autoría que el resto. Si no queda en Markdown, la voz quedaría destilada de la única parte del sistema que no sobrevive los veinte años.

El archivo `SOBRE-EL-AUTOR.md` (quién es, qué hace, sus preferencias, incluido el género) se edita asistido por IA. Cuando un agente detecta desviación entre lo declarado y la práctica, **advierte; no modifica** (P5).

## Motores

Sin vendor lock, con umbral mínimo. Validados en paralelo con resultados equivalentes: Claude Code, Antigravity, y Hermes con DeepSeek V4 Flash. Umbral de referencia (2026): Gemini 3.6 Flash · Sonnet en esfuerzo medio · DeepSeek V4 Flash estándar.

Distintos motores rinden distinto en la misma tarea: la arquitectura permite asignar motor **por rol**, no imponer uno global.
