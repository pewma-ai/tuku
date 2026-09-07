# Sesiones de ejemplo TUKU — FAENA

> Corpus de referencia, ficticio y público. Personas, lugares, instituciones y proyectos están anonimizados, y la correspondencia con sus originales **no vive en este repositorio ni en ninguna parte pública**. Cualquier nombre que aparezca acá se trata como el nombre real de este corpus, no como un seudónimo de alguien.

> [!note] Para qué sirve este corpus
> Ground truth principal y columna de la escalera de estados que recorren los epics. Su fecha de arranque, 2026-08-11, es la que fijan los tests.
>
> Su par es [`referencia-pyme.md`](referencia-pyme.md), en un dominio ajeno. Acá el autor del diseño registra su propio trabajo, con vocabulario que la spec ya conoce; el sesgo es deliberado y pyme existe para compensarlo.
>
> **No declara ninguna `**cadencia**`.** El ritmo lo pone el turno, no un calendario. La tercera marca de la ontología cerrada solo tiene ejemplo en pyme.

## El usuario

**Damián Ulloa** (DUL), 47 años, jefe del grupo de software de un observatorio astronómico en el norte de Chile. Vive en la costa y sube a **Faena**, el sitio de montaña, por turnos.

Su ciclo no es la semana: es el turno. Nueve días arriba, cuatro de descanso, sin corte en domingo, con fechas que se mueven según el clima. Durante parte del turno asume además el rol rotativo de **Jefe de División**, que se recibe y se entrega con hora exacta y parte el día en dos responsabilidades.

Trabaja en tres frentes que no se separan: operación del observatorio, adopción de IA en la organización, y proyectos propios como TUKU. Tres hijos, **Mateo** (22, ingeniero de software), **Lucas** y **Gaspar**. Dos departamentos, uno arrendado y otro propio, cuya administración entra a la bitácora igual que el trabajo: es el mismo día.

Lo que trae al sistema: escribe mucho y ordena poco, sus pendientes se arrastran de turno en turno sin que nadie los promueva, y el aprendizaje de una contingencia se pierde antes del turno siguiente.

---

# Parte 1: Input en Lenguaje Natural (Sesiones de Dictado)

## Turno Faena (11 al 19 de Agosto de 2026)

### Martes 11 de Agosto

* "Subí a Faena e inicié el turno, Fabina Méndez está presente acá en el cerro."
* "Estuve viendo que el agente Hermes con las reglas de MaC toma demasiado tiempo; siento que estoy repitiendo lógica que el modelo ya maneja internamente. Tengo que investigar cómo minimizar reglas aprovechando el aprendizaje nativo de los agentes."
* "Nos pidieron identificar exhaustivamente las interfaces de ODIP. Quedó pendiente reunirme con Víctor Lagos para dividirlas en tareas manejables."
* "Propuesta de marco de trabajo de casos de uso con Azure LLM redactada y lista para presentársela a Fabina Méndez."
* "Terminamos la reunión con Fabina Méndez: Carlos Silva y Víctor Lagos aprobaron el nuevo esquema de exploraciones operacionales; dejamos fijada la primera reunión con practicantes para el viernes 14 (yo veo la logística y Fabina los contacta); Alicia Abarca nos mandó el listado completo; el director dio visto bueno para colaboraciones con Mauricio Barra y proyectos de investigación; y la tesis de Javier Castro avanza con el repositorio de Carla Fuentes."
* "Tuve una reunión informal con un alto cargo de IT aficionado a la ciencia ficción."
* "Le mandé la boleta de gastos comunes del Depto Centro a la administradora Carmen Navarro por WhatsApp."
* "Hoy le envié un correo a Xander Gálvez de IT solicitando disponibilidad para reunirnos a ver el tema de IA en Faena."
* "Ya implementé el experimento de Serendipia en el sistema para darle más espontaneidad al agente."
* "Hice la consulta presencial por el standing desk de Patricio Soto."

---

### Miércoles 12 de Agosto

* "Eliminé el filtro de madurez de 5 minutos del janitor de git en modo automático."
* "Revisamos con Fabina Méndez el diccionario de MetricDB para la tesis de Javier Castro. Por confidencialidad no se le pueden entregar los manuales directos, así que acordamos hablar con Carla Fuentes para armar presentaciones resumen integrando varios documentos."
* "Le presenté a Fabina el marco de trabajo de casos de uso con Azure LLM y dejé creada la nota formal con las pautas de gobernanza para emitir API keys."
* "Proyecto del paper técnico archivado."
* "En temas personales: pagué la sesión con el psicólogo Camilo Aguirre y regularicé los gastos comunes del Depto Cerro con Mónica Castro pagando dos meses juntos por un mes de atraso acumulado."
* "A las 11:00 me reuní con Rodrigo Álvarez y Tomás Toledo de Casa Matriz por la versión 2 de la plataforma de servicios. Pidieron prioridades y aporté con IA: LLM en máquinas NVIDIA y un harness para agentes como OpenCode. Quedo a la espera de sus requerimientos técnicos con Rodrigo como contacto directo."

---

### Jueves 13 de Agosto

* "Dejé cargando el auto eléctrico 94 para que Cristóbal Carrasco lo pueda usar mañana viernes temprano."
* "Le recordé al equipo de SAF que la API de LASCOR tiene prioridad."
* "Irene Morales tuvo un inconveniente médico y tuvo que bajar de Faena a las 7 AM."
* "Estuve reunido con Xander Gálvez y Tomás Toledo de Casa Matriz. Coincidimos en aumentar la comunicación entre Casa Matriz y Faena para romper silos. Están esperando la estrategia del directorado, lo que calza con el apoyo de Elena Sepúlveda. Tomo el consejo de Mauricio Barra de capitalizar todo lo que haga en entregables tangibles. En Casa Matriz perciben la IA con desfase y más que la fuga de datos les preocupa el riesgo real de descontrol de agentes. Sugirieron presentar casos aplicados en los Data Coffee de Fabina. Les envié por correo la recopilación curada sobre gobernanza de agentes IA."
* "Apoyé a Raúl Araya ajustando la justificación técnica de la solicitud de tiempo técnico de noviembre para el interferómetro."
* "Marcelo Jensen me invitó a integrarme al comité de revisión Phase A del proyecto Multi Site Operations."
* "Despaché el correo de la propuesta Concurso I+D Tecnológico 2027 a Carlos Silva, Fabina Méndez y Víctor Lagos."
* "Dejé listo el registro de formularios de API keys de Azure LLM y declaré mi propia API key bajo el caso de uso 'responsible vibe coding', con su nota conceptual lista."
* "Decidí que en el próximo turno voy a avanzar fuerte con Streamlit para operaciones y el pendiente de fuerzas de M1."

---

### Viernes 14 de Agosto

