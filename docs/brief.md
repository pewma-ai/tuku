# TUKU — Project Brief

2026-08-01, jpgil & Claude Fable

> `docs/brief.md` · Documento fundacional. Las especificaciones en `spec/` y las decisiones
> en `docs/decisiones/` se justifican por referencia a este documento. Si una decisión
> futura no puede derivarse de lo que aquí se afirma, o este brief está incompleto, o la
> decisión está equivocada. Ambos casos merecen un ADR.

---

## 1. Qué es

TUKU es un sistema de gestión personal para una persona que pertenece a múltiples
organizaciones a la vez. Registra lo que la persona hace, recuerda lo que la persona
olvida, y convierte la acumulación de ambas cosas en planes, alertas e informes.

El nombre viene de *tukulpan* — en mapudungun, recordar, traer a la memoria. Esa es la
promesa exacta del sistema: **lo que entró a TUKU vuelve solo cuando corresponde**, sin
que nadie tenga que acordarse de acordarse.

TUKU implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante
personal. Producto y metodología son cosas distintas y se versionan por separado: la
metodología describe cómo se gestiona; TUKU es una herramienta que la ejecuta.

## 2. Para quién

Para una persona con vida multidimensional: trabajo formal, emprendimientos paralelos,
familia, responsabilidades cívicas. Cada dimensión tiene sus propios ritmos, compromisos
y vocabulario, y ninguna herramienta de las que usa en una dimensión ve a las demás.

