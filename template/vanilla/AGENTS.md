# Reglas de este vault

Este vault es la bitácora, notas y actividades de la vida de su autor, en Markdown.

## Cómo te invocan

| El primer prompt...                           | Haces                                                                                                                                                                                                                                                                 |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| empieza con `MAINTENANCE MODE`, en mayúsculas | No cargues nada más: ni `tuku context` ni ningún otro archivo. Sigue las instrucciones del prompt tal como están, sin despachar y sin preguntar. Lo que pide una decisión del autor queda sin escribir y va en tu respuesta final. Los Límites del final valen igual. |
| empieza con cualquier otra cosa               | Es una interacción natural con el autor. Carga la skill [asistente](reglas/skills/asistente/SKILL.md) y síguela.                                                                                                                                                                                                |


## Límites

| Nivel                | Regla                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Siempre**          | Links relativos a este Vault, no al sistema.                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Pregunta primero** | Leer, buscar o ejecutar fuera del vault. Si `tuku` falla sin que sea un error de lo que pediste (no arranca, no conecta), dilo y no lo depures. Mover archivos, o renombrar algo que no tenga su `rename`. Modificar cualquier `AGENTS.md` o `reglas/`, salvo un `*.user.md` cuando el autor declara una preferencia. Cerrar el ciclo, o tocar `bitacoras/` fuera de `tuku entry move`. Cerrar un pendiente cuando el autor no repitió su texto: confirma cuál es antes. |
| **Nunca**            | Editar a mano un archivo que tiene comando. Actuar sobre una petición ambigua. Escribir un pendiente que el autor no pidió. Marcar `(Hecho)` algo que nunca estuvo pendiente. Borrar sin confirmación.                                                                                                                                                                                                                                                                   |

El código de `tuku` vive fuera del vault, en su paquete. Sin `tuku` instalado el vault funciona igual, a mano: `reglas/comandos.tuku.md` dice qué hace cada comando y cómo hacerlo.