* "Reunión lista con Carla Fuentes, Fabina Méndez y Florencia Morales por la tesis de Javier Castro: acordamos compilar al vuelo el diccionario de puntos PLC del espectrógrafo desde MetricDB, Carla subió el dataset a GitHub, le consultaré a Nelson Morales sobre ingesta y organizaremos inducción en GitHub para Florencia."
* "A las 14:00 terminó el traspaso de turno y asumí formalmente como Jefe de División en Faena, justo con pronóstico de clima complicado."
* "Le envié a Esteban Parra las condiciones del marco Azure LLM y le emití la primera API key oficial a Bernardo Salinas para su proyecto exploratorio en exploraciones operacionales."
* "Repositorio de exploraciones operacionales finalizado y probado con dos solicitudes de API keys. Decidí formalizar Responsible Vibe Coding como proyecto, habilitando generación autónoma de resúmenes de sesiones y el repositorio Multi-repo Agentic Workflow para gobernar múltiples subdirectorios con reglas agénticas."

---

### Sábado 15 de Agosto

* "Salió excelente la primera reunión de exploraciones operacionales con estudiantes de práctica: 1 hora, 5 alumnos y 4 presentaciones de proyectos IA, muy buen espacio colaborativo."
* "Hice el One2One con Valeria Pizarro y le pedí a Víctor Lagos que defina sus primeros objetivos directamente con ella."
* "Dejé lista una diapositiva de Responsible Vibe Coding para presentarla en los próximos Data Coffee de Fabina Méndez."
* "Carlos Silva aceptó la propuesta general del grupo de soporte de datos y pidió vincularla al desarrollo de procesos sumando a Jorge Muñoz (responsable de mantenimiento predictivo y RCA); agendamos reunión para el lunes 17."
* "Dato importante: Alejandro Palma me informó que en noviembre se reunirá el Comité Conjunto de Operaciones (Faena, Ciencia e Ingeniería) y uno de los temas centrales será la Estrategia de Inteligencia Artificial."
* "Reflexión del almuerzo: el pipeline de mi tesis de grafos (Markdown crudo procesado con IA hacia artefactos finales) es el mismo patrón de PILWA para TUKU en PEWMA y es directamente exportable a la documentación de soporte de datos."
* "Se desató una emergencia por mal tiempo severo en Faena entre las 17:00 y las 22:00. Mi labor como Jefe de División absorbió toda la capacidad técnica. Elaboré el Plan de contingencia por mal tiempo de agosto 2026 para coordinar la logística y turnos del equipo."

---

### Domingo 16 de Agosto

* "Jornada dominical dedicada completa al rol de Jefe de División por la emergencia climática: les avisé a los colegas que la subida del martes se pospone al miércoles, actualicé la planificación de turnos de software, reasigné roles operacionales en telescopios e instrumentos (TSO, TCU, ITOM), aseguré suministros y emití el comunicado general a todo el observatorio."

---

### Lunes 17 de Agosto

* "A las 14:00 entregué el turno de Jefe de División a César Espinoza con todos los planes de contingencia en plena ejecución y una buena gestión cerrada."
* "Tuvimos reunión a las 16:30 con Carlos Silva, Jorge Muñoz y Fabina Méndez: acordamos el Go para la postulación Concurso I+D Tecnológico 2027, enfocada en telemetría y análisis de logs para mantenimiento predictivo y RCA usando el ranking de criticidad de Jorge; voy a preparar la versión pulida para coordinar con Universidad Sur y Universidad Centro."
* "El Plan de contingencia por mal tiempo resultó sumamente útil; se lo compartí a Mauricio Barra y a César Espinoza."
* "Asumí la administración de la instancia de Azure OpenAI (`faenaopenai`), procesé dos formularios adicionales de exploraciones operacionales aprobados por Fabina Méndez y le mandé a Víctor Lagos el esquema de gobernanza de llaves."
* "Idea: abrir un canal o espacio de discusión para la comunidad interesada en IA para compartir experimentos y debatir abiertamente."
* "Estuve revisando la documentación de soporte de datos y el concepto operacional de Carlos Silva: coincide con el modelo de TUKU al terminar en acción y aprendizaje sistematizado, pero hace falta integrar el conocimiento tribal. Los espacios informales de conversación entre especialistas (como vimos en la reunión de estudiantes de exploraciones operacionales) producen un aprendizaje colectivo insustituible."

---

### Martes 18 de Agosto

* "Reunión con Nelson Morales sobre software del interferómetro y CINTILATOR: definimos los pendientes para el próximo turno (corrección de SEQ.CENTERSC por software, FT MODE en CINTILATOR con Alex, revisión del commit de polarización y tablas faltantes del 5 de agosto)."
* "Armonicé las fechas de vacaciones y permisos del equipo de software en Faena, y dejamos confirmada la bajada para mañana miércoles de madrugada por el hielo en la carretera."
* "En la reunión con Carlos Silva y Víctor Lagos sobre el roadmap de operaciones guiadas por datos, Carlos compartió que Phase B exige gobernanza formal; acordamos que el equipo de soporte de datos implementará la estrategia operativa de forma iterativa, apalancando la gobernanza que ya testeamos en exploraciones operacionales."
* "Cerramos la jornada con recreación en la nieve con el equipo y labores administrativas. Además, grabé tres intervenciones explicando el observatorio para las cámaras de la televisión internacional."

---

### Miércoles 19 de Agosto

* "Bajada de Faena de madrugada y turno cerrado."
* "Le mandé el calendario de turnos de Soporte a Alicia Abarca."
* "Marqué como comisionado en Jira el ticket CRB-1003427 sobre el proceso de lecciones aprendidas."
* "Despaché el correo de wrap-up de la propuesta Concurso I+D Tecnológico 2027 a Carlos Silva, Fabina Méndez y Jorge Muñoz con los casos de uso de mantenimiento predictivo y RCA."
* "Dejé lista la versión de agosto 2026 del documento conceptual de soporte de datos estructurado en sus tres pilares (Operación, Desarrollo y Gobernanza) para la próxima reunión del grupo."
* "Me citaron a una tercera entrevista extendida para la televisión internacional; interesante el patrón de visibilidad en medios."
* "En lo personal, ayer quedó pagada la sesión con el psicólogo Camilo Aguirre."

---

## Período de Descanso (20 al 23 de Agosto de 2026)

### Jueves 20 de Agosto

* "Estamos coordinando con mi hijo Mateo la entrega del Depto Centro para que se instale en enero; tengo pendiente coordinar y avisarle con tiempo a la administradora Carmen Navarro."
* "En la máquina virtual de Oracle se nos agotó la cuota de OpenRouter por alto consumo de tokens (más del 50% por Serendipia y 99% acumulado por contexto persistente). Pausé Serendipia y configuré un reinicio horario de contexto pasando únicamente las últimas 100 líneas de la bitácora; además, como Hermes no soporta Groq, sumé Google como fallback."
* "El mecanismo de Serendipia es muy potente y da para escribir un paper o nota técnica en GitHub Gist, pero requiere diseñar bien una caché porque sin optimización llegó a consumir 30 millones de tokens al día; calza perfecto con la estrategia de visibilidad técnica."

---

### Viernes 21 de Agosto

