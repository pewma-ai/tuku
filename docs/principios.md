# Principios de diseño

> `docs/principios.md` · Desarrolla la §4 del [brief](brief.md). Cada principio se
> presenta con lo que afirma, lo que implica en la práctica, cómo se ve una violación y
> cómo se verifica.
>
> Estos principios son la vara para resolver disputas de diseño. Cuando dos opciones
> parecen igual de buenas, gana la que satisface el principio de número más bajo.

---

## P1 — La arquitectura Markdown es el diseño; todo lo demás la sigue

**Afirma.** Primero se decide cómo viven los archivos: qué es canónico, qué es derivado,
qué front matter llevan, cómo se anidan. La GUI, el motor, el deployment y los agentes son
consecuencias de esa arquitectura, nunca al revés.

**Por qué.** La elección de texto plano es deliberada e ideológica: los datos del usuario
deben sobrevivir al motor, a PEWMA.AI y a la industria entera de LLMs. Un archivo Markdown
en Git es legible en 2046 con herramientas que hoy no existen. Cualquier decisión que
introduzca un formato que solo TUKU entiende traiciona el proyecto entero.

**Implica.**
- Ninguna información existe solo en una base de datos, un índice o una caché. Todo lo que
  importa está en un `.md` versionado; lo demás es reconstruible y desechable.
- El front matter es el punto de extensión. Un campo nuevo se agrega ahí antes que en
  cualquier otro lugar.
- Mientras más evidente sea la estructura en Markdown, más simple resulta la GUI.

**Se viola cuando.** La interfaz necesita lógica propia para que los archivos tengan
sentido. Si para entender el estado de una tarea hay que ejecutar el motor, el formato está
mal. Si borrar `~/.tuku/cache/` pierde información, el formato está mal.

**Se verifica.** Abrir el perfil en un editor de texto cualquiera y responder: ¿qué tengo
pendiente?, ¿qué hice la semana pasada?, ¿qué proyectos están activos? Si hace falta
software para contestar, P1 no se cumple.

---

## P2 — Operable a mano; los agentes toman lo tedioso

**Afirma.** Un usuario suficientemente disciplinado debe poder operar el sistema completo
con un editor de texto y nada más. Lo que se delega a agentes es lo tedioso o intensivo en
tiempo, nunca lo esencial.

**Por qué.** Es la garantía de continuidad. Si el sistema solo funciona con un LLM
disponible, entonces una caída de proveedor, un cambio de precios o un país sin acceso
dejan al usuario sin su gestión. También es la garantía de comprensibilidad: un sistema que
un humano puede ejecutar es un sistema que un humano puede auditar.

**Implica.**
- Los procesos (`src/tuku/procesos/*.md`) se escriben como instrucciones explícitas,
  ejecutables por una persona **o por un agente de inteligencia media**. Sin trucos de
  prompting, sin depender de razonamiento de frontera.
- El motor agéntico de referencia para pruebas es Hermes con un modelo de gama económica,
  invocado por línea de comandos. Si un proceso necesita un modelo caro para no
  descarrilar, el proceso está mal escrito — no falta modelo.
- Toda acción del agente tiene un equivalente manual documentado.

**Se viola cuando.** Un proceso dice "el agente decide" sin especificar con qué criterio, o
cuando una operación no tiene forma manual descrita.

**Se verifica.** Ejecutar un ciclo completo —apertura, registro, cierre— siguiendo solo los
procesos, sin agente, y obtener un resultado válido. Y ejecutarlo con el modelo económico y
obtener lo mismo.

---

## P3 — Determinismo primero, agencia al final

**Afirma.** Todo lo que puede garantizarse con un script se garantiza con un script. El
juicio del LLM se reserva para lo que genuinamente requiere juicio.

**Por qué.** Un recordatorio que depende de que un modelo se acuerde no es un recordatorio.
La promesa del nombre —lo que entró vuelve cuando corresponde— solo es creíble si el
mecanismo es determinista, reproducible y funciona sin conexión.

**Implica.** La coherencia del sistema se divide en tres familias con garante y costo
distintos:

| Familia | Qué garantiza | Garante | Costo |
|---|---|---|---|
| **Invariante** | el repo cumple propiedades verificables | janitor | barato |
| **Derivación** | un derivado es función de sus fuentes: `D = f(A₁…Aₙ)` | janitor de build | barato |
| **Semántica** | una propagación preserva sentido y legibilidad | agente | caro |

- El agente **escribe** reglas cuando el usuario habla y las **interpreta** al abrir el
  ciclo, pero nunca es quien las recuerda.
- El motor de cadencias es Python leyendo front matter. Corre sin API, sin red y sin
  créditos.
- Una sesión normal de registro no invoca ningún modelo caro.

**Se viola cuando.** Un artefacto que podría producirse por regla se produce por
inferencia. El síntoma es que el mismo insumo da resultados distintos en dos ejecuciones.

