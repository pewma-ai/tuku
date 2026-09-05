# Entorno de desarrollo

Python 3.14 con `uv`. Todo comando corre con `uv run`:

```bash
uv run ruff check .
uv run ruff format . --check
uv run mypy src
uv run pytest
```

`uv run pytest` todavía no corre: los marcadores y la jerarquía de `pyproject.toml` son del diseño anterior y se redefinen en el epic 2, junto con la suite. Mientras tanto los escenarios se corren directo:

```bash
python3 tests/escenarios/test_001_001_instalacion_minima.py
```

El hook de `pre-commit` está en `.pre-commit-config.yaml` y se instala una vez con `uv run pre-commit install`.

## Tres invariantes de determinismo

Son lo único de este documento que no depende de qué suite exista.

| Invariante | Cómo se cumple |
| --- | --- |
| **Zona horaria** | `TZ=UTC` forzado en `tests/conftest.py`, antes de la primera llamada a `time.localtime()`. Un test que pase en Chile y falle en CI es una tarde perdida |
| **Fecha actual** | Se inyecta por parámetro. Prohibido llamar `date.today()` dentro de la lógica: el usuario instala con hoy, el test con una fecha fija |
| **Round-trip byte a byte** | Leer y escribir un archivo canónico no altera espacios ni comentarios. Es el criterio del escenario `001-001` |

La segunda no es teórica: `sembrar_ahora()` etiquetaba los días por posición y solo se vio al fijar la fecha en un martes.