* "Actualicé mis notas de Perfil y de Guía de Voz en primera persona, incorporando los hallazgos del análisis con IA sobre mis correos e interacciones previas."
* "Cerré el análisis retrospectivo de lo ocurrido en el último turno de Faena."
* "Para el próximo turno en Faena definimos con Fabina Méndez cómo estructurar y segmentar las sesiones con estudiantes (como las de Oficina Regional) para experimentos de IA, adaptando la dinámica a la audiencia."
* "Me contactó Agustín Díaz de la Organización para dar charlas online de captación de estudiantes de Universidad Sur y eventualmente otra internacional en inglés para septiembre u octubre. Queda como reflexión que mi vocería institucional y en otros ámbitos como la paya viene creciendo, pero tengo que acelerar el posicionamiento público visible como especialista en IA."
* "Decidí no ir a kinesiología en Centro Kine durante este descanso, lo dejo postergado."
* "Lucas está desarrollando con mucha fuerza la lectura y escritura de cómics; su veta humanista está aflorando y hay que evaluar opciones para apoyarlo, como un taller de anime."
* "Mateo está mostrando avances muy sólidos en su primer año como ingeniero de software enfocado en IA. Compartimos trabajo en paralelo con enfoques propios pero con los mismos principios: centralidad en Markdown, uso fluido de agentes y control total sobre los resultados delegando la ejecución a sistemas agénticos."
* "Creé un espacio para recopilar artículos web interesantes con fecha, trazabilidad y comentarios breves, partiendo con Los Artefactos del Pensamiento de Psychology Today."

---

### Sábado 22 de Agosto

* "Compras familiares y actividades de hoy resueltas: compré el traje de baño para Gaspar, compré el regalo de cumpleaños para Nico, coordiné con la mamá la compra de la camisa a cuadros para Lucas, y salí con los niños a jugar realidad virtual a Arcade VR, estuvo excelente."

---

### Domingo 23 de Agosto

* "Son las 03:00 y estuve varias horas destilando lo que funciona de mi sistema de gestión hacia el proyecto TUKU de PEWMA. Definí partir de forma ultra minimalista con lo que ya tenemos (brief, principios y specs) y validar con ejemplos concretos y bitácoras reales para que el sistema genere la documentación de forma clara para el equipo; también queda pendiente mapear qué fricciones no me gustan de mi sistema actual para no repetirlas en TUKU. Pauso la sesión por ahora para retomarla después porque condensar seis meses de práctica es complejo."
* "Compré el pasaje en Bus interurbano para el viaje de subida a Faena del próximo turno este martes 25 de agosto."
* "Formulé el patrón arquitectónico en tres niveles para TUKU: un Coordinador con impersonación contextual, Supervisores de dominio para bitácora, ámbito y tareas, y subagentes de ejecución con contexto limpio."
* "Fuimos al cumpleaños de Nico en Parque Infantil con Lucas."

---

# Parte 2: Tabla de Verdad (Ground Truth — Formato Bitácora TUKU)

> [!tip] Ground Truth para benchmarking de modelos
> La entrada canónica que corresponde a cada dictado de la Parte 1, según [`spec/bitacora.md`](../../spec/bitacora.md): `- HH:MM - [[ambito]] ~~(Hecho)~~ **clasificacion**: cuerpo`. Mide si un agente convierte habla desestructurada en entradas que se sostienen solas.
>
> **Las horas no vienen del dictado**: se derivan de la jornada que el dictado describe. La clasificación abierta usa el vocabulario del autor, no uno que fije TUKU.

> [!question] Pendiente de decisión #REVISAR
> 52 `~~(Hecho)~~` contra 15 `**pendiente**`: la mayoría de los cierres no tiene pareja previa, nacen y se cierran el mismo día porque así fue dictado. [`spec/pendientes.md`](../../spec/pendientes.md) dice que `~~(Hecho)~~` cierra un pendiente preexistente. O el corpus abre el pendiente implícito en la misma entrada, o la invariante admite el cierre sin pareja. Lo decide el escenario `002-004`, no el corpus.

## Turno Faena (11 al 19 de Agosto de 2026)

### Martes 11 de Agosto
> [!tldr]
> Subida a Faena e inicio de turno con Fabina Méndez presente en el cerro. Reunión clave de exploraciones operacionales que aprueba el nuevo esquema de practicantes y las colaboraciones de investigación. Avances en ODIP y en IA para Faena con coordinación hacia IT, más gestión personal de gastos comunes del Depto Centro.

- 07:30 - [[jefatura]] ~~(Hecho)~~: subir a Faena e iniciar turno
- 07:45 - [[exploraciones-operacionales]] **señal**: Fabina Méndez presente en el cerro durante la primera mitad del turno
- 09:15 - [[tuku]] **observación**: el agente Hermes con las reglas de MaC toma demasiado tiempo; hay lógica repetida que el modelo ya maneja internamente
- 09:20 - [[tuku]] **pendiente**: investigar cómo minimizar las reglas de MaC aprovechando el aprendizaje nativo de los agentes
- 10:00 - [[transformacion-digital]] **señal**: solicitada la identificación exhaustiva de las interfaces de ODIP
- 10:05 - [[transformacion-digital]] **pendiente**: reunirse con Víctor Lagos para dividir las interfaces de ODIP en tareas manejables
- 11:00 - [[faena-ai]] ~~(Hecho)~~: redactar la propuesta de marco de trabajo de casos de uso con Azure LLM
- 11:05 - [[faena-ai]] **pendiente**: presentar a Fabina Méndez la propuesta de marco de casos de uso con Azure LLM
- 12:30 - [[exploraciones-operacionales]] **hito**: reunión con Fabina Méndez cerrada; Carlos Silva y Víctor Lagos aprobaron el nuevo esquema de exploraciones operacionales
- 12:35 - [[exploraciones-operacionales]] **decisión**: primera reunión con practicantes fijada para el viernes 14 de agosto; Damián Ulloa ve la logística y Fabina Méndez los contacta
- 12:40 - [[exploraciones-operacionales]] **progreso**: Alicia Abarca envió el listado completo de practicantes
- 12:45 - [[exploraciones-operacionales]] **decisión**: el director dio visto bueno a las colaboraciones con Mauricio Barra y a la integración de proyectos de investigación
- 12:50 - [[tesis-javier-castro]] **progreso**: la tesis de Javier Castro avanza con el repositorio de Carla Fuentes; los manuales no se entregan directos por confidencialidad
- 12:55 - [[tesis-javier-castro]] **pendiente**: conversar el diccionario de MetricDB con Fabina Méndez el miércoles 12 de agosto
- 15:20 - [[faena-ai]] **nota**: reunión informal con un alto cargo de IT, aficionado a la ciencia ficción
- 16:40 - [[arriendo-depto-centro]] ~~(Hecho)~~: enviar la boleta de gastos comunes del Depto Centro a Carmen Navarro por WhatsApp
- 17:10 - [[faena-ai]] ~~(Hecho)~~: enviar correo a Xander Gálvez de IT solicitando disponibilidad para reunirse por IA en Faena
- 18:30 - [[mac-personal]] ~~(Hecho)~~: implementar el experimento de Serendipia para dar más espontaneidad al agente
- 19:00 - [[jefatura]] ~~(Hecho)~~: hacer la consulta presencial por el standing desk de Patricio Soto

---

