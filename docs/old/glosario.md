# Glosario

> `docs/glosario.md` · Vocabulario preciso del proyecto. Cuando un término aparece en `docs/`, `spec/` o en el código, significa esto y no otra cosa. El porqué de cada uno está en [`brief.md`](brief.md); aquí solo está la definición.
>
> Convención de idioma: las primitivas del dominio se nombran en español, tanto en la documentación como en lo que ve el usuario. Los campos de front matter y los identificadores internos van en inglés.

---

## Los tres elementos

**Entrada** — Un hecho fechado que pertenece a una entidad y lleva una clasificación. Es la unidad de registro de lo que pasó. Inmutable: una entrada nunca cambia de fecha y no se corrige, se enmienda escribiendo otra. No confundir con *bitácora*, que es donde se leen.

**Bitácora** — Cualquier **proyección** de entradas. La *bitácora del ciclo* filtra por rango de fechas; la *bitácora de una entidad* filtra por pertenencia. Ninguna es un almacén: las entradas viven en `entradas/entradas.md` (activo) o `entradas/entradas-YYYY-MM.md` (archivado).

**Tarea** — Compromiso de acción con estado en `tareas/tareas.md`, pertenencia a una entidad y temporalidad en tres grados: fecha precisa, ventana difusa ("en dos semanas") o sin fecha. Puede depender de otras tareas y activar otras al completarse. Es el único de los tres elementos con vida propia: nace, espera, se hace o se abandona. En español siempre *tarea*; nunca *TODO*.

**Nota** — Documento del eje deliberativo: una idea desarrollada o una conclusión sedimentada. No es temporal y puede pertenecer a una entidad sin estar obligada a ello. A diferencia de una entrada, que es un hecho fechado e inmutable, una nota es mutable y se corrige editándola. Guarda solo lo que hará falta para retomar la idea, no el proceso de pensarla. Lleva `summary` obligatorio, que es lo que hace consultable el corpus sin leerlo entero (`spec/nota.md`).

**Stub** — Nota que existe solo para que un enlace resuelva, con `summary: ""`. Es un estado válido y declarado, no un pendiente: un stub que sigue vacío un año es información sobre la importancia real de ese concepto.

---

## Dónde y cuándo

**Entidad** — Cualquier cosa sobre la que se gestiona: un área, un proyecto, un cliente, un instrumento, un profesional de la salud. Tiene `type` como string libre, plantilla, cadencias propias, un `alineamiento`, que es su objetivo, y una descripción que el agente infiere y el usuario corrige. Su estado es `lifecycle: vigente | archivada` en front matter; el path lleva la jerarquía, no el estado.

**Ámbito** — Nivel raíz de la jerarquía de entidades y frontera de confidencialidad y de compartición (`personal/`, `trabajo/`). Es lo que se federa, lo que se excluye de un export y lo que puede tener convenciones propias. Todo perfil tiene al menos un ámbito `personal`. Qué se escribe dentro de cada uno es criterio del usuario: el sistema ofrece la separación, no sabe qué le debe confidencialidad a quién.

**Práctica** — Lo que se hace con las entidades de una misma clase, escrito una vez para toda la clase en vez de repetirse en cada una. Vive en el `AGENTS.md` del nivel que corresponde, de modo que una entidad nueva nace sabiendo cómo se la gestiona por el solo hecho de colgar de ahí. La práctica dice **qué** se hace; la cadencia dice **cuándo**.

**Cadencia** — Regla que produce artefactos en el tiempo: tareas, ciclos o alertas. Tiene un **origen** (sistema, tipo de entidad, entidad concreta) y una **forma de disparo** (absoluta, relativa a evento, por ausencia, por completitud). La disparada por ausencia es la que hace verdadera la promesa del nombre: nadie recuerda lo que dejó de hacer. Absorbe lo que en otros sistemas serían rituales cableados.

**Ciclo** — El período que define la vida del usuario, no el almanaque: un turno, un descanso, unas vacaciones, una misión. Se abre con una **intención** y se cierra con un **reporte**. Lo **declara** su archivo `plan_*`, que fija tipo, lugar y fechas; una cadencia puede proponerlo, pero el plan es la verdad. El conjunto de planes es el calendario del usuario y es contra él que se resuelven las fechas relativas.

**Reporte** — Lo que se escribe al cerrar un ciclo, y la memoria de largo plazo del sistema. El detalle crudo no se borra nunca, pero la pregunta por un año lejano se responde leyendo lo que se escribió al cerrarlo, no releyendo diez años de entradas sueltas. Nunca *informe*.

**Capacidad** — Tiempo y recursos disponibles del usuario, en `estrategia/capacidad.md`. Es la restricción contra la que se contrasta el plan y, junto con los objetivos de las entidades vigentes, lo que determina qué se archiva.

---

## Etiquetas y campos

**Clasificación** — Etiqueta obligatoria de una entrada, extensible por configuración: `hito`, `decision`, `senal`, `msg`. Es lo que permite que el reporte de cierre parta de un filtro determinista y no de una inferencia.

**Marcador** — Etiqueta inline (`#venta`, `#uno-a-uno`) distinta de la clasificación. String libre que indica el evento específico que una cadencia relativa a evento reconoce (`spec/entradas.md` §3.4).

**Originator** — Quién creó una tarea: `manual` o el `id` de la cadencia emisora. Permite que la tarea sobreviva como referencia blanda si la cadencia desaparece.

