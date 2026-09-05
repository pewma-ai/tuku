# tests/

Se construye solo desde los epics ([`../devel/epics.md`](../devel/epics.md)), no por adelantado: la suite del diseño anterior se borró entera en vez de arrastrarla a medio migrar.

| Directorio | Qué hace |
|---|---|
| [`escenarios/`](escenarios/README.md) | El caso narrativo y su arnés, uno junto al otro |
| [`scripts/`](scripts/README.md) | Pasos deterministas compartidos entre escenarios |

El nombre del test ya es el tag de su epic: `uv run pytest tests/escenarios/ -k 001` filtra sin necesitar marcadores ni script propio. Ver [`escenarios/README.md`](escenarios/README.md#cómo-correr).