### Miércoles 12 de Agosto
> [!tldr]
> Jornada centrada en IA y cierre de pendientes. Con Fabina Méndez se revisa el diccionario de MetricDB para la tesis, con presentaciones resumen como salida ante la restricción de confidencialidad, y se presenta el marco Azure LLM dejando creada la nota de gobernanza de llaves. Reunión con Casa Matriz por la versión 2 de la plataforma, con la IA aportada como prioridad. En lo operativo, paper archivado y gastos personales regularizados.

- 08:40 - [[mac-personal]] ~~(Hecho)~~: eliminar el filtro de madurez de cinco minutos del janitor de git en modo automático
- 10:15 - [[tesis-javier-castro]] ~~(Hecho)~~: conversar el diccionario de MetricDB con Fabina Méndez el miércoles 12 de agosto
- 10:30 - [[tesis-javier-castro]] **fricción**: por confidencialidad no se pueden entregar los manuales directos a Javier Castro
- 10:35 - [[tesis-javier-castro]] **decisión**: hablar con Carla Fuentes para armar presentaciones resumen que integren varios manuales, en vez de entregar los manuales
- 11:00 - [[transformacion-digital]] **hito**: reunión con Rodrigo Álvarez y Tomás Toledo de Casa Matriz por la versión 2 de la plataforma de servicios de IT
- 11:45 - [[transformacion-digital]] **señal**: IT pidió opinión y prioridades; se aportó IA, con LLM en máquinas NVIDIA y un harness para agentes como OpenCode
- 11:50 - [[transformacion-digital]] **nota**: Rodrigo Álvarez queda como contacto directo del grupo; no hay pendientes hasta que IT envíe sus requerimientos técnicos
- 15:00 - [[faena-ai]] ~~(Hecho)~~: presentar a Fabina Méndez la propuesta de marco de casos de uso con Azure LLM
- 15:30 - [[exploraciones-operacionales]] ~~(Hecho)~~: crear la nota Marco Azure LLM para Proyectos Exploratorios de IA con las pautas de gobernanza para emitir API keys
- 17:00 - [[paper-conferencia]] **decisión**: archivar el proyecto del paper técnico
- 20:10 - [[salud-personal]] ~~(Hecho)~~: pagar la sesión con el psicólogo Camilo Aguirre
- 20:30 - [[personal]] ~~(Hecho)~~: regularizar los gastos comunes del Depto Cerro con Mónica Castro
- 20:35 - [[personal]] **señal**: se detectó un mes de atraso acumulado en los gastos comunes del Depto Cerro y se pagaron dos meses juntos para quedar al día

---

### Jueves 13 de Agosto
> [!tldr]
> Alineación con Casa Matriz en gobernanza de agentes de IA, con envío de referencias curadas. Despachada la propuesta del Concurso I+D Tecnológico 2027. Apoyo técnico en la solicitud de tiempo del interferómetro, invitación al comité de revisión de Multi Site Operations y primeras gestiones de API keys en Azure.

- 07:00 - [[jefatura]] **señal**: Irene Morales tuvo un inconveniente médico y bajó de Faena a las 07:00
- 09:10 - [[jefatura]] ~~(Hecho)~~: recordar al equipo de SAF que la API de LASCOR tiene prioridad
- 10:30 - [[faena-ai]] **hito**: reunión con Xander Gálvez y Tomás Toledo de Casa Matriz
- 10:40 - [[faena-ai]] **decisión**: aumentar la comunicación entre Casa Matriz y Faena para romper silos, con acuerdo de ambos por experiencia previa en organizaciones distribuidas
- 10:45 - [[faena-ai]] **señal**: Casa Matriz espera la estrategia del directorado, lo que calza con el apoyo de Elena Sepúlveda
- 10:50 - [[faena-ai]] **observación**: en Casa Matriz la percepción de la IA va dos o tres años atrás; preocupa menos la fuga de datos que el riesgo real de que un agente se descontrole, sea por malicia o por error
- 10:55 - [[faena-ai]] **decisión**: presentar casos de uso aplicados en los Data Coffee que gestiona Fabina Méndez, por sugerencia de Casa Matriz
- 11:10 - [[faena-ai]] ~~(Hecho)~~: enviar a Tomás Toledo y Xander Gálvez la recopilación curada sobre gobernanza de agentes de IA
- 11:30 - [[jefatura]] **aprendizaje**: tomar el consejo de Mauricio Barra y capitalizar todo lo que se hace, documentos, acuerdos y software, en entregables tangibles
- 14:20 - [[responsable-sw]] **progreso**: apoyo a Raúl Araya en el ajuste de la justificación técnica de la solicitud de tiempo técnico de noviembre para el interferómetro
- 15:00 - [[operaciones-general]] **señal**: invitación de Marcelo Jensen a integrar el comité de revisión Phase A del proyecto Multi Site Operations
- 16:15 - [[colaboraciones]] ~~(Hecho)~~: despachar el correo de la propuesta Concurso I+D Tecnológico 2027 a Carlos Silva, Fabina Méndez y Víctor Lagos
- 17:00 - [[exploraciones-operacionales]] ~~(Hecho)~~: dejar listo el registro de formularios de API keys de Azure LLM
- 17:20 - [[exploraciones-operacionales]] ~~(Hecho)~~: declarar la API key propia bajo el caso de uso responsible vibe coding y crear su nota conceptual
- 18:00 - [[responsable-sw]] ~~(Hecho)~~: dejar cargando el auto eléctrico 94 para que Cristóbal Carrasco lo use el viernes temprano
- 19:30 - [[streamlit-operaciones]] **decisión**: en el próximo turno avanzar fuerte con Streamlit para operaciones y con el pendiente de fuerzas de M1

---

### Viernes 14 de Agosto
> [!tldr]
> Traspaso de turno a las 14:00 y asunción del rol de Jefe de División con pronóstico de clima complicado. Reunión de colaboración por el dataset de puntos PLC del espectrógrafo. Emitida la primera API key oficial del marco Azure LLM y cerrado el repositorio de exploraciones operacionales tras validarlo con dos solicitudes. Responsible Vibe Coding pasa a proyecto formal.

- 09:30 - [[colaboraciones]] **hito**: reunión con Carla Fuentes, Fabina Méndez y Florencia Morales por la tesis de Javier Castro
- 09:40 - [[colaboraciones]] **decisión**: compilar al vuelo el diccionario de puntos PLC del espectrógrafo desde MetricDB, sin gestión de software central
- 09:45 - [[tesis-javier-castro]] **progreso**: Carla Fuentes subió a GitHub el dataset de puntos PLC de MetricDB para la tesis
- 09:50 - [[colaboraciones]] **pendiente**: consultar a Nelson Morales por el respaldo y la ingesta del dataset de puntos PLC
- 09:55 - [[colaboraciones]] **pendiente**: organizar la inducción en GitHub para Florencia Morales
- 14:00 - [[responsable-sw]] ~~(Hecho)~~: terminar el traspaso de turno y asumir como Jefe de División en Faena
- 14:10 - [[jefatura]] **señal**: pronóstico de clima complicado para el turno que empieza
- 15:30 - [[exploraciones-operacionales]] ~~(Hecho)~~: enviar a Esteban Parra las condiciones del marco Azure LLM
- 16:00 - [[exploraciones-operacionales]] **hito**: emitida la primera API key oficial del marco Azure LLM a Bernardo Salinas para su proyecto exploratorio
- 17:15 - [[exploraciones-operacionales]] **hito**: repositorio de exploraciones operacionales finalizado y probado con dos solicitudes de API keys
- 17:30 - [[exploraciones-operacionales]] **decisión**: formalizar Responsible Vibe Coding como proyecto
- 17:40 - [[exploraciones-operacionales]] **progreso**: habilitada la generación autónoma de resúmenes de sesiones de trabajo en Responsible Vibe Coding
- 17:50 - [[exploraciones-operacionales]] **progreso**: implementado el repositorio Multi-repo Agentic Workflow, base mínima para gobernar con reglas agénticas un directorio con múltiples subdirectorios

