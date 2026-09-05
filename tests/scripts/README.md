# tests/scripts

Pasos deterministas reutilizables entre escenarios: instalar una variante, invocar un janitor con argumentos (la "segunda vía" de `spec/flujo-informacion.md`), o construir un estado intermedio sin repetir la lógica en cada test de `tests/escenarios/`.

Se llenó cuando apareció el segundo consumidor real, que era la condición: `001-001` y `001-002` afirman lo mismo sobre un vault recién instalado y estaban duplicando el cuerpo entero.

| Módulo | Qué ofrece |
| --- | --- |
| `vault.py` | `diff_recursivo` contra el template en vivo, `ahora_sembrado` para derivar el esperado sin congelarlo, y `placeholders_sin_sustituir` para que un placeholder nuevo en el template no pase en silencio |

Sigue sin haber janitors que invocar (el epic 001 no entra ninguno). Esa parte se decide cuando el epic 002 la necesite.
