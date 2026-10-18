# Desarrollo de TUKU: Método y Guía Operativa

Guía de trabajo para agentes y colaboradores. Este repositorio contiene el motor de TUKU en Python; el vault del autor vive en su propio directorio y es lo que el motor crea y asiste.

## Principios de trabajo con el autor

- **Deliberar antes de escribir:** Separar el diseño de la ejecución. Durante discusiones conceptuales no se modifican archivos. La edición se realiza tras acordar la solución o por instrucción explícita.
- **Entrada por voz y dictado:** Las instrucciones del autor suelen llegar por dictado (audio a texto), con frases entrecortadas o autocorrecciones. Se debe interpretar la intención de fondo directamente, sin exigir reformulaciones ni detenerse en la sintaxis hablada.
- **Comunicación concisa y directa:** Respuestas breves, sin voseo, sin explicaciones obvias ni disculpas vacías. Reportar los cambios indicando el enlace al archivo y el resultado concreto. No repetir en el chat lo que ya quedó plasmado en el código o documento.
- **Una sola fuente de verdad (cero duplicación):** La información vive en un solo lugar. Si un dato se necesita en dos sitios, se enlaza o se transcluye. Nunca se copian tablas normativas, códigos ni contratos entre documentos.

## Dónde vive cada cosa

| Directorio | Qué contiene | Naturaleza |
|---|---|---|
| [`docs/`](docs/README.md) | Marco rector: brief, principios, glosario y libro de estilo | Fundacional |
| [`spec/`](spec/README.md) | Especificación normativa de primitivas y contratos del sistema | Normativo |
| [`devel/`](devel/epics.md) | Plan de construcción: epics, fases, dependencias, entorno y diario de iteraciones | Planificación |
| [`template/`](template/README.md) | Estructuras Markdown iniciales que se siembran en un nuevo vault | Producto |
| [`src/`](src/) | Código fuente del paquete Python `tuku` | Implementación |
| [`corpus/`](corpus/README.md) | Dictados de referencia reales y ficticios para pruebas de proceso | Datos |
| [`tests/`](tests/AGENTS.md) | Capa unitaria en memoria y escenarios encadenados sobre el vault | Verificación |
| `playground/` | Entornos de prueba efímeros generados por los tests (ignorado por git) | Descartable |

Jerarquía de precedencia: Dentro de un epic, [`spec/`](spec/README.md) manda sobre el código. Entre epics, los experimentos y el uso mandan sobre [`spec/`](spec/README.md). [`devel/epics.md`](devel/epics.md) es la única fuente de verdad sobre el orden y estado de implementación.

### Artefactos, spec y código

Antes de cambiar un artefacto del vault, esta tabla dice qué más se toca. La plantilla es `template/vanilla/<la misma ruta>`, que `python -m tuku._pack` empaqueta en `src/tuku/_home/` (ignorado por git). Un archivo derivado se cambia en su función constructora, nunca solo en disco.

| Artefacto | Spec | Módulos | Lo escriben |
|---|---|---|---|
| `AHORA.md` | [`bitacora.md`](spec/bitacora.md), [`ciclo.md`](spec/ciclo.md) | [`entry.py`](src/tuku/entry.py), [`ahora.py`](src/tuku/ahora.py), [`cycle.py`](src/tuku/cycle.py), [`regenerate.py`](src/tuku/regenerate.py) | `tuku entry create`, `tuku process cycle`; la región del día, `tuku regenerate` (tema `todo`) |
| `PENDIENTES.md` | [`pendientes.md`](spec/pendientes.md) | [`todo.py`](src/tuku/todo.py) | `tuku todo open`, `tuku todo close` |
| `ambitos/PENDIENTES-AMBITOS.md` | [`pendientes.md`](spec/pendientes.md), [`ambitos.md`](spec/ambitos.md) | [`regenerate.py`](src/tuku/regenerate.py) | `tuku regenerate` (tema `todo`) |
| `ambitos/<nombre>/<nombre>.md` | [`ambitos.md`](spec/ambitos.md) | [`scope.py`](src/tuku/scope.py), [`link.py`](src/tuku/link.py) | `tuku scope create`, `tuku scope rename`; la actividad, `tuku regenerate` (tema `scope`) |
| `notas/<slug>.md` | [`notas.md`](spec/notas.md) | [`note.py`](src/tuku/note.py) | `tuku note create` |
| `LIBRO-DE-ESTILO.md` | [`bitacora.md`](spec/bitacora.md) | [`style.py`](src/tuku/style.py), [`vocab.py`](src/tuku/vocab.py) | el autor; se lee con `tuku context` (tema `style`) |
| `reglas/config.tuku.md` | [`vault.md`](spec/vault.md) | [`config.py`](src/tuku/config.py), [`init.py`](src/tuku/init.py) | `tuku init` |
| `reglas/types.md` | [`vault.md`](spec/vault.md) | [`doctor.py`](src/tuku/doctor.py) | el autor; lo valida `tuku doctor` |
| `AGENTS.md` | [`despacho.md`](spec/despacho.md), [`agente.md`](spec/agente.md) | [`doctor.py`](src/tuku/doctor.py) | el autor; lo revisa `tuku doctor` |

Las cadencias y la capacidad todavía no tienen módulo (epic 006).

## El ciclo de desarrollo e iteraciones

