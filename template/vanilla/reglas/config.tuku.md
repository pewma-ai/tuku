---
type: Config
---

> [!info] Generado por la instalación
> Esta tabla la escribió `tuku init`. Los valores son tuyos y se cambian cuando haga falta; los nombres de los campos no, porque son los que leen los comandos.

| Campo           | Valor              | Qué decide                                                             |
| --------------- | ------------------ | ---------------------------------------------------------------------- |
| `TZ`            | `TZ-DEL-SISTEMA`   | Qué día es HOY, y por lo tanto qué está atrasado                        |
| `cycle_name`    | `semana`           | Cómo se llama tu ciclo, o los nombres que se alternan en orden (`turno, descanso`). Los horizontes pueden nombrarse con él |
| `tuku_template` | `vanilla`          | La variante de la que salió este vault                                  |
| `tuku_version`  | `TUKU-VERSION`     | La versión de TUKU con la que se sembró. `tuku doctor` la compara con `~/.tuku` |
| `origen`        | `TUKU-ORIGEN`      | De dónde sale TUKU, para saber dónde revisar cambios                    |
| `scope_default` | `personal`         | El ámbito de un registro, un pendiente o su cierre cuando el comando no nombra otro |
| `date_format`   | `MMM/DD`           | Cómo se escribe la fecha de un pendiente en el callout de su ámbito: `MMM` es el mes abreviado (`Ago`), `MM` el mes en número, `DD` el día y `AAAA` el año |
| `context_note_limit` | `25` | Cuántas notas de cada tipo enlazable trae `tuku context note`, las de `updated` más reciente |