---

### Sábado 15 de Agosto
> [!tldr]
> Jornada de hitos como Jefe de División: Carlos Silva valida la propuesta de soporte de datos y pide vincularla a procesos, primera reunión de exploraciones operacionales con estudiantes, One2One de DevOps y diapositiva de Responsible Vibe Coding. Se proyecta la Estrategia de IA al Comité Conjunto de noviembre. Por la tarde, una emergencia climática de cinco horas absorbe la capacidad técnica y activa el plan de contingencia.

- 10:00 - [[exploraciones-operacionales]] ~~(Hecho)~~: realizar la primera reunión de exploraciones operacionales con estudiantes de práctica
- 11:05 - [[exploraciones-operacionales]] **hito**: primera reunión con practicantes cerrada: una hora, cinco alumnos y cuatro presentaciones de proyectos de IA, con muy buen espacio colaborativo
- 11:10 - [[exploraciones-operacionales]] **aprendizaje**: el traslape presencial en el cerro con Fabina Méndez durante la primera mitad del turno resultó altamente productivo; mantener días de traslape se confirma como patrón de trabajo
- 12:00 - [[devops-contrataciones]] ~~(Hecho)~~: hacer el One2One con Valeria Pizarro
- 12:20 - [[devops-contrataciones]] **pendiente**: pedir a Víctor Lagos que defina los primeros objetivos directamente con Valeria Pizarro
- 13:30 - [[tesis-grafos]] **reflexión**: el pipeline de la tesis de grafos, Markdown crudo procesado con IA hacia artefactos finales, es el mismo patrón de PILWA para TUKU en PEWMA y es exportable a la documentación de soporte de datos
- 15:00 - [[exploraciones-operacionales]] ~~(Hecho)~~: dejar lista una diapositiva de Responsible Vibe Coding para los Data Coffee de Fabina Méndez
- 16:00 - [[soporte-datos]] **hito**: Carlos Silva aceptó la propuesta general del grupo de soporte de datos
- 16:10 - [[soporte-datos]] **decisión**: vincular la iniciativa al desarrollo de procesos e incluir a Jorge Muñoz, responsable de mantenimiento predictivo y RCA, para asegurar un caso de uso ligado a procesos reales
- 16:15 - [[soporte-datos]] **pendiente**: reunirse con Carlos Silva y Jorge Muñoz el lunes 17 de agosto
- 16:40 - [[faena-ai]] **señal**: Alejandro Palma informó que en noviembre se reúne el Comité Conjunto de Operaciones y uno de los temas centrales será la Estrategia de Inteligencia Artificial
- 17:00 - [[jefatura]] **fricción**: emergencia por mal tiempo severo en Faena entre las 17:00 y las 22:00; el rol de Jefe de División absorbió toda la capacidad técnica del día
- 22:00 - [[jefatura]] ~~(Hecho)~~: elaborar el Plan de contingencia por mal tiempo de agosto 2026 para coordinar la logística y los turnos del equipo

---

### Domingo 16 de Agosto
> [!tldr]
> Jornada dominical dedicada íntegramente al rol de Jefe de División por la emergencia climática: reprogramación de la subida del martes al miércoles, actualización de la planificación de turnos, reasignación de roles operacionales, aseguramiento de suministros y comunicado general al observatorio.

- 08:30 - [[jefatura]] ~~(Hecho)~~: avisar a los colegas que la subida del martes se pospone al miércoles
- 10:15 - [[jefatura]] ~~(Hecho)~~: actualizar la planificación de turnos del equipo de software
- 12:00 - [[jefatura]] ~~(Hecho)~~: reasignar los roles operacionales de telescopios e instrumentos (TSO, TCU, ITOM)
- 15:40 - [[jefatura]] ~~(Hecho)~~: asegurar los suministros para la contingencia
- 17:20 - [[jefatura]] ~~(Hecho)~~: emitir el comunicado general al observatorio por la emergencia climática
- 20:00 - [[jefatura]] **nota**: jornada dominical completa dedicada al rol de Jefe de División por la emergencia climática

---

### Lunes 17 de Agosto
> [!tldr]
> Última jornada del rol operacional, entregado a las 14:00 con los planes de contingencia en ejecución. La reunión de las 16:30 acuerda el Go para la postulación al Concurso I+D Tecnológico 2027, enfocada en telemetría y análisis de logs. Avances en gobernanza de API keys y el plan de contingencia compartido. Cierre reflexivo sobre el conocimiento tribal que el modelo sistematizado no captura.

- 14:00 - [[responsable-sw]] ~~(Hecho)~~: entregar el turno de Jefe de División a César Espinoza con los planes de contingencia en ejecución
- 15:00 - [[soporte-datos]] **progreso**: tarde completa dedicada a los pendientes de soporte de datos
- 16:30 - [[colaboraciones]] ~~(Hecho)~~: reunirse con Carlos Silva y Jorge Muñoz el lunes 17 de agosto
- 17:30 - [[colaboraciones]] **hito**: acordado el Go para la postulación al Concurso I+D Tecnológico 2027, enfocada en telemetría y análisis de logs para mantenimiento predictivo y RCA usando el ranking de criticidad de Jorge Muñoz
- 17:35 - [[colaboraciones]] **pendiente**: preparar la versión pulida de la propuesta para coordinar con Universidad Sur y Universidad Centro
- 18:00 - [[jefatura]] **aprendizaje**: el Plan de contingencia por mal tiempo resultó un recurso valioso para la gestión del rol
- 18:05 - [[jefatura]] ~~(Hecho)~~: compartir el Plan de contingencia por mal tiempo con Mauricio Barra y César Espinoza
- 18:40 - [[exploraciones-operacionales]] **decisión**: asumir la administración de la instancia de Azure OpenAI (`faenaopenai`)
- 18:50 - [[exploraciones-operacionales]] ~~(Hecho)~~: procesar dos formularios adicionales de exploraciones operacionales aprobados por Fabina Méndez
- 19:00 - [[exploraciones-operacionales]] ~~(Hecho)~~: enviar a Víctor Lagos el esquema de gobernanza de las API keys
- 20:15 - [[faena-ai]] **idea**: abrir un canal o espacio de discusión para la comunidad interesada en IA, para compartir experimentos y debatir abiertamente
- 21:30 - [[soporte-datos]] **reflexión**: el concepto operacional de Carlos Silva coincide con el modelo de TUKU al terminar en acción y aprendizaje sistematizado, pero le falta integrar el conocimiento tribal; los espacios informales entre especialistas producen un aprendizaje colectivo insustituible

