# Entorno de Desarrollo y Restricciones

Normas del entorno de desarrollo, determinismo e invariantes de ejecución.

---

## 1. Comandos de Verificación (`uv`)

Requiere **Python 3.14**. Todo comando de desarrollo corre con `uv run`:

```bash
uv run pytest              # Suite sin tests agénticos (default en CI)
uv run ruff check .        # Linter de estilo e imports
uv run ruff format . --check # Formateo
uv run mypy src            # Verificación de tipos estricta
```

### Hook pre-commit
Configurado en `.pre-commit-config.yaml` reusando `uv run`. Instalación única:
```bash
uv run pre-commit install
```

---

## 2. Marcadores Pytest

- `not agentic` (default en `pyproject.toml`): Desactiva tests con LLM para no gastar tokens por accidente.
- `-m agentic`: Ejecución explícita de tests agénticos (F5).
- `--strict-markers`: Falla inmediatamente si un marcador no está registrado.

---

## 3. Determinismo e Invariantes

| Invariante                 | Solución                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Zona horaria**           | `TZ=UTC` forzado en `tests/conftest.py`.                                                                                        |
| **Fecha actual**           | Inyectada por parámetros; prohibido llamar `date.today()` directamente.                                                         |
| **Aislamiento Hermes**     | Tests usan `--safe-mode` + `--ignore-rules` y `HERMES_HOME` en `tmp_path`. Nunca levantar gateways en tests (usar `hermes -z`). |
| **Round-trip byte-a-byte** | Lectura/escritura de archivos canónicos no debe alterar espacios ni comentarios HTML                                            |
| **Modelos internos**       | Toda entidad interna debe usar `pydantic.BaseModel` v2                                                                          |
