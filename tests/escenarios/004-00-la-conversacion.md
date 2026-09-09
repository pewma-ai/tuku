# Epic 004 · La conversación

> El autor deja de dictar hechos consumados y conversa: delibera, consulta el estado, cambia de rumbo a media sesión, atiende urgencias y solo al final ratifica. El vault final debe contener únicamente lo resuelto.

Si el [Epic 003](003-00-el-dia-uno-dictado.md) midió la traducción aislada en un turno único, este epic mide la **resistencia del sistema al diálogo humano**: varias idas y vueltas donde pensar en voz alta no debe ensuciar el conjunto canónico ([principio 3](../../docs/principios.md#3-el-agente-es-un-secretario-no-un-dueno)), las dudas se aclaran con preguntas directas y los límites de [`AGENTS.md`](../../template/vanilla/AGENTS.md) se sostienen bajo acumulación de contexto.

---

## Qué entrega el epic

1. **El conductor de sesión multi-turno:** La infraestructura de pruebas capaz de sostener un diálogo de varios turnos sobre el arnés sin perder la sesión ni contaminar el entorno.
2. **Refinamiento de [`AGENTS.md`](../../template/vanilla/AGENTS.md):** Ajuste de las reglas de despacho y límites ante la fricción real de una conversación (deliberación, interrupciones, desambiguación interactiva).
3. **Validación fuerte de los Límites:** Afirmación de que ninguna prohibición de la tabla se vulnera a lo largo de una interacción prolongada (cero edición manual, cero supuestos ante ambigüedad, cero rastro tras propuestas rechazadas).

---

## La escalera de escenarios

| Escenario | Fenómeno dialógico | Qué afirma |
| --- | --- | --- |
| `004-01` | [Deliberación y consulta](004-01-deliberacion-y-consulta.md) | Evaluar opciones y consultar radar sin escribir nada (**diff cero**). |
| `004-02` | [Rectificación y marcha atrás](004-02-rectificacion-y-marcha-atras.md) | Orden tentativa descartada en el turno siguiente no deja rastro. |
| `004-03` | [Desambiguación en dos turnos](004-03-desambiguacion-en-dos-turnos.md) | El agente pregunta ante ambigüedad y el autor resuelve; cierre fuerte del pendiente correcto. |
| `004-04` | [Hecho urgente intercalado](004-04-hecho-urgente-intercalado.md) | Incidente fortuito registrado al vuelo sin perder el hilo de la deliberación previa. |
| `004-05` | [Propuesta y rechazo limpio](004-05-propuesta-y-rechazo-limpio.md) | Curiosidad operativa del agente rechazada sin dejar marcas ni expedientes. |
| `004-06` | [Ratificación compuesta](004-06-ratificacion-compuesta.md) | Resumen final destilado exactamente a los comandos necesarios. |
| `004-07` | [Invariante de límites en sesión larga](004-07-invariante-de-limites-en-sesion-larga.md) | Sesión de 6 turnos sin tocar archivos a mano y con `tuku doctor` sano. |

---

## Cómo se observa la conversación

A diferencia del turno único del 003, un escenario del 004 encadena múltiples turnos donde el arnés preserva el identificador de sesión.

Se vigilan tres momentos:
- **Durante la deliberación:** el `delta` del vault debe permanecer estrictamente vacío.
- **Ante la interrupción o desambiguación:** el comando ejecutado debe limitarse exactamente al hecho o cierre aclarado.
- **Al cierre:** el estado final del vault debe ser idéntico al que habría producido un dictado directo de los acuerdos ratificados, sin residuos de las alternativas descartadas.

---

## Criterio de salida

Una conversación humana donde el autor duda, se contradice, atiende un imprevisto y rectifica termina con el vault en el estado neto ratificado al final, sin mutaciones manuales y sin violar ninguna prohibición de la tabla de Límites.