---

### Martes 18 de Agosto
> [!tldr]
> Último día de turno en Faena. Con Nelson Morales quedan definidos los pendientes de software para el próximo turno. Con Carlos Silva y Víctor Lagos se cierra el roadmap de operaciones guiadas por datos, con gobernanza formal exigida por Phase B. Vacaciones armonizadas, bajada de madrugada confirmada por hielo y cierre recreativo con el equipo.

- 09:40 - [[responsable-sw]] **hito**: reunión con Nelson Morales sobre software del interferómetro y CINTILATOR
- 09:50 - [[responsable-sw]] **pendiente**: corregir por software la keyword SEQ.CENTERSC, reportada por Johan y hoy cambiada a mano por astronomía
- 09:55 - [[responsable-sw]] **pendiente**: revisar la keyword FT MODE en CINTILATOR con Alex
- 10:00 - [[responsable-sw]] **pendiente**: revisar el commit de polarización y las tablas faltantes del 5 de agosto
- 11:30 - [[jefatura]] ~~(Hecho)~~: armonizar las fechas de vacaciones y permisos del equipo de software en Faena
- 11:45 - [[jefatura]] **decisión**: confirmada la bajada de Faena para el miércoles 19 de agosto de madrugada por el hielo en la carretera
- 15:00 - [[soporte-datos]] **hito**: reunión con Carlos Silva y Víctor Lagos sobre el roadmap de operaciones guiadas por datos
- 15:10 - [[soporte-datos]] **señal**: Phase B exige gobernanza formal para la puesta en marcha de las operaciones guiadas por datos
- 15:15 - [[soporte-datos]] **decisión**: el equipo de soporte de datos implementa la estrategia operativa de forma iterativa, apalancando la gobernanza ya probada en exploraciones operacionales
- 19:00 - [[jefatura]] **nota**: cierre de jornada con recreación en la nieve con el equipo y labores administrativas
- 20:30 - [[faena-ai]] **nota**: grabadas tres intervenciones explicando el observatorio para las cámaras de la televisión internacional

---

### Miércoles 19 de Agosto
> [!tldr]
> Bajada de madrugada y cierre de turno tras una semana marcada por la emergencia climática. Enviado el calendario de Soporte y comisionado el ticket de lecciones aprendidas. Despachado el wrap-up del Concurso I+D 2027 y cerrada la versión de agosto del documento conceptual de soporte de datos. Tercera citación de la televisión internacional.

- 05:30 - [[jefatura]] ~~(Hecho)~~: bajar de Faena de madrugada y cerrar el turno
- 09:00 - [[jefatura]] ~~(Hecho)~~: enviar el calendario de turnos de Soporte a Alicia Abarca
- 10:20 - [[responsable-sw]] ~~(Hecho)~~: marcar como comisionado en Jira el ticket CRB-1003427 sobre el proceso de lecciones aprendidas
- 11:40 - [[colaboraciones]] ~~(Hecho)~~: despachar el correo de wrap-up de la propuesta Concurso I+D Tecnológico 2027 a Carlos Silva, Fabina Méndez y Jorge Muñoz con los casos de uso de mantenimiento predictivo y RCA
- 15:00 - [[soporte-datos]] ~~(Hecho)~~: dejar lista la versión de agosto 2026 del documento conceptual de soporte de datos, estructurado en Operación, Desarrollo y Gobernanza
- 17:20 - [[faena-ai]] **señal**: citación a una tercera entrevista, esta vez más extendida, para la televisión internacional
- 17:25 - [[faena-ai]] **reflexión**: hay un patrón de visibilidad en medios que conviene mirar
- 19:00 - [[salud-personal]] **nota**: quedó pagada la sesión del día anterior con el psicólogo Camilo Aguirre

---

## Período de Descanso (20 al 23 de Agosto de 2026)

### Jueves 20 de Agosto
> [!tldr]
> Coordinación de la entrega del Depto Centro a Mateo para enero. En infraestructura, contención del consumo de tokens en la máquina virtual pausando Serendipia, reiniciando el contexto por hora y sumando Google como fallback. Serendipia se proyecta como futuro artículo técnico.

- 10:00 - [[arriendo-depto-centro]] **decisión**: coordinar con Mateo la entrega del Depto Centro para que se instale en enero
- 10:05 - [[arriendo-depto-centro]] **pendiente**: avisar con tiempo a Carmen Navarro sobre la entrega del Depto Centro en enero
- 12:30 - [[oracle-vm]] **señal**: cuota de OpenRouter agotada en la máquina virtual por alto consumo de tokens, más del 50% por Serendipia y 99% acumulado por contexto persistente
- 12:45 - [[oracle-vm]] ~~(Hecho)~~: pausar Serendipia y configurar un reinicio horario de contexto que pase solo las últimas cien líneas de la bitácora
- 13:00 - [[oracle-vm]] ~~(Hecho)~~: sumar Google como fallback, dado que Hermes no soporta Groq
- 18:40 - [[mac-personal]] **idea**: el mecanismo de Serendipia da para un paper o una nota técnica en GitHub Gist, y calza con la estrategia de visibilidad técnica
- 18:45 - [[mac-personal]] **señal**: sin optimización de caché, Serendipia llegó a consumir treinta millones de tokens al día

---

### Viernes 21 de Agosto
> [!tldr]
> Actualizadas las notas de Perfil y Voz y cerrada la retrospectiva del turno. Definido para el próximo turno el manejo de las sesiones de IA con estudiantes junto a Fabina Méndez. Contacto de la Organización para charlas de captación. Kinesiología postergada. En lo familiar, observaciones sobre los avances de Lucas y de Mateo.

- 09:30 - [[mac-personal]] ~~(Hecho)~~: actualizar las notas de Perfil y de Guía de Voz en primera persona con los hallazgos del análisis con IA sobre correos e interacciones previas
- 11:00 - [[jefatura]] ~~(Hecho)~~: cerrar el análisis retrospectivo del último turno de Faena
- 12:15 - [[exploraciones-operacionales]] **decisión**: definir en el próximo turno con Fabina Méndez cómo estructurar y segmentar las sesiones con estudiantes para experimentos de IA, adaptando la dinámica a la audiencia
- 15:00 - [[colaboraciones]] **señal**: Agustín Díaz de la Organización propone charlas online de captación de estudiantes de Universidad Sur, y eventualmente una internacional en inglés para septiembre u octubre
- 15:20 - [[colaboraciones]] **reflexión**: la vocería institucional y en otros ámbitos viene creciendo, pero falta acelerar el posicionamiento público visible como especialista en IA
- 16:00 - [[salud-personal]] **decisión**: no ir a kinesiología en Centro Kine durante este descanso; el pendiente queda postergado
- 19:00 - [[personal]] **observación**: Lucas está desarrollando con fuerza la lectura y escritura de cómics, y su veta humanista está aflorando
- 19:05 - [[personal]] **pendiente**: evaluar opciones para apoyar a Lucas, como un taller de anime
- 19:20 - [[personal]] **observación**: Mateo muestra avances sólidos en su primer año como ingeniero de software enfocado en IA; enfoques propios con los mismos principios, centralidad en Markdown, uso fluido de agentes y control total sobre los resultados
- 21:00 - [[mac-personal]] ~~(Hecho)~~: crear un espacio para recopilar artículos web con fecha, trazabilidad y comentarios breves, partiendo con Los Artefactos del Pensamiento de Psychology Today

