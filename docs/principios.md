# TUKU: principios

> Orientación normativa, no contrato rígido. Sirven para tomar decisiones cuando el uso diario plantee dilemas no resueltos.

### 1. El archivo de texto es lo primero

Todo lo que importa vive en archivos Markdown legibles sin necesidad de ejecutar ningún software. El frontmatter se mantiene al mínimo: si hace falta un programa propietario o una base de datos para entender los datos, la arquitectura está mal.

Horizonte: veinte años. La prueba de fuego es que el sistema completo se pueda operar a mano con un editor de texto básico, aunque tome más esfuerzo. Los agentes existen para absorber ese esfuerzo mecánico, nunca para volverlo obligatorio.

### 2. La organización emerge del uso

Cero configuración inicial. El repositorio nace con un solo ámbito —`ámbitos/personal/personal.md`— y una bitácora en blanco.

Lo que el sistema sabe de la vida del autor —clientes, proyectos, ritmos de trabajo— se destila de lo que quedó registrado día a día, no de un formulario. El agente detecta patrones y propone; el autor aprueba con una palabra.

Corolario de diseño: **lo que debe emerger no se especifica por adelantado**. Se deja espacio para que la práctica aparezca sola, y cuando se consolida, se anota como regla en el libro de estilo.

### 3. El agente es un secretario, no un dueño

Un solo agente conversa con el autor y sostiene su contexto global. Detrás de él, organiza a otros **agentes colaboradores** para tareas específicas y rutinarias: clasificar, resumir o auditar enlaces.

Su rol es proponer, jamás ratificar. Redacta borradores, pero no modifica reglas. Opera bajo higiene estricta: silencio por defecto, contexto mínimo por sesión y sin interrupciones innecesarias. Un asistente que interrumpe todo el día deja de ser útil.

Mantiene además curiosidad operativa: si nota que una entrada de un ámbito encaja mejor en otro, propone moverla.

### 4. Todo baja hasta donde alcance el determinismo

```
libro de estilo  →  janitor (script)  →  agente (LLM)  →  autor
```

Cada nivel libera de carga al siguiente. Al implementar cualquier funcionalidad, se empuja hacia la izquierda tanto como sea posible: si un script determinista puede resolverlo, no se gastan tokens ni juicio en un LLM; si el agente puede redactar el borrador, no se consume tiempo del autor.

Al autor le queda lo irreductible: gobernar, ratificar y decidir.

### 5. Las reglas viven en el libro de estilo

Un único documento en prosa condensa cómo se escribe y cómo se organiza el repositorio. Lo lee el autor, lo leen los agentes y de él nacen las automatizaciones deterministas (janitors).

Está escrito para consumo humano, por lo que no es un esquema formal cerrado. Lo formalizable lo absorben scripts de higiene (*janitors*); lo que requiere juicio semántico queda en manos del agente. Cada regla declara explícitamente quién es responsable de aplicarla.

Si una regla no cabe en el libro de estilo, todavía no es una regla madura.

### 6. Las tres primitivas mínimas

El sistema opera sobre dos ejes ortogonales: el **tiempo** (un continuo global que va del pasado en la bitácora al futuro en los pendientes) y el **ámbito** (la carpeta que define a qué frente de la vida pertenece cada hecho). Cualquier vista es un corte transversal de ambos: *esta semana en el trabajo* fija tiempo y ámbito en una sola consulta.

El tiempo debe ser global porque una jornada real salta entre temas: mientras se resuelve una tarea técnica se atiende un asunto personal. Trocear el registro por carpetas destruiría esa secuencia real.

| Primitiva | Qué guarda | Dónde vive |
|---|---|---|
| **Bitácora** | Hechos ocurridos. Fechado, con hora, inmutable. Fuente canónica de la que nace todo. | Global (`BITACORA.md`) |
| **Pendientes** | Compromisos abiertos. Un solo archivo, solo lo pendiente. Nace y muere por líneas de bitácora. | Global (`PENDIENTES.md`) |
| **Notas** | Conclusiones e ideas destiladas. Estilo wiki, enlazadas entre sí. | En la carpeta del ámbito correspondiente |

Las notas son el espacio mental: no pertenecen a un momento específico, valen mientras la idea conserve sentido.

Lo que cada ámbito muestra de sí mismo —sus avances destacados o sus tareas pendientes— es una **vista filtrada** de los archivos globales, nunca un registro paralelo. Cualquier otro concepto (ciclos, cadencias, reportes) se construye componiendo estas tres primitivas con el árbol de directorios y el libro de estilo.

### 7. Las carpetas archivan; los enlaces conectan

**Los ámbitos son los directorios**: `personal/`, `trabajo/observatorio/`, `clientes/pyme/`. La jerarquía de carpetas refleja la estructura de la vida del autor, lo que habilita tres operaciones sin agregar complejidad técnica:

- **Archivar:** congelar una etapa o proyecto archivando la rama completa del árbol.
- **Reglas locales:** definir directrices específicas dejando un `AGENTS.md` en la carpeta. La regla más cercana al archivo tiene prioridad.
- **Apagar:** suspender temporalmente el seguimiento de un área (*esta semana estoy de vacaciones, no toco trabajo*).

El árbol crece de forma orgánica. Ninguna entrada queda huérfana: lo que no tiene ámbito explícito entra a `personal/` hasta que el agente detecte a dónde pertenece.

**Los enlaces conectan transversalmente.** Con `[[nombre]]` se salta entre páginas, reuniones y proyectos sin importar en qué carpeta o fecha vivan. El agente enlaza al momento de escribir; un enlace que no se creó en el instante casi nunca se crea después.

### 8. Las notas son espontáneas; los ámbitos, ontológicos

Una **nota** adopta el formato libre que el autor decida, con apoyo del agente. No impone plantillas rígidas.

La página principal de un **ámbito**, en cambio, debe explicar con claridad qué es y qué compromisos implica: un cliente externo exige seguimientos y facturación; un proyecto interno sigue ciclos de desarrollo. De cada uno se derivan rutinas distintas.

Ese modelo tampoco se le exige al autor por adelantado: el agente observa cómo opera y redacta notas de observación (*El modelo de cliente en Pyme* o *Flujo de releases de software*). Siempre formuladas como descripciones revisables (*he visto que con estos clientes sueles…*), nunca como normas impuestas. Describir el comportamiento del autor no es decidir por él.

### 9. Reconstruir lo derivado debe devolver lo mismo

Si se borran todos los archivos derivados y se ejecuta la reconstrucción desde los hechos canónicos de la bitácora, se obtiene el mismo sistema: idéntico byte a byte si lo generó un janitor; equivalente en significado si lo redactó un agente.

Este es el test fundamental de arquitectura: si una salida que debía ser idéntica solo resulta equivalente, se introdujo criterio probabilístico de LLM donde correspondía una regla determinista.