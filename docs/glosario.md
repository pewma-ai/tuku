# Glosario

> `docs/glosario.md` · Vocabulario preciso del proyecto. Cuando un término aparece en
> `docs/`, `spec/` o en el código, significa esto y no otra cosa.
>
> Convención de idioma: las primitivas del dominio se nombran en español, tanto en la
> documentación como en lo que ve el usuario. Los campos de front matter y los
> identificadores internos van en inglés.

---

## Primitivas del dominio

**Entrada** — Un hecho fechado que pertenece a una entidad y lleva una clasificación. Es la
unidad de registro de la bitácora. Inmutable: una entrada nunca cambia de fecha. No
confundir con *bitácora*, que es el archivo donde se escriben.

**Bitácora** — El archivo de un ciclo donde se registran las entradas de cada día
(`bitacora_FECHA_tipo.md`). También, por extensión, la sección proyectada dentro de una
entidad que muestra sus entradas; esa sección no es un archivo ni una copia.

**Tarea** — Compromiso de acción con estado, pertenencia a una entidad y temporalidad en
tres grados: fecha precisa, ventana difusa ("en dos semanas") o sin fecha. Puede depender
de otras tareas y activar otras al completarse. En español siempre *tarea*; nunca *TODO*.

**Entidad** — Cualquier cosa sobre la que se gestiona: un área, un proyecto, un cliente, un
instrumento, un profesional de la salud. Tiene `type` como string libre, plantilla,
cadencias propias y una descripción que el agente infiere y el humano corrige. Vive en
`VIGENTES/` o `ARCHIVADAS/`.

**Cadencia** — Regla que produce artefactos en el tiempo: bitácoras, tareas o alertas.
Tiene un **origen** (sistema, tipo de entidad, entidad concreta) y una **forma de disparo**
(absoluta, relativa a evento, por ausencia, por completitud). Absorbe lo que en otros
sistemas serían rituales cableados.

**Ciclo** — El período que define la vida del usuario, no el almanaque: un turno de martes
a martes, un descanso, una semana ISO, un semestre. Lo declara una cadencia. Al abrirse
produce plan y bitácora; al cerrarse produce resultados.

**Capacidad** — Tiempo y recursos disponibles del usuario, en `estrategia/capacidad.md`.
Es la restricción contra la que se contrasta el plan y, junto con los objetivos de las
entidades vigentes, lo que determina qué se archiva.

**Nota** — Documento del eje deliberativo: ideas desarrolladas y conclusiones sedimentadas.
No es temporal ni pertenece necesariamente a una entidad. La destilación ocurre al
escribirla; no hay ritual de destilación en el sistema.

**Clasificación** — Etiqueta obligatoria de una entrada, extensible por configuración:
`hito`, `decision`, `senal`, `friccion`, `msg`. Es lo que permite que el informe de cierre
sea mayormente un filtro determinista.

---

## Modelo de datos

**Canónico** — Lugar único donde un dato se escribe. Fuente de verdad. Editable por el
humano o por el agente.

**Proyección** — Contenido generado filtrando o transformando canónicos. Nunca se edita a
mano; se regenera. Borrar una proyección no pierde información.

**Derivación** — La relación declarada `D = f(A₁…Aₙ)` entre un derivado y sus fuentes,
registrada en el grafo de `.tuku/config.yaml`.

**Compuesto** — Documento que mezcla secciones editables y derivadas. La página de una
entidad es el caso típico.

**Sección** — Bloque de un compuesto delimitado por marcas y con `id` estable, declarado
como `editable` o `derived`. No hay secciones ambiguas.

**Átomo** — Sección promovida a archivo independiente. **Diferido** en la versión actual;
el gancho existe porque toda sección tiene `id`.

**Replay** — Reconstrucción del estado completo desde un perfil vacío más el log de
entradas y eventos. Lo determinista se exige con diff cero; lo semántico, por equivalencia.
Es el test estructural del modelo canónico y un detector de agencia mal ubicada.

---

## Motor

**Motor** — Código, janitors, procesos y plantillas. Instalado vía pipx, versionado por
PEWMA.AI, vive fuera de los datos.

**Perfil** — Repositorio Git de un usuario con sus datos. Portable, con `schema_version`
declarada, propiedad del usuario.

**Janitor** — Script Python determinista que garantiza invariantes o construye
derivaciones. Idempotente por construcción: correrlo dos veces da el mismo resultado.

**Invariante** — Propiedad verificable del perfil, garantizada por un janitor. Ejemplos:
front matter válido, enlaces que resuelven, grafo acíclico.

**Proceso** — Instrucciones en Markdown para una operación multi-paso (apertura de ciclo,
cierre, alta de entidad). Escritas para ser ejecutables por un humano disciplinado o por un
agente de inteligencia media.

**Agente** — El LLM cumpliendo una función. Hay **una sola interfaz conversacional
visible**; planificar, vigilar y analizar son funciones internas, no personajes con nombre.

**Build sobre diff** — Estrategia de recomputación: el motor recibe la lista de archivos
cambiados y recomputa solo lo alcanzable desde ellos, en vez de escanear el perfil
completo.

**Gate** — Punto donde una escritura requiere aprobación humana explícita. Aplica a todo
cambio en `estrategia/` (P5).

---

## Contexto

**MaC** — *Management as Code*, la metodología de PEWMA.AI. TUKU la implementa en su
variante personal. Metodología y producto se versionan por separado.

**TUKU** — De *tukulpan*, mapudungun: recordar, traer a la memoria. El nombre es la
promesa: lo que entró vuelve solo cuando corresponde.

**Sembrar** — Generar un borrador que el humano corregirá y del que pasará a ser dueño.
Un artefacto sembrado se genera una vez; ningún janitor vuelve a pisarlo.

**Tesauro vivo** — Índice de nombres de entidades y sus `keywords`, inyectado en el
contexto del agente en cada turno. Es lo que permite entender "avancé en ELIANA" sin
ambigüedad.
