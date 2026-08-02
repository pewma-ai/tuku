# Entorno de desarrollo y restricciones de ejecución

> `devel/entorno-devel.md` · Normas de desarrollo, aislamiento y herramientas.

---

## 1. Aislamiento con `uv`

Para garantizar reproducibilidad y no contaminar el Python del sistema (requiere **Python 3.14**):

```bash
uv venv --python 3.14            # crea el entorno fijado en Python 3.14
uv pip install -e ".[dev]"       # motor en editable + herramientas de desarrollo
```

Todo comando de desarrollo se ejecuta dentro del entorno:

```bash
uv run pytest                    # suite completa, sin tests agénticos
uv run ruff check .              # estilo e imports
uv run ruff format .             # formateo
uv run mypy src                  # tipos, en modo estricto
uv run tuku doctor               # el motor, cuando exista
```

---

## 2. Comandos de la suite

| Comando | Para qué |
|---|---|
| `uv run pytest` | todo salvo lo agéntico — es lo que corre en CI |
| `uv run pytest -m spec` | solo los ejemplos normativos de `spec/` |
| `uv run pytest -m invariante` | solo los janitors |
| `uv run pytest -m aceptacion` | las simulaciones de `corpus/` |
| `uv run pytest -m replay` | reconstrucción con diff cero |
| `uv run pytest -m agentic` | **gasta tokens**, se pide explícitamente |
| `uv run pytest --cov=tuku` | cobertura de código |

`-m "not agentic"` está fijado en `pyproject.toml`: los tests que invocan un modelo nunca
corren por accidente.

**`--strict-markers` es deliberado.** Un marcador mal escrito (`@pytest.mark.agente` en vez
de `agentic`) haría que el test se saltara en silencio y nadie lo notaría durante meses. Con
esta opción, falla al instante.

---

## 3. Restricciones y principios

- **No gastar tokens en F0–F4.** Parsers, janitors, derivaciones, cadencias y CLI se prueban
  de forma determinista, sin invocar modelos. Un test que necesite un LLM en esas fases es
  señal de agencia mal ubicada (P3), no de que falte un modelo.
- **Spec-driven.** `src/` no inventa reglas: implementa lo que dice `spec/`, validado por los
  ADR. Ver el contrato en [`README.md`](README.md).
- **Round-trip byte a byte.** Leer un archivo canónico y reescribirlo no altera ni un byte de
  espaciado ni de comentarios. Obligación derivada de los ADR 0013 y 0014, que guardan datos
  canónicos dentro de comentarios HTML.
- **Aislamiento agéntico (F5).** Cada test instancia un perfil de Hermes desde cero vía
  `HERMES_HOME` apuntando a `tmp_path`.

---

## 4. Determinismo del entorno

Tres fuentes de irreproducibilidad, y cómo se cierran:

| Fuente | Cómo se cierra |
|---|---|
| **Zona horaria** | `TZ=UTC` fijado en `tests/conftest.py` antes de cualquier llamada a `localtime()` |
| **Fecha actual** | ninguna función del motor llama a `date.today()` directamente: la fecha se inyecta |
| **Entorno del usuario** | `--safe-mode` e `--ignore-rules` en Hermes; sin ellos, el `SOUL.md` y las skills locales entran al prompt |

La tercera es la que convierte "corre en mi máquina" en "corre igual en CI".

**Regla dura de Hermes:** nunca dos gateways contra el mismo directorio de datos. Los tests
no levantan gateway — solo `hermes -z`.

---

## 5. Antes de cada commit

```bash
uv run ruff check . && uv run mypy src && uv run pytest
```

Los tres en verde. La suite incluye chequeos de coherencia documental que no dependen del
motor, así que este comando es válido desde hoy.
