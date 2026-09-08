---
type: Config
---

> [!warning] Estos nombres no son tuyos
> Son el contrato con [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format). Renombrar uno rompe los comandos y deja el vault ilegible para cualquier herramienta que hable OKF. Es lo contrario de las tablas del libro de estilo, que sí se cambian a gusto.

| `type`        | Qué archivo                          | Se reconoce por                             |
| ------------- | ------------------------------------ | ------------------------------------------- |
| `Logbook`     | `AHORA.md` y todo lo de `bitacoras/` | Registros fechados, en orden de hora        |
| `Pending`     | `PENDIENTES.md`                      | Lo abierto, agrupado por horizonte          |
| `Scope`       | Los archivos de `ambitos/`           | Un frente de la vida del autor              |
| `Note`        | Los archivos de `notas/`             | Algo que no pertenece a un día              |
| `Cadence`     | Los `CADENCIAS.md`                   | Lo que vuelve                               |
| `Capacity`    | Los `CAPACIDAD.md`                   | Lo que rinde un día, y lo que se va antes   |
| `Config`      | Los archivos de `reglas/`            | Lo que las automatizaciones necesitan saber |
| `Style Guide` | `LIBRO-DE-ESTILO.md`                 | El vocabulario del autor                    |
