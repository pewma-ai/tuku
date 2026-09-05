# tests/

Se construye solo desde los epics ([`../devel/epics.md`](../devel/epics.md)), no por adelantado: la suite del diseño anterior se borró entera en vez de arrastrarla a medio migrar.

| Directorio | Qué hace |
|---|---|
| [`escenarios/`](escenarios/README.md) | El caso narrativo y su arnés, uno junto al otro |
| [`scripts/`](scripts/README.md) | Pasos deterministas compartidos entre escenarios (vacío hasta el epic 2) |

`correr.sh` es la forma de correr todo, un epic o un escenario. Ver [`escenarios/README.md`](escenarios/README.md#cómo-correr).
