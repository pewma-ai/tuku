# TUKU: principios

> Orientación normativa, no contrato rígido. Sirven para tomar decisiones cuando el uso diario plantee dilemas no resueltos.

### 1. El archivo de texto es lo primero

Todo lo que importa vive en archivos Markdown legibles sin necesidad de ejecutar ningún software propietario ni bases de datos. El frontmatter se mantiene al mínimo: si hace falta un programa especial para entender los datos, la arquitectura está mal.

Horizonte: veinte años. La prueba de fuego es que el sistema completo se pueda operar a mano con un editor de texto básico, aunque tome más esfuerzo. Los agentes y janitors existen para absorber ese esfuerzo mecánico, nunca para volverlo obligatorio. Por eso, cada janitor especifica su procedimiento **"A mano"**: si el código no está disponible, el libro se sostiene igual.

**La especificación sobrevive, la implementación se reemplaza.** Un script de hoy no correrá en veinte años, pero la descripción de lo que hacía sí se leerá.

### 2. La organización emerge del uso

Cero configuración inicial. El repositorio recién instalado (el **estado cero**) contiene únicamente la infraestructura básica y arranca en un ciclo semanal:
- `AGENTS.md` y `LIBRO-DE-ESTILO.md` en la raíz.
- `AHORA.md` con los días sembrados del primer ciclo, sin entradas.
- `PENDIENTES.md` con los callouts permanentes de horizonte vacíos.
- `ambitos/` con `AGENTS.md` y `CADENCIAS.md`, y la rama inicial `personal/` (`AGENTS.md`, `CADENCIAS.md`, `personal.md`).
- `notas/` y `reglas/`.

El primer día hay una bitácora en blanco y una sola pregunta: *¿qué anotaremos hoy?*. Lo que el sistema sabe de la vida del autor —clientes, proyectos, ritmos de trabajo— se destila de lo que quedó registrado día a día, no de un formulario. El agente detecta patrones y propone; el autor aprueba con una palabra.

Corolario de diseño: **lo que debe emerger no se especifica por adelantado**. Se deja espacio para que la práctica aparezca sola, y cuando se consolida, se anota como regla en el libro de estilo.

### 3. El agente es un secretario, no un dueño

Un solo agente principal conversa con el autor y sostiene su contexto global. Detrás de él, organiza a otros **agentes colaboradores** y janitors para tareas específicas: clasificar, resumir, auditar enlaces o colectar cadencias.

Su rol es proponer, jamás ratificar. Redacta borradores y propone notas o cambios, pero no modifica reglas ni ejecuta decisiones sin autorización. Opera bajo higiene estricta: silencio por defecto, contexto mínimo por sesión y sin interrupciones innecesarias.

Mantiene además curiosidad operativa: si nota que una entrada de un ámbito encaja mejor en otro, propone moverla.

### 4. Todo baja hasta donde alcance el determinismo

```
libro de estilo / reglas  →  janitor (script)  →  agente (LLM)  →  autor
```

Cada nivel libera de carga al siguiente. Al implementar cualquier funcionalidad, se empuja hacia la izquierda tanto como sea posible: si un script determinista puede resolverlo, no se gastan tokens ni juicio en un LLM; si el agente puede redactar el borrador, no se consume tiempo del autor.

Al autor le queda lo irreductible: gobernar, ratificar y decidir.

El LLM se aísla en los dos extremos: la entrada (interpretar dictado a hecho estructurado) y la inferencia semántica (resúmenes, destilado de notas y propuestas). Todo el medio —abrir, cerrar y mover pendientes, resolver cadencias, mantener índices y transclusiones— es **100% determinista**.

### 5. Las reglas viven en el libro de estilo y reglas/

Un único documento en prosa (`LIBRO-DE-ESTILO.md`) condensa cómo se escribe y cómo se organiza el repositorio. Lo lee el autor, lo leen los agentes y de él nacen las automatizaciones deterministas (janitors).

La **especificación** vive en el repositorio (`reglas/janitors.tuku.md` y `reglas/`), documentando en prosa qué hace cada proceso. El **código ejecutable** vive fuera, instalado en `~/.tuku/janitors`. Así el libro del autor no duplica código de herramientas ni diverge con el tiempo.

Si una regla no cabe en el libro de estilo o en `reglas/`, todavía no es una regla madura.

### 6. Las primitivas y el conjunto canónico

El sistema opera sobre dos ejes ortogonales: el **tiempo** (un continuo global que va del pasado en las bitácoras al futuro en los pendientes) y el **ámbito** (la carpeta que define a qué frente de la vida pertenece cada hecho). Cualquier vista es un corte transversal de ambos: *esta semana en el trabajo* fija tiempo y ámbito en una sola consulta.

