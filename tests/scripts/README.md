# tests/scripts

Pasos deterministas reutilizables entre escenarios: instalar una variante, invocar un janitor con argumentos (la "segunda vía" de `spec/flujo-informacion.md`), o construir un estado intermedio sin repetir la lógica en cada test de `tests/escenarios/`.

Se llenó cuando apareció el segundo consumidor real, que era la condición: `001-001` y `001-002` afirman lo mismo sobre un vault recién instalado y estaban duplicando el cuerpo entero.

| Módulo | Qué ofrece |
| --- | --- |
| `vault.py` | `diff_recursivo` contra el template en vivo, `ahora_sembrado` para derivar el esperado sin congelarlo, y `placeholders_sin_sustituir` para que un placeholder nuevo en el template no pase en silencio |
| `cadena.py` | `preparar_paso` deja el vault inicial de un escenario 002-YYY en `playground/<slug>/`, recién instalado si `previo=None` o copiado del paso anterior si no; `instantanea` y `delta` comparan dos estados, que es lo que afirma un escenario encadenado |

Los janitors viven en `src/tuku/`, un módulo por cada `noun` del CLI, con una función por `verb`. El primero es `tuku entry add` (`src/tuku/entry.py`, función `add`), que consume `002-001`. `cadena.py` todavía exige que el paso previo se haya corrido en la misma sesión de pytest; reproducir la cadena entera desde el fixture del epic queda pendiente.
