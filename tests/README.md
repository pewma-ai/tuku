# tests/

Se construye solo desde los epics ([`../devel/epics.md`](../devel/epics.md)), no por adelantado: la suite del diseño anterior se borró entera en vez de arrastrarla a medio migrar.

| Directorio | Qué hace |
|---|---|
| [`unitarios/`](unitarios/README.md) | Pruebas de grano fino en memoria: funciones puras, parsers y lógica interna |
| [`escenarios/`](escenarios/README.md) | El caso narrativo y su arnés, uno junto al otro, sobre el vault |
| [`scripts/`](scripts/README.md) | Pasos deterministas compartidos entre escenarios |

Para correr toda la suite:
```bash
uv run pytest
```

Para correr solo los tests unitarios:
```bash
uv run pytest --unittests   # o uv run pytest --unit
```

El nombre del test de escenario ya es el tag de su epic: `uv run pytest tests/escenarios/ -k 001` filtra sin necesitar marcadores ni script propio. Ver [`escenarios/README.md`](escenarios/README.md#cómo-correr).
