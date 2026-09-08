# tests/scripts

Pasos deterministas reutilizables entre escenarios: instalar una variante, invocar un comando con argumentos (la "segunda vía" de `spec/flujo-informacion.md`), o construir un estado intermedio sin repetir la lógica en cada test de `tests/escenarios/`.

Se llenó cuando apareció el segundo consumidor real, que era la condición: `001-01` y `001-02` afirman lo mismo sobre un vault recién instalado y estaban duplicando el cuerpo entero.

| Módulo | Qué ofrece |
| --- | --- |
| `vault.py` | `diff_recursivo` contra el template en vivo, `ahora_sembrado` para derivar el esperado sin congelarlo, y `placeholders_sin_sustituir` para que un placeholder nuevo en el template no pase en silencio |
| `gherkin.py` | `correr` ejecuta un escenario leyendo su `.md`: parsea los bloques `bash` de `Dado`, `Cuando` y `Entonces` y los corre con el directorio de trabajo en `playground/<slug>/` y `TUKU_HOME` en el checkout. El `.md` es la fuente ejecutable y el arnés queda con las aserciones; la convención está en [`../escenarios/README.md`](../escenarios/README.md) |
| `cadena.py` | `preparar_paso` deja el vault inicial de un escenario 002-YY en `playground/<slug>/`, recién instalado si `previo=None` o copiado del paso anterior si no; `instantanea` y `delta` comparan dos estados, que es lo que afirma un escenario encadenado |

Los comandos viven en `src/tuku/`, un módulo por cada `noun` del CLI, con una función por `verb`. El primero es `tuku entry add` (`src/tuku/entry.py`, función `add`), que consume `002-01`. `cadena.py` todavía exige que el paso previo se haya corrido en la misma sesión de pytest; reproducir la cadena entera desde el fixture del epic queda pendiente.