1. **Unidad de entrega y cortes:** Los epics cortan por **estado del vault** (`vacio`, `primer-dia`, `ciclo-en-curso`, etc.) y las fases técnicas cortan por **primitiva** interna ([`devel/epics.md`](devel/epics.md)). Se construye siempre de lo determinista a lo agéntico, de lo simple a lo complejo, y del caso feliz a los casos borde.
2. **Escalera de fixtures e idempotencia:** En los escenarios de vault, el estado final de un paso es el estado inicial del siguiente. Los tests comparan el `diff` exacto entre instantáneas en `playground/`. Toda operación sobre el vault debe ser idempotente: una segunda corrida debe arrojar un delta vacío.
3. **Registro obligatorio de iteración:** Toda sesión de trabajo inicia leyendo la última iteración y finaliza actualizando [`devel/iteraciones/AAAA-MM-DD.md`](devel/iteraciones/README.md). Se registran las tareas completadas, las decisiones tomadas con su justificación, los pendientes detectados y el estado de la suite de pruebas. Las decisiones que quedan en el chat se pierden.
4. **Decisiones abiertas:** Lo que el diseño todavía no decide vive en una sola lista, [Decisiones abiertas](spec/README.md#decisiones-abiertas), y se lee al iniciar la sesión junto con la última iteración. Un epic que toca uno de esos temas lo decide, lo escribe en la spec que corresponde y lo saca de la lista.

## Reglas de implementación (`src/`)

- **Principio 1 (soberanía y offline):** Todo comando de TUKU opera localmente sobre archivos Markdown, y su ayuda dice qué archivos toca y cómo, con precisión para hacerlo con un editor ([`spec/cli.md`](spec/cli.md)). Si una función solo es operable mediante el software, viola el principio 1.
- **Contrato de CLI ([`spec/cli.md`](spec/cli.md)):** Los códigos de salida son contrato y viven en su tabla. Toda salida de error o rechazo debe nombrar explícitamente el defecto y la acción correctiva sugerida. Una sola salida en prosa humana (sin flags como `--json`).
- **Tres capas, y `tuku/cli/` es solo la de arriba.** El núcleo son funciones puras de texto a texto, sin disco, y es donde vive la lógica: `entry.add`, `todo.abrir`, `note.lint`. Encima, un caso de uso por comando en el módulo de su noun (`entry.add_al_vault`, `todo.cerrar_en_vault`, `note.crear_con_constancia`), que lee el vault, llama a su planner (`todo.plan_open`, `entry.plan_add`, `note.plan_create`) y entrega lo que decidió al ejecutor único [`plan.apply`](src/tuku/plan.py), que escribe solo lo que difiere, regenera lo derivado y devuelve un [`Resultado`](src/tuku/resultado.py). El planner es una función pura: recibe lo leído (`State`) y el instante (`now`), y devuelve un `Change` (los textos nuevos por ruta, el mensaje y los avisos) o el rechazo, así que sus reglas se prueban sobre texto, sin vault. Arriba del todo, [`tuku/cli/`](src/tuku/cli/), un módulo por noun: argparse y la traducción de ese `Resultado` a texto y código de salida, nada más. Una regla del sistema que termine dentro de un `_cmd_*` está en la capa equivocada, y la señal es que solo se puede probar con un escenario E2E. El núcleo puro de cada noun puede vivir en su propio módulo (`todo_core`, `scope_tree`), que el módulo del noun reexporta. El reloj se lee una sola vez, en [`cli.main`](src/tuku/cli/__init__.py), y baja como `now` hasta el caso de uso: ningún otro módulo llama a `date.today()` ni a `datetime.now()`.
- **Código en inglés:** identificadores, docstrings y comentarios del código nuevo van en inglés, sin mezclar castellano. Los mensajes que ve quien invoca `tuku` y los `.md` siguen en español. Lo existente no se renombra salvo que cambie por otra razón.
- **Centralización de lecturas:** Ningún comando lee archivos de configuración o reglas por su cuenta. Toda lectura de `config.tuku.md`, `LIBRO-DE-ESTILO.md`, plantillas u otros elementos de configuración se delega a [`src/tuku/config.py`](src/tuku/config.py).
- **Markdown:** Todo lo que se escribe en el vault sigue [`spec/markdown.md`](spec/markdown.md): el dialecto admitido, los datos de máquina en estructura visible y nunca comentarios HTML.

## Verificación y pruebas (`tests/`)

Las reglas de los tests, el lenguaje de los escenarios y cómo se corre la suite viven en [`tests/AGENTS.md`](tests/AGENTS.md).

## Entorno e higiene técnica

- **Entorno:** Python 3.14 gestionado mediante `uv`. Detalles de determinismo en [`devel/entorno-devel.md`](devel/entorno-devel.md).
- **Linters y tipado estricto:** Todo cambio debe mantener limpios:
  ```bash
  uv run ruff check .
  uv run mypy src tests
  ```
- **Hook de pre-commit:** Ejecuta `ruff`, `mypy` y los tests unitarios (`uv run pytest --unittests`) antes de cada commit. Se activa con:
  ```bash
  uv run pre-commit install
  ```
- **Instalación del paquete en desarrollo:**
  ```bash
  uv tool install "git+https://github.com/pewma-ai/tuku.git@devel"
  tuku init mi-vault
  ```
