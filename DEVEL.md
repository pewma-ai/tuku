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
| [`devel/`](devel/epics.md) | Plan de construcción: epics, fases, entorno y diario de iteraciones | Planificación |
| [`template/`](template/README.md) | Estructuras Markdown iniciales que se siembran en un nuevo vault | Producto |
| [`src/`](src/) | Código fuente del paquete Python `tuku` | Implementación |
| [`corpus/`](corpus/README.md) | Dictados de referencia reales y ficticios para pruebas de proceso | Datos |
| [`tests/`](tests/README.md) | Capa unitaria en memoria y escenarios encadenados sobre el vault | Verificación |
| `playground/` | Entornos de prueba efímeros generados por los tests (ignorado por git) | Descartable |

Jerarquía de precedencia: Dentro de un epic, [`spec/`](spec/README.md) manda sobre el código. Entre epics, los experimentos y el uso mandan sobre [`spec/`](spec/README.md). [`devel/epics.md`](devel/epics.md) es la única fuente de verdad sobre el orden y estado de implementación.

## El ciclo de desarrollo e iteraciones

1. **Unidad de entrega y cortes:** Los epics cortan por **estado del vault** (`vacio`, `primer-dia`, `ciclo-en-curso`, etc.) y las fases técnicas cortan por **primitiva** interna ([`devel/epics.md`](devel/epics.md)). Se construye siempre de lo determinista a lo agéntico, de lo simple a lo complejo, y del caso feliz a los casos borde.
2. **Escalera de fixtures e idempotencia:** En los escenarios de vault, el estado final de un paso es el estado inicial del siguiente. Los tests comparan el `diff` exacto entre instantáneas en `playground/`. Toda operación sobre el vault debe ser idempotente: una segunda corrida debe arrojar un delta vacío.
3. **Registro obligatorio de iteración:** Toda sesión de trabajo inicia leyendo la última iteración y finaliza actualizando [`devel/iteraciones/AAAA-MM-DD.md`](devel/iteraciones/README.md). Se registran las tareas completadas, las decisiones tomadas con su justificación, los pendientes detectados y el estado de la suite de pruebas. Las decisiones que quedan en el chat se pierden.

## Reglas de implementación (`src/`)

- **Principio 1 (soberanía y offline):** Todo comando de TUKU opera localmente sobre archivos Markdown y debe tener su equivalente ejecutable "A mano" documentado. Si una función solo es operable mediante el software, viola el principio 1.
- **Contrato de CLI ([`spec/cli.md`](spec/cli.md)):** Códigos de salida fijos (`0` éxito, `1` rechazo justificado, `2` reservado para sintaxis de `argparse`). Toda salida de error o rechazo debe nombrar explícitamente el defecto y la acción correctiva sugerida. Una sola salida en prosa humana (sin flags como `--json`).
- **Centralización de lecturas:** Ningún comando lee archivos de configuración o reglas por su cuenta. Toda lectura de `config.tuku.md`, `LIBRO-DE-ESTILO.md`, plantillas u otros elementos de configuración se delega a [`src/tuku/config.py`](src/tuku/config.py).
- **Transparencia en Markdown:** No usar comentarios HTML para almacenar metadatos o estados ocultos. Los datos legibles por máquinas viven en secciones declaradas (pares clave-valor en negrita o tablas formales).

## Verificación y pruebas (`tests/`)

La suite separa las pruebas puras de lógica interna de la evolución de integración del vault:

| Capa | Ubicación | Propósito |
|---|---|---|
| **Unitarios** | [`tests/unitarios/`](tests/unitarios/README.md) | Funciones puras, parsers y lógica interna en memoria. Ultra-rápidos (~0,05s). |
| **Escenarios** | [`tests/escenarios/`](tests/escenarios/README.md) | Pruebas narrativas Gherkin (`Dado / Cuando / Entonces`) encadenadas en `playground/`. |

### Cobertura de tests unitarios

Toda función pura de parsing, formateo de texto, expresiones regulares o validación que opere en memoria (sin tocar disco ni red) debe contar con tests unitarios en [`tests/unitarios/`](tests/unitarios/README.md).
- Debe cubrir: caso nominal, entradas vacías y entradas malformadas.
- Los escenarios en [`tests/escenarios/`](tests/escenarios/README.md) se reservan para verificar la evolución del vault y la experiencia del usuario, no para agotar combinaciones de sintaxis interna.
- **Invariante de rendimiento:** La suite unitaria (`uv run pytest --unittests`) debe ejecutarse en menos de **0,2 segundos** y con cero I/O de disco. Es la única capa de tests que se fuerza en el hook de pre-commit.

### Modos de ejecución

- **Toda la suite determinista (por defecto):**
  ```bash
  uv run pytest
  ```
- **Solo tests unitarios:**
  ```bash
  uv run pytest --unittests         # o: uv run pytest --unit
  uv run pytest tests/unitarios/    # o por ruta
  ```
- **Escenarios de un epic específico:**
  ```bash
  uv run pytest tests/escenarios/ -k 002
  ```
- **Un escenario individual:**
  ```bash
  uv run pytest tests/escenarios/ -k 002_04
  ```
- **Tests con modelo LLM (agénticos):** Requieren tokens y no son deterministas. Excluidos por defecto.
  ```bash
  uv run pytest -m agentic
  ```
- **Instalación real desde la red:** Verifican descargas directas desde git con socket real. Excluidos por defecto.
  ```bash
  uv run pytest -m red
  ```

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
