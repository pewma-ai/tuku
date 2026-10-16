# tests/scripts

El arnés de los escenarios de [`../escenarios/`](../escenarios/README.md).

| Módulo | Qué ofrece |
| --- | --- |
| `gherkin.py` | `correr` ejecuta un escenario desde su `.md`: corre los bloques de `Dado`, `Cuando` y `Entonces` en `<banco>/<slug>/`, con `TUKU_HOME` en el checkout, y devuelve la corrida para que el test afirme. |
| `vault.py` | Los dos playgrounds: `BANCO` (en `/tmp`) donde se corre y `ARCHIVO` (`playground/`) donde el autor revisa; `archivar` copia del uno al otro. `instantanea` y `delta` comparan dos estados; `diff_recursivo`, `ahora_sembrado` y `placeholders_sin_sustituir` comparan contra el template en vivo. |
| `agente.py` | `turno` corre un turno de agente en un vault y devuelve lo que **ejecutó**, anotado por un `tuku` puesto al frente del `PATH`. El arnés y el modelo salen del entorno (`TUKU_AGENTE`, `TUKU_AGENTE_BIN`, `TUKU_AGENTE_MODELO`); `disponible()` dice si hay con qué correr. |

En un `.md`, un bloque `bash` es un comando y un bloque `agente` es lo que el autor le dice al agente; su resultado queda en `corrida.turno`.
