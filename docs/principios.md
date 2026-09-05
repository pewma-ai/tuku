# TUKU: principios

> **Qué es este documento.** Con qué criterio se decide cuando aparece un dilema que nadie escribió todavía. Un principio sobrevive a cualquier reorganización del repositorio: si un `git mv` lo vuelve falso, no era un principio, era una spec. Ningún principio nombra un archivo ni una herramienta.
>
> Los otros dos documentos del marco: [`brief.md`](brief.md) responde qué problema resuelve TUKU y para quién, y le habla a quien todavía no decide usarlo. [`../spec/`](../spec/README.md) responde qué hace el sistema, con nombres, formatos e invariantes, y cambia cuando cambia el layout.

Orientación normativa, no contrato rígido.

### 1. El archivo de texto es lo primero

Todo lo que importa vive en archivos Markdown legibles sin ejecutar software propietario ni bases de datos. El frontmatter se mantiene al mínimo: si hace falta un programa especial para entender los datos, la arquitectura está mal.

Horizonte: veinte años. La prueba de fuego es que el sistema completo se pueda operar a mano con un editor de texto básico, aunque tome más esfuerzo. La automatización existe para absorber ese esfuerzo mecánico, nunca para volverlo obligatorio, y por eso toda automatización declara por escrito su equivalente manual. Una que no lo declare es una dependencia disfrazada.

**La especificación sobrevive, la implementación se reemplaza.** Un script de hoy no correrá en veinte años, pero la descripción de lo que hacía sí se leerá.

### 2. La organización emerge del uso

Cero configuración inicial. El primer día hay una página en blanco y una sola pregunta: *¿qué anotaremos hoy?*. Lo que el sistema sabe de la vida del autor, sus clientes, proyectos y ritmos de trabajo, se destila de lo que quedó registrado día a día, no de un formulario.

Corolario de diseño: **lo que debe emerger no se especifica por adelantado**. Se deja espacio para que la práctica aparezca sola, y cuando se consolida, se anota como regla.

Segundo corolario: **nada de lo que sirve para anticipar puede ser requisito para registrar**. Declarar recurrencias o dimensionar cuánto cabe en un ciclo son piezas deseables, no puertas de entrada. Sin ellas el sistema registra y devuelve lo registrado; con ellas además se adelanta. Un sistema que exige configurar antes de dejar escribir no sobrevive al primer día.

### 3. El agente es un secretario, no un dueño

Un solo agente conversa con el autor y sostiene su contexto global. Detrás de él se organizan otros agentes y procesos deterministas para tareas específicas.

Su rol es proponer, jamás ratificar. Redacta borradores y sugiere cambios, pero no modifica reglas ni ejecuta decisiones sin autorización. Opera bajo higiene estricta: silencio por defecto, contexto mínimo por sesión y sin interrupciones innecesarias.

Mantiene además curiosidad operativa: si nota que algo encaja mejor en otra parte, lo propone.

### 4. Todo baja hasta donde alcance el determinismo

```
reglas escritas  →  proceso determinista  →  agente (LLM)  →  autor
```

Cada nivel libera de carga al siguiente. Al implementar cualquier funcionalidad se empuja hacia la izquierda tanto como sea posible: si un programa determinista puede resolverlo, no se gastan tokens ni juicio de un LLM; si el agente puede redactar el borrador, no se consume tiempo del autor.

Al autor le queda lo irreductible: gobernar, ratificar y decidir.

El LLM se aísla en los dos extremos, la entrada (interpretar dictado y convertirlo en hecho estructurado) y la inferencia semántica (resúmenes, destilado y propuestas). Todo el medio es determinista.

### 5. Las reglas se escriben en prosa, en un solo lugar

Cómo se escribe y cómo se organiza el repositorio vive en un texto en prosa que leen igual el autor y la máquina, y del que nacen los automatismos. No hay lógica de gestión escondida dentro del código.

La especificación de cada automatismo acompaña al libro del autor; el código ejecutable vive fuera, instalado aparte. Así el libro no se vuelve una copia del programa que después diverge por su cuenta.

Si una regla no cabe en esa prosa, todavía no es una regla madura.

### 6. Tres ejes, y un conjunto canónico que no se regenera

El sistema indexa cada hecho por tres dimensiones a la vez: **cuándo** ocurrió, **sobre qué** ocurrió y **qué se concluyó** de él. El tiempo es un continuo que va del pasado registrado al futuro comprometido; el ámbito es el frente de la vida al que el hecho pertenece; la deliberación es lo que el autor entendió a partir de ahí. Cualquier vista útil es un corte sobre esos ejes, y el valor del sistema aparece en los cruces, no en cada eje por separado (ver [`brief.md`](brief.md), "Los tres ejes").

De ahí salen las primitivas, en ese orden y no al revés: la bitácora sirve al tiempo, los ámbitos a la estructura, las notas a la deliberación, y los pendientes y las cadencias cruzan el tiempo con las otras dos.

El **conjunto canónico** es la fuente primaria y **nunca se regenera**. Todo lo demás es una vista de él, y ninguna vista guarda un registro paralelo.

### 7. Las carpetas archivan; los enlaces conectan

La jerarquía de directorios refleja la estructura de la vida del autor y sirve para archivar. Dentro de ella **la regla más cercana prevalece**: una regla escrita más adentro afina la de arriba sin repetirla.

Los enlaces conectan transversalmente, y son lo que permite saltar entre páginas, reuniones y proyectos sin importar en qué carpeta o fecha vivan.

**Archivar es una operación deliberada.** No es mover archivos: implica resolver compromisos abiertos, reasignar recurrencias y asegurar que los enlaces escritos en el pasado sigan resolviendo. Por eso el sistema nunca archiva solo: propone y delibera con el autor.

### 8. Lo que se infiere sobre alguien se le podría mostrar

El sistema escribe inferencias sobre personas: sobre el autor y sobre terceros que aparecen en su trabajo.

Sobre el autor, lo observado se redacta como descripción revisable (*he visto que con estos clientes sueles…*) y nunca como norma. Describir su comportamiento no es decidir por él.

Sobre un tercero vale eso y una regla más: se infiere lo que sirve para trabajar mejor con esa persona, no lo que sirve para juzgarla. La prueba es directa, **una inferencia que no se le podría mostrar a la persona no va escrita**.

### 9. Reconstruir lo derivado debe devolver lo mismo

Si se borra todo lo derivado y se regenera desde el conjunto canónico, se obtiene el mismo resultado: idéntico byte a byte si lo generó un proceso determinista, equivalente en significado si lo redactó un agente.

Este es el test fundamental de arquitectura. Si una salida determinista no produce el mismo resultado dos veces, hay un defecto de no determinismo. Ninguna operación automática es válida sin **idempotencia estricta**.

Y su recíproco, que es el que ordena el resto del diseño: si algo que debía ser idéntico tras reconstruir solo resulta equivalente, hay juicio de un agente donde correspondía una regla.