---

### Sábado 22 de Agosto
> [!tldr]
> Día familiar con las compras resueltas y salida recreativa con los niños a jugar realidad virtual.

- 11:00 - [[personal]] ~~(Hecho)~~: comprar el traje de baño para Gaspar
- 11:30 - [[personal]] ~~(Hecho)~~: comprar el regalo de cumpleaños para Nico
- 12:00 - [[personal]] ~~(Hecho)~~: coordinar con la mamá la compra de la camisa a cuadros para Lucas
- 16:30 - [[personal]] ~~(Hecho)~~: salir con los niños a jugar realidad virtual a Arcade VR

---

### Domingo 23 de Agosto
> [!tldr]
> Sesión nocturna de destilación hacia TUKU con el enfoque minimalista definido, y el patrón arquitectónico de tres niveles formulado. Queda abierto mapear las fricciones del sistema actual para no repetirlas. Compras y cumpleaños familiar cierran el período de descanso.

- 03:00 - [[tuku]] **reflexión**: sesión nocturna de varias horas destilando hacia TUKU lo que funciona del sistema de gestión actual
- 03:10 - [[tuku]] **decisión**: partir de forma ultra minimalista con brief, principios y specs, y validar con ejemplos concretos y bitácoras reales para que el sistema genere la documentación de forma clara para el equipo
- 03:20 - [[tuku]] **pendiente**: mapear qué fricciones del sistema actual no deben repetirse en TUKU
- 03:30 - [[tuku]] **fricción**: condensar seis meses de práctica acumulada es complejo; la sesión se pausa para retomarla después
- 11:00 - [[personal]] ~~(Hecho)~~: comprar el pasaje en Bus interurbano para la subida a Faena del martes 25 de agosto
- 15:40 - [[tuku]] ~~(Hecho)~~: formular el patrón arquitectónico de TUKU en tres niveles: Coordinador con impersonación contextual, Supervisores de dominio para bitácora, ámbito y tareas, y subagentes de ejecución con contexto limpio
- 17:00 - [[personal]] ~~(Hecho)~~: asistir al cumpleaños de Nico en Parque Infantil con Lucas

---

# Parte 3: Estado Reconstruible del Repositorio (Grafo de Entidades y Metadatos MaC)

> [!abstract] Especificación de Estado Objetivo
> Esta sección describe el estado documental y relacional completo del repositorio que un sistema agéntico debe ser capaz de inferir, actualizar o reconstruir a partir de los inputs de actividad anteriores.

> [!question] Pendiente de traducción #REVISAR
> **Esta Parte 3 sigue en la estructura de `mac-jpgil`**: `org/<Organización>/VIGENTES/`, sin los `AGENTS.md` ni `CADENCIAS.md` que exige [`spec/ambitos.md`](../../spec/ambitos.md). El equivalente traducido está en la Parte 3 de [`referencia-pyme.md`](referencia-pyme.md). Traducirla es trabajo del epic 003, el que necesita el estado poblado: hacerlo ahora sería inventar la jerarquía sin un test que la fuerce. Mientras tanto los `[[ambito]]` de la Parte 2 usan nombre corto, único en este corpus.

## 1. Árbol de Organizaciones y Áreas (ORG)

```
org/
├── Faena/
│   ├── Faena.md (Frontpage de organización)
│   ├── VIGENTES/
│   │   ├── faena-ai.md
│   │   ├── jefatura.md
│   │   ├── tesis-javier-castro.md
│   │   ├── devops-contrataciones.md
│   │   ├── responsable-sw.md
│   │   ├── exploraciones-operacionales.md
│   │   ├── transformacion-digital.md
│   │   ├── operaciones-general.md
│   │   ├── soporte-datos.md
│   │   ├── streamlit-operaciones.md
│   │   └── colaboraciones.md
│   └── ARCHIVADO/
│       └── paper-conferencia.md (archivado el 12 de agosto)
├── Personal/
│   ├── Personal.md (Frontpage de organización)
│   └── VIGENTES/
│       ├── arriendo-depto-centro.md
│       ├── salud-personal.md
│       ├── tesis-grafos.md
│       ├── mac-personal.md
│       └── oracle-vm.md
└── PEWMA.AI/
    ├── PEWMA.AI.md (Frontpage de organización)
    └── VIGENTES/
        └── tuku.md
```

## 2. Inventario de Pendientes y Estados de Tarea

### Turno Faena (11 al 19 de Agosto de 2026)
* **Completados `[x]`:**
  - `arriendo-depto-centro`: Enviar boleta de Gastos Comunes de Depto Centro a Carmen Navarro por WhatsApp.
  - `responsable-sw`: Cargar auto eléctrico 94 para Cristóbal Carrasco.
  - `jefatura`: Recordar a SAF que LASCOR API tiene prioridad.
  - `faena-ai`: Enviar correo a Tomás Toledo y Xander Gálvez sobre gobernanza de agentes IA.
  - `colaboraciones`: Enviar correo Concurso I+D Tecnológico 2027 a Carlos Silva, Fabina Méndez y Víctor Lagos.
  - `exploraciones-operacionales`: Registro y validación de formularios de API keys Azure LLM.
  - `exploraciones-operacionales`: Declarar API key con caso de uso "responsible vibe coding" y crear nota.
  - `exploraciones-operacionales`: Primera reunión de internships con Fabina Méndez y estudiantes.
  - `devops-contrataciones`: One2One con Valeria Pizarro y solicitud de objetivos a Víctor Lagos.
  - `exploraciones-operacionales`: Enviar condiciones de API keys a Esteban Parra.
  - `soporte-datos`: Agendar y realizar reunión con Carlos Silva y Jorge Muñoz.
  - `responsable-sw`: Handover de Jefe de División y fin de turno con entrega a César Espinoza.
  - `jefatura`: Avisos de postergación de subida por mal tiempo, actualización de turnos y roles operacionales.
  - `jefatura`: Enviar calendario de turnos de Soporte a Alicia Abarca.
  - `responsable-sw`: Comisionamiento del ticket CRB-1003427 en Jira.
  - `colaboraciones`: Despacho de correo de wrap-up y casos de uso de investigación 2027.
  - `soporte-datos`: Preparar versión agosto 2026 de documentación conceptual de soporte-datos.
  - `Personal`: Pagos de psicólogo Camilo Aguirre y regularización de gastos comunes Depto Cerro.

