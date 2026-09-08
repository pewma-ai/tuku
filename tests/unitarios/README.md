# tests/unitarios/

Pruebas unitarias de grano fino sobre componentes de `src/tuku/`.

## Propósito

A diferencia de [`../escenarios/`](../escenarios/README.md) (que verifica flujos de integración y evolución del vault mediante escenarios Gherkin en `playground/`), esta capa verifica:
- Funciones puras de parsing y serialización (configuración, vocabularios, fechas).
- Reglas de validación y linters en memoria.
- Estructuras de datos internas y excepciones.

Se ejecutan en milisegundos, sin efectos colaterales en disco ni dependencias externas.

## Cómo correrlos

Se autoejecutan al correr la suite completa:

```bash
uv run pytest
```

Para correr **únicamente** los tests unitarios:

```bash
uv run pytest --unittests
# o bien:
uv run pytest tests/unitarios/
# o mediante el marcador:
uv run pytest -m unitario
```
