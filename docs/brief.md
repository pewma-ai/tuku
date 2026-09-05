# TUKU: brief

> **Qué es este documento.** Qué problema resuelve TUKU y para quién. Le habla a alguien que todavía no decide usarlo y que quizá nunca lo instale, así que no nombra archivos, formatos ni herramientas: sobrevive intacto si mañana se renombra todo.
>
> Los otros dos documentos del marco: [`principios.md`](principios.md) da el criterio para decidir lo que aún no está escrito, y [`../spec/`](../spec/README.md) dice qué hace el sistema, con nombres y formatos.

### Qué es

TUKU es un sistema de gestión personal hecho exclusivamente de archivos de texto Markdown. Registra lo que el autor hace, recuerda lo que olvida, sostiene lo que concluye y devuelve todo eso cuando corresponde.

Gestionar una vida repartida en varios frentes ocurre casi entera dentro de la cabeza: recordar, comparar y decidir qué toca ahora es trabajo deliberado y caro (el Sistema 2 de Kahneman), del que no hay mucho al día. TUKU baja esa carga a archivos en disco para devolver la atención a lo que sí la merece.

El nombre viene de *tukulpan*, en mapudungun: recordar, traer a la memoria. Esa es la promesa exacta: **lo que entró a TUKU vuelve solo cuando corresponde**, sin que nadie tenga que acordarse de acordarse.

TUKU implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal. Producto y metodología se versionan por separado: la metodología describe cómo se gestiona; TUKU es una herramienta de software que la ejecuta.

### Para quién

Para personas con una vida multidimensional: trabajo formal, emprendimientos paralelos, familia, compromisos técnicos o comunitarios. Cada dimensión tiene sus ritmos, compromisos y vocabulario, y ninguna herramienta tradicional conecta esos mundos entre sí.

El **autor** de referencia puede ser un desarrollador que opera todo por terminal o la dueña de una Pyme de insumos escolares, con clientes que tienen sus propios ciclos (*vendí lápices hoy, ofrecer reposición en tres meses*) y donde hoy todo vive en la cabeza y en cuadernos. Ninguno de los dos es el centro del diseño: el sistema se concibe para ambos por igual.

El sistema habla el idioma del autor. La primera lengua es el español, y el vocabulario del día a día va siendo incorporado de manera orgánica.

### Los tres ejes

Cada hecho que entra a TUKU queda indexado a la vez por tres dimensiones: **cuándo** ocurrió, **sobre qué** ocurrió y **qué se concluyó** de él. El tiempo es un continuo que va del pasado registrado al futuro comprometido; el ámbito es el frente de la vida al que el hecho pertenece; la deliberación es lo que el autor entendió y decidió a partir de ahí. Son tres lecturas del mismo hecho, no tres archivos separados.

Ninguna de las tres es original por sí sola, y por separado están bien resueltas en otras herramientas. Lo que no existe es la triangulación. Un gestor de tareas tiene compromisos pero no sabe de qué proyecto son ni por qué se decidieron. Un sistema de notas enlazadas tiene la red de ideas pero no tiene tiempo ni compromiso. Una herramienta de proyectos tiene la estructura pero trata el arrastre de una tarea como un descuido del usuario, no como información sobre el proyecto.

El valor aparece en los cruces, y por eso los tres ejes son el diseño y no una forma de ordenar el índice:

- **Tiempo × ámbito** es la pregunta operativa del día: qué toca ahora en este frente, y qué se prometió aquí que sigue sin hacerse.
- **Ámbito × deliberación** es el foco: un frente cuyas conclusiones no se han movido en meses está pidiendo que se le baje la prioridad o se archive.
- **Tiempo × deliberación** es la trazabilidad: por qué se decidió así, leído desde la acción que lo motivó.
- **Los tres a la vez** es el diagnóstico: un pendiente que se arrastra cuatro ciclos, en un ámbito sin notas nuevas hace dos meses, dice que ese proyecto terminó y nadie lo declaró. Ningún eje por separado lo dice.

De ahí salen las primitivas, en ese orden y no al revés: la bitácora sirve al tiempo, los ámbitos a la estructura, las notas a la deliberación, y los pendientes y las cadencias son lo que cruza el tiempo con las otras dos.

> [!question] Lo que esta sección deja abierto #REVISAR
> La capacidad ya tiene dónde vivir y cómo se declara ([`../spec/ciclo.md`](../spec/ciclo.md) y [`../spec/ambitos.md`](../spec/ambitos.md)), pero sigue sin ubicarse respecto de los ejes: cuelga del ámbito y se gasta en el tiempo, así que no es un cuarto eje sino lo que mide cuánto cabe en el cruce de los dos primeros. Falta decidir si eso merece decirse aquí, en el brief, o si basta con que esté en las specs.

### Cómo funciona

Tres niveles, en este orden de importancia:

1. **Los archivos de texto.** Todo lo que importa vive en Markdown, es propiedad del autor, se lee con cualquier editor básico, viaja en un pendrive y sigue siendo legible cuando esta herramienta ya no exista (horizonte: 20 años). Hay una sola fuente de verdad, y el sistema completo se puede operar a mano sin ejecutar nada.
2. **Lo que trabaja solo.** Lo mecánico y repetitivo se resuelve sin intervención; lo que requiere criterio se redacta como borrador y se propone al autor. Nada se da por ratificado sin él: el sistema propone hacia arriba y el autor decide.
3. **Las herramientas.** Editores, visualizadores y canales de conversación son interfaces intercambiables. No cuentan como parte del diseño: se reemplazarán antes que los archivos de texto.

**La organización emerge.** No hay configuración inicial. El primer día hay una página en blanco y una sola pregunta: *¿qué anotaremos hoy?*. A medida que el autor escribe, el sistema ve nombres que se repiten y propone abrirles página, o pagos periódicos y propone recordarlos solo. El autor aprueba con una palabra.

**Las reglas están escritas en prosa.** Cómo se escribe y cómo se organiza todo vive en un texto que leen igual el autor y la máquina, y del que nacen los automatismos. No hay lógica de gestión escondida dentro del código.

> [!question] Qué salió de esta sección y dónde debería quedar #REVISAR
> Se quitaron por ser implementación, no brief: los nombres del conjunto canónico (viven en [`../spec/README.md`](../spec/README.md)), los términos "janitor", "transclusión", "secretario", "vault" y "estado cero" (glosario, specs y [`../template/README.md`](../template/README.md)), y la mención del libro de estilo como documento.
> Se quitó también la lista de herramientas concretas: **Claude Code, Hermes, Antigravity, Obsidian, Telegram u otra mensajería, visualizadores web o CLI**. El repositorio no las nombra en ningún otro lugar, así que ese dato se pierde si no se reubica. Destino natural: [`../devel/entorno-devel.md`](../devel/entorno-devel.md) (lo que se usa hoy para desarrollar) o [`../spec/agente.md`](../spec/agente.md) (lo que se espera del canal). Decidir y mover.

### Qué ofrece

Que cualquier persona quede gestionando con la disciplina de un project manager riguroso, sin haber estudiado gestión ni haberse vuelto una persona ordenada.

Y el mejor momento del producto: **abrir un ciclo y encontrarse con lo que uno había olvidado que se había prometido.**