**Se verifica.** El test de replay (criterio 1 del brief): lo producido por janitors debe
reconstruirse con diff exactamente cero; lo producido por agentes, por equivalencia
semántica. **Si algo que debería ser determinista solo pasa el test semántico, hay agencia
donde debería haber una regla.** El replay es, además de prueba de regresión, un detector
de agencia mal ubicada.

---

## P4 — Sembrar y corregir

**Afirma.** El patrón de colaboración es siempre el mismo: el agente produce un borrador,
el humano corrige, y corregir cuesta una línea.

**Por qué.** Es lo único que hace tolerable el error del agente. Un sistema que exige
acierto del modelo es frágil; uno que asume error y lo abarata es robusto. También mantiene
la propiedad del contenido donde corresponde: el plan y la retrospectiva son del humano
aunque los haya empezado a escribir la máquina.

**Implica.**
- Se aplica al plan del ciclo, a la retrospectiva, a la clasificación de entradas, a la
  descripción inferida de una entidad, y a toda propuesta de estructura.
- Un artefacto sembrado se genera **una vez** y después pertenece al humano: ningún janitor
  vuelve a pisarlo.
- El agente propone en la forma más corregible posible: opciones concretas, no preguntas
  abiertas; una palabra de respuesta, no un formulario.

**Se viola cuando.** El agente regenera algo que el humano ya corrigió, o cuando corregir
exige más esfuerzo que escribir desde cero.

**Se verifica.** Medir el delta entre lo sembrado y lo que queda tras la corrección. Un delta grande y sostenido no es un fallo del usuario: es la señal de que el sembrado está mal calibrado.

**Curiosidad acotada.** Cuando el agente detecta una anomalía —no cualquier desviación, sino la que un humano responsable notaría de inmediato—, la señala en voz activa en vez de esperar a que se le pregunte. El límite es la alarma: como máximo unas pocas preguntas por apertura o cierre, reservadas para lo que genuinamente sorprendería a un especialista del dominio.

---

## P5 — Dirección del flujo

**Afirma.** La información fluye con reglas de gobernanza explícitas, y la dirección
determina cuánta autonomía tiene el sistema.

| Origen → destino | Autonomía |
|---|---|
| Entradas y tareas → proyecciones en entidades | automático, sin intervención |
| Entidades → `estrategia/` (capacidad, cadencias) | propuesta con aprobación humana explícita |
| Edición directa de `estrategia/` | solo humano |
| Referencias a `notas/` | cualquier dirección; es transversal |

**Por qué.** Lo que define la gestión de una persona —cuánto puede abarcar, con qué ritmo
vive— no puede ser modificado por inferencia. El sistema propone hacia arriba; nunca decide
hacia arriba.

**Implica.**
- Un cambio en `estrategia/` originado por el agente es siempre una propuesta pendiente de
  aprobación, nunca una escritura directa.
- El plan del ciclo, una vez corregido por el humano, queda fuera del alcance de los
  janitors.

**Se viola cuando.** El sistema ajusta la capacidad declarada del usuario porque observó
que no cumple sus planes. Ese es exactamente el comportamiento que P5 prohíbe.

**Se verifica.** Auditar el historial de Git: todo commit que toque `estrategia/` debe
tener aprobación humana registrada.

---

## P6 — Estructura mínima cerrada, interpretación abierta

**Afirma.** El sistema valida muy poco. Todo lo demás es territorio del usuario y del
agente.

**Núcleo cerrado**: identidad estable, fechas, pertenencia a una entidad, estado de una
tarea, gramática de cadencia. Eso es todo.

**Abierto**: qué tipos de entidad existen, qué campos llevan, qué significa "cliente
grande", cómo se organiza el árbol. `type` es *string libre*: el sistema lo indexa, no lo
valida contra un catálogo.

**Por qué.** Las categorías reales de un usuario no son anticipables. Un observatorio tiene
instrumentos y turnos; una PyME de insumos escolares tiene clientes y temporadas de compra;
una familia tiene profesionales de salud. Cualquier taxonomía que se imponga será
equivocada para el segundo usuario.

**Implica.**
- Un tipo de entidad es, como mucho, una plantilla de front matter más una lista de
  cadencias, declarado en Markdown. No hay editor de esquemas, ni validación fuerte, ni UI
  de configuración.
- El usuario define tipos **conversando**; el agente los escribe.
- La interpretación puede equivocarse sin consecuencias graves, porque P4 hace barata la
  corrección.

**Se viola cuando.** Aparece una lista cerrada de tipos permitidos, o un campo obligatorio
que no pertenece al núcleo, o una pantalla de configuración de esquemas.

**Se verifica.** Tomar un dominio ajeno al del autor —una PyME, una junta de vecinos— y
modelarlo sin tocar el código del motor. Si hace falta modificar `src/`, P6 no se cumple.

---

## Regla de desempate

Un desarrollador, tiempo escaso. Ante dos opciones que satisfacen los seis principios,
**gana la que reduce superficie**: menos archivos, menos comandos, menos reglas, menos
prompts que mantener. La visión completa está registrada y ordenada; el orden de
construcción parte siempre del núcleo que hace verdadera la promesa del nombre.