* **Postergados / Heredados al siguiente ciclo:**
  - `responsable-sw`: Limpieza de tickets ITK en Soporte (postergado al próximo turno).
  - `responsable-sw`: CINTILATOR: Revisar keyword SEQ.CENTERSC reportado por Johan.
  - `responsable-sw`: CINTILATOR: Revisar keyword FT MODE en CINTILATOR con Alex.
  - `responsable-sw`: CINTILATOR: Revisar commit de polarización y tablas faltantes del 5 de agosto (Takao).
  - `crb-grism`: Refactorización de script de chequeo (postergado por contingencia climática).
  - `soporte-datos`: Formalizar rol Data-led Operations (DLO).
  - `devops-contrataciones`: Escribir objetivos de Valeria Pizarro en portal de RRHH.
  - `transformacion-digital`: Dividir interfaces ODIP en tareas manejables con Víctor Lagos.
  - `exploraciones-operacionales`: Calendario de feedback de proyectos y revisión de ADRs.
  - `Personal`: Comprar maleta, hora en Centro Kine y bioimpedanciometría con Dr. Pablo Lara.

### Período de Descanso (20 al 23 de Agosto de 2026)
* **Completados `[x]`:**
  - `Personal`: Análisis retrospectivo del turno anterior cerrado.
  - `Personal`: Comprar traje de baño para Gaspar.
  - `Personal`: Compra de camisa a cuadros para Lucas (coordinada con la mamá).
  - `Personal`: Comprar regalo de cumpleaños para Nico.
  - `Personal`: Salida recreativa con los niños a Arcade VR.
  - `Personal`: Compra de pasaje de Bus interurbano para subida a Faena del martes 25 de agosto.
  - `Personal`: Salida al cumpleaños de Nico en Parque Infantil con Lucas.

* **Activos y Postergados:**
  - `Personal`: Pedir Bioimpedanciometría con Dr. Pablo Lara al +56974984494.
  - `Personal`: Crear repositorio para workflows personales (abstracts y boletas médicas).
  - `oracle-vm`: Probar Hermes en la VM cuando se reactive el plan de OpenCode Go.
  - `salud-personal`: Kinesiología en Centro Kine (postergada deliberadamente).

## 3. Personas Enlazadas (Notas de Entidad en `notas/`)

* **Ámbito Laboral e Institucional:**
  - `Fabina Méndez` (FME) — Contraparte clave en exploraciones operacionales e iniciativas de IA.
  - `Carlos Silva` (CSI) — Jefatura de ingeniería / operaciones; validación de estrategia de soporte-datos y colaboración científica.
  - `Víctor Lagos` (VLA) — Liderazgo técnico; gobernanza de IA, ODIP y objetivos de equipo.
  - `Mauricio Barra` (MBA) — Dirección de operaciones; asesoría estratégica y patrocinio institucional.
  - `Jorge Muñoz` (JMU) — Mantenimiento predictivo, RCA y ranking de criticidad de sistemas.
  - `Carla Fuentes` (CFU) — Gestión de datos PLC de espectrógrafo y soporte a tesis de grado.
  - `Florencia Morales` — Colaboradora en gestión de datos y repositorio GitHub.
  - `Javier Castro` — Tesista de ingeniería analizando datos de telemetría.
  - `Tomás Toledo` (TTO) — IT Casa Matriz; servicios de plataforma y gobernanza de agentes.
  - `Xander Gálvez` — IT Casa Matriz; arquitectura tecnológica y gobernanza IA.
  - `Rodrigo Álvarez` — IT Casa Matriz; infraestructura NVIDIA y plataforma v2.
  - `Bernardo Salinas` — Primer intern receptor de API key Azure LLM.
  - `Esteban Parra` (EPA) — Casos de uso de LLM en ingeniería y operaciones.
  - `Cristóbal Carrasco` — Colega de turno de software y logística.
  - `Raúl Araya` (RAR) — Solicitudes de tiempo técnico (TTQ) de instrumentos interferométricos.
  - `César Espinoza` — Relevo y entrega de turno en rol de Jefe de División.
  - `Alejandro Palma` — Jefe de operadores de telescopio; coordinación de Comité Conjunto.
  - `Patricio Soto` (PSO) — Colega de área de ingeniería (ergonomía / standing desk).
  - `Valeria Pizarro` (VPI) — Nueva contratación DevOps; asignación de metas iniciales.
  - `Alicia Abarca` — Coordinación de estudiantes y calendarios de turnos de soporte.
  - `Marcelo Jensen` — Líder de proyecto Multi Site Operations.
  - `Agustín Díaz` — Representante de la Organización para captación académica y charlas.
  - `Nelson Morales` (NMO) — Responsable de software de instrumentos interferométricos y CINTILATOR.
  - `Alex` — Colaborador técnico en modos de observación CINTILATOR.
  - `Irene Morales` — Colega de jefatura/gestión de equipo en faena.
  - `Elena Sepúlveda` (ESE) — Contraparte científica para estrategia y documentos de IA.

* **Ámbito Familiar y Personal:**
  - `Mateo` — Hijo, informático; transición de arriendo Depto Centro y trabajo agéntico con Markdown.
  - `Lucas` — Hijo; desarrollo de cómics y lectura, veta humanística.
  - `Gaspar` — Hijo; compras familiares.
  - `Nico` — Amigo de la familia (cumpleaños infantil).
  - `Carmen Navarro` — Administradora de Depto Centro.
  - `Mónica Castro` — Administradora de Depto Cerro.
  - `Camilo Aguirre` — Psicólogo personal.
  - `Dr. Pablo Lara` — Médico para examen de bioimpedanciometría.

## 4. Notas Conceptuales y Documentos Enlazados (`notas/`)

* **Gobernanza y Estrategia de IA:**
  - `Marco Azure LLM para Proyectos Exploratorios de IA` — Reglas de emisión y gobernanza de API keys.
  - `Responsible Vibe Coding` — Proyecto y filosofía de codificación asistida con agentes autónomos.
  - `Evaluación de riesgo y gobernanza de agentes en la Organización` — Referencias curadas para IT.
* **Operaciones y Arquitectura de Datos:**
  - `Data Stewardship Concept - Version Agosto 2026` — Documento base en 3 pilares (Operación, Desarrollo, Gobernanza).
  - `Concurso I+D Tecnológico 2027 log-analysis` — Propuesta interuniversitaria de telemetría y RCA.
  - `Plan de contingencia por mal tiempo agosto 2026` — Protocolo operacional ante mal tiempo en Faena.
  - `Cosas que hablar con Víctor - 2026-08-15` — Colector de temas pendientes para sincronización semanal.
* **Sistema de Gestión Personal y Agéntico:**
  - `Perfil de Damián Ulloa` — Modelo cognitivo, valores y toma de decisiones.
  - `Voz de Damián Ulloa - cómo escribir en primera persona` — Guía de estilos y registros conversacionales.
  - `Visibilidad profesional y comunicación en la era post-IA` — Ensayo sobre posicionamiento técnico y difusión.
  - `Artículos generales interesantes` — Registro estructurado de lecturas y reflexiones externas.
  - `TUKU - Dispatch a agentes con clear context` — Arquitectura de 3 niveles y ciclo de vida de contexto.
  - `PILWA, ideas para Zettelkasten criollo` — Patrón de captura, refinamiento y generación de artefactos.

----