El usuario de referencia no es un desarrollador. Es alguien como la dueña de una PyME de
insumos escolares: gestiona clientes, cada cliente tiene sus ciclos ("vendí lápices hoy,
ofrecer reposición en tres meses"), y hoy todo eso vive en su cabeza y en cuadernos. El
desarrollador que puede operar todo por terminal es un caso particular bienvenido, no el
centro del diseño.

El sistema habla el idioma del usuario. La primera lengua es el español; los nombres de
las primitivas (tarea, bitácora, entidad, cadencia, ciclo) son palabras del castellano
corriente, no anglicismos técnicos.

## 3. El modelo

### 3.1 El ciclo de gestión

Gestionar tiene la misma forma siempre, en un observatorio y en un almacén:

```
objetivos generales → recursos → capacidad → plan → acciones → aprendizajes
```

Los aprendizajes alimentan los objetivos del ciclo siguiente. TUKU existe para sostener
ese lazo: sin sistema, las acciones se registran mal, los aprendizajes se pierden y cada
ciclo empieza de cero.

### 3.2 Tres ejes, dos cruces

El ciclo de gestión se proyecta sobre tres ejes:

| Eje | Pregunta | Materialización |
|---|---|---|
| **Temporal** | ¿cuándo? | ciclos, con su plan y resultados |
| **Organizacional** | ¿sobre qué? | entidades: áreas, proyectos, clientes, lo que el usuario defina |
| **Deliberativo** | ¿por qué así? | notas: ideas desarrolladas y conclusiones sedimentadas |

Los ejes se cruzan exactamente en dos puntos, y esos dos puntos son las primitivas
centrales del sistema:

- La **entrada de bitácora**: una acción fechada que pertenece a una entidad.
- La **tarea**: nace de una entidad y se ejecuta dentro de un ciclo.

De este cruce se deduce la regla de oro del modelo de datos: entrada y tarea se escriben
**una sola vez, en un lugar canónico**, y todo lo demás — la bitácora del ciclo, la página
de la entidad, el informe anual — son **proyecciones** recomputables de ese canónico. Nada
se copia; todo se proyecta.

**El eje deliberativo no cruza: toca.** Una nota puede declarar una entidad, y entonces se
proyecta en su página; pero no tiene fecha, no pertenece a un ciclo, no la despiertan las
cadencias y no aparece en el cierre. Es el artefacto más inerte del sistema y eso es
deliberado — el pensamiento no tiene ritmo propio, y forzarle uno sería convertirlo en
tarea. Su especificación es [`spec/nota.md`](../spec/nota.md).

### 3.3 El ciclo no es la semana

El ciclo lo define la vida del usuario, no el almanaque: un turno de faena de martes a
martes, un descanso de miércoles a lunes, una semana ISO para quien trabaja 9-a-5, un
semestre académico. El sistema no impone calendario; lee el del usuario desde
sus cadencias.

### 3.4 La cadencia es la pieza central

Una cadencia es una regla que produce artefactos en el tiempo: bitácoras nuevas, tareas
nuevas, alertas. Absorbe lo que en otros sistemas son "rituales" cableados — abrir y
cerrar ciclo son cadencias que disparan procesos, editables como cualquier otra regla.

Tres orígenes con herencia (sistema → tipo de entidad → entidad concreta, donde lo
específico gana) y cuatro formas de disparo:

1. **Absoluta** — función del calendario. *El día 1, pagar cuentas.*
2. **Relativa a evento** — evento en una entidad + Δt. *Venta hoy → contactar en 3 meses.*
3. **Por ausencia** — se dispara porque no pasó nada. *Proyecto sin actividad en 4 semanas.*
4. **Por completitud** — al cerrarse una tarea se activa otra regla.

El momento de mayor valor del producto ocurre aquí: abrir el ciclo y encontrar lo que se
había olvidado. La forma 3 es su complemento exacto — nadie recuerda lo que dejó de hacer.

### 3.5 El informe es la memoria

Markdown no es una base de datos: no se consulta el año 2016 con una query. La memoria de
largo plazo del sistema son sus **informes** — el cierre de cada ciclo, los resúmenes
anuales — generados con estructura estable y front matter, consultables por humanos y por
agentes. El detalle crudo se conserva por año y no se destruye nunca, pero la consulta
histórica se responde por informes. Un informe pobre es memoria perdida: por eso la
calidad del cierre de ciclo es un problema de arquitectura, no de redacción.

## 4. Principios

### P1 — La arquitectura Markdown es el diseño; todo lo demás la sigue

Primero se diseña cómo viven los archivos: qué es canónico, qué es derivado, qué front
matter llevan, cómo se anidan. GUI, motor, deployment y agentes son consecuencias. Prueba
operativa: si la interfaz necesita lógica propia para que los archivos tengan sentido, la
arquitectura de archivos está mal.

La elección de Markdown es deliberada: texto plano legible a 1, 5 y 20 años,
versionable con Git, independiente de todo proveedor. Los datos del usuario deben
sobrevivir al motor, a PEWMA.AI y a la industria entera de LLMs.

### P2 — Operable a mano; los agentes toman lo tedioso

Un usuario suficientemente disciplinado debe poder operar el sistema completo con un
editor de texto. Los procesos se escriben para ser ejecutables por un humano **o por un
agente de inteligencia media** — sin trucos de prompting, sin razonamiento de frontera.
Lo que se delega a agentes es lo tedioso o intensivo en tiempo, nunca lo esencial.

### P3 — Determinismo primero, agencia al final

Todo lo que puede garantizarse con un script, se garantiza con un script. La coherencia
del sistema se divide en tres familias con garante y costo distintos:

| Familia | Qué garantiza | Garante | Costo |
|---|---|---|---|
| **Invariante** | el repo cumple propiedades verificables | janitor | barato |
| **Derivación** | un derivado es función de sus fuentes: `D = f(A…)` | janitor de build | barato |
| **Semántica** | una propagación preserva sentido y legibilidad | agente LLM | caro |

El agente escribe reglas cuando el usuario habla y las interpreta al abrir el ciclo, pero
**nunca es quien las recuerda**. Un recordatorio que depende de la memoria de un modelo no
es un recordatorio.

### P4 — Sembrar y corregir

El patrón de colaboración humano-agente es siempre el mismo: el agente produce un
borrador (plan, retrospectiva, clasificación, estructura propuesta), el humano corrige, y
la corrección es barata — una línea, una palabra. Este patrón absorbe el error del agente
sin ceremonia y mantiene la propiedad del contenido en el humano.

### P5 — Dirección del flujo

La información fluye con reglas de gobernanza explícitas: de la actividad hacia las
entidades, automático; de las entidades hacia la capacidad y las cadencias, solo por
propuesta con aprobación humana; el plan del ciclo y la retrospectiva, una vez corregidos
por el humano, son del humano. El sistema propone hacia arriba; nunca decide hacia arriba.

### P6 — Estructura mínima cerrada, interpretación abierta

El sistema valida muy poco: identidad estable, fechas, pertenencia, el estado de una
tarea. Todo lo demás — qué tipos de entidad existen, qué campos llevan, qué significa
"cliente grande" — es territorio del usuario y del agente. Un tipo de entidad es una
plantilla más una lista de cadencias declaradas en Markdown; no hay editor de esquemas ni
catálogo cerrado.

## 5. Forma del sistema

### 5.1 Motor y perfil

Dos artefactos con ciclos de vida distintos, nunca mezclados:

- El **motor**: código, janitors, procesos, plantillas. Se instala vía pipx, se versiona
  por PEWMA.AI, vive fuera de los datos.
- El **perfil**: un repositorio Git por usuario con sus bitácoras, tareas, entidades y
  notas. Propiedad del usuario, portable, con su versión de esquema declarada.

Un motor sirve N perfiles. El diseño local es el diseño del servidor: pasar de la máquina
del usuario a una VM multiusuario cambia dónde viven los perfiles, no el modelo.

### 5.2 Los artefactos del ciclo

La apertura de un ciclo declara el ciclo; el cierre produce su informe:

| Artefacto | Dueño | Contenido |
|---|---|---|
| `plan_FECHA_tipo` | sembrado por el agente, corregido por el humano | intención, tareas del ciclo, restricciones |
| `resultados_FECHA_tipo` | sembrado, corregido | avances, desviaciones, aprendizajes |

No hay archivo de bitácora del ciclo: las entradas se escriben en `entradas/`, particionadas
por mes, y la vista del ciclo es una proyección que se congela dentro de `resultados_*` al
cerrar. Así no queda ninguna zona donde el usuario pueda escribir sobre una proyección.

Un archivo, un dueño. Las entradas llevan prefijo estructurado —fecha, entidad,
clasificación— y las clasificaciones (`hito`, `decision`, `senal`, extensibles) permiten que
el informe de cierre parta de un filtro determinista que el agente redacta, no de una
inferencia que el agente inventa.

**No hay clasificación de fricción.** Las desviaciones no se etiquetan al escribir: se
descubren en el cierre contrastando lo esperado de cada entidad con lo efectivamente
registrado. Pedirle al usuario que rotule sus propios fracasos mientras trabaja es pedirle lo
que no va a hacer — en el corpus real, cero veces.

### 5.3 El primer día

Un perfil recién creado no tiene historia, y el valor de TUKU crece con la historia. La
respuesta no es un asistente de configuración: es invertir la carga. El primer día el
usuario ve los días restantes de su ciclo y un chat que pregunta **"¿qué quieres registrar
hoy?"**. Registra — por texto o por voz. La estructura emerge: el agente ve nombres que se
repiten y propone entidades; ve pagos que se repiten y propone cadencias; el usuario
aprueba con una palabra. El onboarding no es una feature: es el sistema funcionando sobre
un perfil vacío.

Las cadencias de sistema (apertura, cierre, higiene) vienen sembradas y son editables,
de modo que el primer cierre de ciclo ocurre solo, aunque el usuario no haya configurado
nada.

## 6. Lo que TUKU no es

- **No es un segundo cerebro genérico.** Existe para gestionar, no para coleccionar. El eje
  deliberativo tiene peso real —notas con clasificación, enlaces justificados e índice
  derivado (`spec/nota.md`)— pero está al servicio del ciclo de gestión: una nota se escribe
  para decidir mejor, no para completar una colección. TUKU no compite con Obsidian; escribe
  Markdown plano que Obsidian lee, y esa es toda la relación.
- **No es una plataforma de esquemas configurables.** No hay editor de tipos, ni
  validación fuerte de campos, ni UI de configuración. Notion ya existe.
- **No es un ejército de agentes.** Hay una sola interfaz conversacional visible. Las
  funciones internas (planificar, vigilar, analizar) son eso: funciones, no personajes.
- **No es un almacén de secretos.** Contactos y contexto, sí; credenciales y contraseñas,
  jamás. Cada perfil es visible solo por su dueño.
- **No decide.** Propone planes, alerta ausencias, sugiere estructura. La aprobación es
  siempre humana y el costo de corregir es siempre una línea.

## 7. Criterios de éxito

El diseño se considera correcto cuando:

1. **Replay**: desde un perfil vacío más el log de entradas y eventos de tareas, el motor reconstruye el estado completo. El criterio se separa según el garante. Todo lo producido por janitors —tareas abiertas, entidades vigentes, proyecciones, índices— debe reconstruirse con diff exactamente cero: son derivaciones deterministas y cualquier diferencia es un defecto. Lo producido por agentes —informes de cierre, descripciones inferidas, planes sugeridos— se evalúa por equivalencia semántica: los mismos hechos, las mismas desviaciones señaladas, las mismas tareas priorizadas, aunque la redacción difiera. Este es el test estructural del modelo canónico, y la frontera entre ambos criterios es también su segundo hallazgo: si algo que debería ser determinista solo pasa el test semántico, es que hay juicio del agente donde debería haber una regla.
2. **Operación manual**: una persona ejecuta un ciclo completo (apertura, registro,
   cierre) siguiendo solo los procesos en Markdown, sin agente, y el resultado es válido.
3. **Recuerdo**: una cadencia declarada meses atrás produce su tarea en el ciclo correcto
   sin intervención de ningún LLM.
4. **Foco conversacional**: abrir una entidad y modificarla conversando resulta ser una
   llamada al agente con el path de la sección como contexto restringido. Si exige
   arquitectura adicional, el modelo de secciones está mal planteado.
5. **Frugalidad**: una sesión normal de registro no invoca ningún modelo caro; el LLM de
   juicio aparece solo en apertura, cierre y peticiones explícitas.

## 8. Restricciones de construcción

Un desarrollador, tiempo escaso, alto conocimiento de AI. Toda decisión de alcance se
evalúa contra esa realidad: ante la duda, la opción que reduce superficie gana. La visión
completa — canal Telegram con audio, tres renderizadores, servidor multiusuario,
federación entre perfiles vía MCP — está registrada y ordenada, pero el orden de
construcción parte del núcleo que hace verdadera la promesa del nombre: **cadencias,
backlog canónico de tareas y captura conversacional**. Todo lo demás es consecuencia o
espera.