**Outcome** — Razón de cierre de una tarea no completada por avance normal: `cancelled | expired | superseded`, registrada con motivo en el comentario HTML.

---

## Modelo de datos

**Canónico** — Lugar único donde un dato se escribe. Fuente de verdad. Editable por el usuario o por el agente.

**Proyección** — Contenido generado filtrando o transformando canónicos. Nunca se edita a mano; se regenera. Borrar una proyección no pierde información.

**Derivación** — La relación declarada `D = f(A₁…Aₙ)` entre un derivado y sus fuentes, registrada en el grafo de `.tuku/config.yaml`.

**Compuesto** — Documento que mezcla secciones editables y derivadas. La página de una entidad es el caso típico.

**Sección** — Bloque de un compuesto delimitado por marcas y con `id` estable, declarado como `editable` o `derived`. No hay secciones ambiguas.

**Átomo** — Sección promovida a archivo independiente. **Diferido** en la versión actual; el gancho existe porque toda sección tiene `id`.

**Reconstrucción** — Borrar todo lo derivado y volver a construirlo desde lo que el usuario escribió. Lo producido por janitors debe volver idéntico; lo redactado por agentes, equivalente en sentido. Es el test estructural del modelo canónico y un detector de agencia mal ubicada: si algo que debía ser idéntico solo resulta equivalente, hay juicio del agente donde correspondía una regla. También llamado *replay* en el código.

---

## Motor y agente

**Motor** — Código, janitors, procesos y plantillas. Instalado vía pipx, versionado por PEWMA.AI, vive fuera de los datos.

**Perfil** — Repositorio Git de un usuario con sus datos. Portable, con `schema_version` declarada, propiedad del usuario.

**Janitor** — Script Python determinista que garantiza invariantes o construye derivaciones. No juzga ni interpreta: ordena, archiva, reconstruye, verifica. Idempotente por construcción: correrlo dos veces da el mismo resultado.

**Invariante** — Propiedad verificable del perfil, garantizada por un janitor. Ejemplos: front matter válido, enlaces que resuelven, grafo acíclico.

**`AGENTS.md`** — Archivo de reglas guardado en la carpeta de aquello que rige, y válido para todo lo que cuelga de ahí hacia abajo. Un nivel más adentro puede afinar la regla sin repetir la de arriba. Está escrito en prosa y sin destinatario técnico, porque debe servir igual al agente y al usuario; que haya que traducirlo para uno de los dos es señal de que está mal escrito. Es donde vive la lógica que en otros sistemas estaría en el código.

**Proceso** — Instrucciones en Markdown para una operación multi-paso (apertura de ciclo, cierre, alta de entidad). Escritas para ser ejecutables por un usuario disciplinado o por un agente de inteligencia media. Ver también *Proceso* en la sección siguiente, que es otra cosa.

**Agente** — El LLM cumpliendo una función sobre el perfil. Escribe lo que el usuario le cuenta y redacta borradores; lo determinista queda en los janitors. Planificar, vigilar y analizar son funciones suyas, no personajes con nombre. Puede llegársele desde distintos canales, pero es el mismo agente detrás de todos.

**Hermes** — El agente concreto de las fases iniciales, preconfigurado con las reglas de TUKU y con acceso al repositorio del usuario. Es una elección, no parte del diseño: se puede reemplazar sin perder nada, porque lo que el sistema garantiza no depende de él.

**Gate** — Punto donde una escritura requiere aprobación explícita del usuario. Aplica a todo cambio en `estrategia/`, que es donde vive lo que el usuario decidió sobre su propia gestión.

**Build sobre diff** — Estrategia de recomputación: el motor recibe la lista de archivos cambiados y recomputa solo lo alcanzable desde ellos, en vez de escanear el perfil completo.

**RADAR** — Capa de consulta bajo demanda sobre el estado actual del perfil (tareas bloqueadas, actividad anómala, seguimientos vencidos). Es determinista, no se materializa en archivo ni existe fuera de la consulta (`docs/arquitectura.md` §11).

---

## Superficies

**Obsidian** — Visor y editor local sobre la carpeta del perfil. Es la puerta de escritorio, no una dependencia: los archivos son Markdown y cualquier editor sirve.

**Quartz** — Publicación web del mismo contenido, para acceder sin instalar nada.

**Telegram** — Canal de captura desde el teléfono, para contar algo en una línea mientras se camina.

---

## Contexto

**MaC** — *Management as Code*, la metodología de PEWMA.AI. TUKU la implementa en su variante personal. Metodología y producto se versionan por separado.

**TUKU** — De *tukulpan*, mapudungun: recordar, traer a la memoria. El nombre es la promesa: lo que entró vuelve solo cuando corresponde.

**Proceso** (de gestión) — Patrón repetible que define pasos ordenados, responsables y reglas de avance, por ejemplo una cotización a cliente o la resolución de un bug. Especificado en `spec/proceso.md`. No confundir con los *procesos* del motor, que son instrucciones de operación.

**Instancia de proceso** — La aplicación concreta de una plantilla de proceso sobre una entidad específica en el tiempo, por ejemplo la cotización `cot-0042` sobre `distribuidora-sur`. Emite un grupo de tareas vinculadas por `process` y `step`.

**Tesauro vivo** — Índice de nombres de entidades y sus `keywords`, inyectado en el contexto del agente en cada turno. Es lo que permite entender "avancé en el paper" sin ambigüedad.
