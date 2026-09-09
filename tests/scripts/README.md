# tests/scripts

Pasos deterministas reutilizables entre escenarios: instalar una variante, invocar un comando con argumentos (la "segunda vía" de `spec/flujo-informacion.md`), o construir un estado intermedio sin repetir la lógica en cada test de `tests/escenarios/`.

Se llenó cuando apareció el segundo consumidor real, que era la condición: `001-01` y `001-02` afirman lo mismo sobre un vault recién instalado y estaban duplicando el cuerpo entero.

| Módulo | Qué ofrece |
| --- | --- |
| `vault.py` | Dueño de `playground/`: `preparar_dir` da la carpeta de un escenario, e `instantanea` y `delta` comparan dos estados, que es lo que afirma un escenario encadenado. Más `diff_recursivo` contra el template en vivo, `ahora_sembrado` para derivar el esperado sin congelarlo, y `placeholders_sin_sustituir` para que un placeholder nuevo en el template no pase en silencio |
| `gherkin.py` | `correr` ejecuta un escenario leyendo su `.md`: parsea los bloques `bash` de `Dado`, `Cuando` y `Entonces` y los corre con el directorio de trabajo en `playground/<slug>/` y `TUKU_HOME` en el checkout. El `.md` es la fuente ejecutable y el arnés queda con las aserciones; la convención está en [`../escenarios/README.md`](../escenarios/README.md) |
| `agente.py` | El arnés agéntico del epic 003: `turno` corre un turno dentro de un vault y devuelve lo que el agente **ejecutó**, no lo que dijo. La traza sale de un `tuku` puesto al frente del `PATH` que anota `argv` y delega en el real, así que el agente no coopera ni sabe que está siendo observado. Cuál arnés y qué modelo salen del entorno (`TUKU_AGENTE`, `TUKU_AGENTE_BIN`, `TUKU_AGENTE_MODELO`); `disponible()` dice si hay con qué correr, para que un escenario se salte en vez de fallar |

En un `.md`, un bloque `bash` es un comando y un bloque `agente` es lo que el autor le dice al agente. El segundo lo corre `agente.py` y deja el resultado en `corrida.turno`.

Los comandos viven en `src/tuku/`, un módulo por cada `noun` del CLI, con una función por `verb`. El primero es `tuku entry add` (`src/tuku/entry.py`, función `add`), que consume `002-01`.

`cadena.py` se retiró: desde que los escenarios toman sus comandos del `.md`, la herencia entre pasos de una cadena se escribe en el propio escenario con un `cp -r`, y no hace falta un módulo que la construya.
