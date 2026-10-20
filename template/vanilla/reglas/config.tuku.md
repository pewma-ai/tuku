---
type: Config
---


| Campo                | Valor            | Qué decide                                                                                                                                                 |
| -------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TZ`                 | `TZ-DEL-SISTEMA` | Qué día es HOY, y por lo tanto qué está atrasado                                                                                                           |
| `tuku_template`      | `vanilla`        | La variante de la que salió este vault                                                                                                                     |
| `tuku_version`       | `TUKU-VERSION`   | La versión de TUKU con la que se sembró. `tuku doctor` la compara con `~/.tuku`                                                                            |
| `origen`             | `TUKU-ORIGEN`    | De dónde sale TUKU, para saber dónde revisar cambios                                                                                                       |
| `scope_default`      | `personal`       | El ámbito de un registro, un pendiente o su cierre cuando el comando no nombra otro                                                                        |
| `date_format`        | `MMM/DD`         | Cómo se escribe la fecha de un pendiente en el callout de su ámbito: `MMM` es el mes abreviado (`Ago`), `MM` el mes en número, `DD` el día y `AAAA` el año |
| `context_note_limit` | `25`             | Cuántas notas de cada tipo enlazable trae `tuku context note`, las de `updated` más reciente                                                               |