El **conjunto canónico** es la fuente primaria del sistema y **nunca se regenera**:
- `AHORA.md`: ciclo en curso con entradas vivas y vistas transcluidas.
- `bitacoras/`: ciclos cerrados, inmutables y autocontenidos.
- `PENDIENTES.md`: fuente de verdad única de compromisos abiertos.
- `ambitos/`: árbol de frentes de actividad con sus `AGENTS.md` y `CADENCIAS.md`.
- `notas/`: zettelkasten global de ideas y notas tipadas.

| Primitiva | Qué guarda | Dónde vive |
|---|---|---|
| **Bitácora** | Hechos ocurridos. Fechado, con hora, inmutable. | `AHORA.md` (en curso) y `bitacoras/` (cerrados) |
| **Pendientes** | Compromisos abiertos. Fuente única de verdad, no derivado. | `PENDIENTES.md` |
| **Notas** | Conclusiones e ideas destiladas. Zettelkasten global. | `notas/` |
| **Ámbitos** | Estructura ontológica de la vida del autor. | `ambitos/` |
| **Cadencias** | Reglas de recurrencia que emiten pendientes con fecha. | En `CADENCIAS.md` de cada ámbito |
| **Ciclos** | Composición temporal (planes y resúmenes). | `planes/` y `reportes/` |

Lo que cada ámbito o día muestra de sí mismo es una **vista transcluida** o filtrada de los archivos canónicos, nunca un registro paralelo.

### 7. Las carpetas archivan; los enlaces conectan

**El árbol de ámbitos (`ambitos/`) refleja la estructura de la vida del autor.** Se distinguen tres roles según lo que contiene cada nodo:
- **Ámbito:** frente de actividad con identidad propia. Es un directorio con página propia (`personal/personal.md`, `trabajo/trabajo.md`).
- **Categoría:** agrupador sin identidad propia. Es un directorio sin página propia (`trabajo/clientes/`).
- **Actividad:** la hoja donde efectivamente ocurren las cosas. Es un archivo `.md` en minúsculas (`juanito_perez.md`).

Regla operativa: **las entradas apuntan a una actividad o a un ámbito, nunca a una categoría.**

Convención de nombres: **MAYÚSCULAS es de TUKU** (`AHORA.md`, `PENDIENTES.md`, `AGENTS.md`, `CADENCIAS.md`), **minúsculas es del autor** (`trabajo.md`, `juanito_perez.md`, notas).

Todo directorio bajo `ambitos/` lleva obligatoriamente dos archivos, aunque estén vacíos: `AGENTS.md` y `CADENCIAS.md`. En ambos, **la regla más cercana prevalece**.

**Los enlaces conectan transversalmente.** Con `[[nombre]]` se salta entre páginas, reuniones y proyectos sin importar en qué carpeta o fecha vivan.

**Archivar es una operación deliberada.** Archivar una rama no es mover archivos: implica resolver pendientes abiertos, reasignar cadencias y asegurar que los enlaces desde bitácoras ya cerradas sigan resolviendo (`archivado/`). Por eso el sistema nunca archiva solo: propone y delibera con el autor.

### 8. Las notas son espontáneas o tipadas; los ámbitos, ontológicos

En `notas/` conviven dos naturalezas:
- **Notas libres:** zettelkasten de formato libre para ideas y reflexiones espontáneas.
- **Notas tipadas:** notas sobre entidades recurrentes (personas, clientes, sistemas) que declaran `tipo:` en su frontmatter y siguen una plantilla y procedimiento de destilado en contexto aislado.

**Regla ética para notas de terceros (`persona`):** la nota describe a alguien que podría leerla. Se infiere lo que sirve para trabajar mejor con esa persona, no lo que sirve para juzgarla. **Una inferencia que no se le podría mostrar a la persona no va escrita.**

La página de un **ámbito**, en cambio, define compromisos y naturaleza operativa. El agente documenta modelos observados como descripciones revisables (*he visto que con estos clientes sueles…*), nunca como normas impuestas. Describir el comportamiento del autor no es decidir por él.

### 9. Reconstruir lo derivado debe devolver lo mismo

Si se borran todos los archivos derivados (`index.md`, `log.md`, `reportes/`, etc.) y se regeneran a partir del conjunto canónico, se obtiene exactamente el mismo resultado: **idéntico byte a byte** si lo generó un janitor; equivalente en significado si lo redactó un agente.

El conjunto canónico (`AHORA.md`, `bitacoras/`, `PENDIENTES.md`, `ambitos/`, `notas/`) es intocable y no se regenera.

Este es el test fundamental de arquitectura: si una salida generada por janitor no produce el mismo resultado dos veces, existe un defecto de no-determinismo. Ninguna operación de janitor es válida sin **idempotencia estricta**.