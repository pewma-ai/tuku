# Epic 010 · El tutorial entero

> **Marco:** [Brief de TUKU](../../docs/brief.md) · [Principios normativos](../../docs/principios.md) · [Especificaciones](../../spec/README.md) · [Tutorial](../../docs/tutorial/README.md)

Una persona nueva sigue el tutorial de Andrea de principio a fin, sobre un vault que sale de `tuku init`, y cada paso hace lo que su capítulo promete. El tutorial dice qué se le promete al autor; este epic comprueba que es cierto.

## Qué entrega el epic

1. **El extractor del tutorial:** lee un capítulo de [`docs/tutorial/`](../../docs/tutorial/README.md) y lo convierte en un plan para `test-tui`. Los bloques `> [!tip]` son las frases que dicta el autor, en orden y tal cual; los `> [!check]` son lo que se afirma tras el paso que los precede. Nada de eso se copia a un escenario.
2. **Pasos que no son del agente:** `tuku doctor` y las ediciones a mano del capítulo 5 (corregir una palabra, borrar una fila) corren entre turnos.
3. **La corrida en cadena:** los diez capítulos seguidos, cada uno sobre el vault donde terminó el anterior, con el vault de cada capítulo archivado en `playground/010-NN/`.

## Qué se verifica

- **Cada paso** deja un delta del vault y cada `check` se juzga contra él.
- **Las invariantes comunes** valen en todos los pasos: cada cambio del vault tiene su comando `tuku` en la traza, el agente no sale del vault y `tuku doctor` queda sano al final de cada capítulo.
- **Lo que se mira a mano** es lo que ningún archivo registra: si la pregunta de ambigüedad del agente era la correcta, y si el aviso de cambio de ciclo se entiende.

## Escenarios del epic

Cada escenario es un capítulo, y su fuente es el capítulo. Se corre con `uv run python tests/scripts/test-tui.py tutorial NN` (`3-6` o `1,4,7` para varios; sin número, los diez).

| Escenario | Capítulo | Parte de | Depende de |
| --- | --- | --- | --- |
| `010-01` | [Instalar](../../docs/tutorial/01-instalar.md) | Un directorio vacío | Epic 001 |
| `010-02` | [Registrar](../../docs/tutorial/02-registrar.md) | El vault del 01 | Epic 003 |
| `010-03` | [Pendientes](../../docs/tutorial/03-pendientes.md) | El vault del 02 | Epic 003 |
| `010-04` | [Frentes y notas](../../docs/tutorial/04-frentes-y-notas.md) | El vault del 03 | Epic 003 |
| `010-05` | [Corregir y revisar](../../docs/tutorial/05-corregir-y-revisar.md) | El vault del 04 | Epic 003 |
| `010-06` | [El día completo](../../docs/tutorial/06-el-dia-completo.md) | El vault del 05 | Epic 003 |
| `010-07` | [Conversar](../../docs/tutorial/07-conversar.md) | El vault del 06 | Epic 004 |
| `010-08` | [Una semana después](../../docs/tutorial/08-una-semana-despues.md) | El vault del 07 | Epic 005 |
| `010-09` | [Cerrar la semana](../../docs/tutorial/09-cerrar-la-semana.md) | El vault del 08 | Epic 006 |
| `010-10` | [Lo que nadie pidió](../../docs/tutorial/10-lo-que-nadie-pidio.md) | El vault del 09, con meses de historia | Epic 007 |

Los capítulos 1 a 6 dependen de lo que ya existe. Los capítulos 7 y 8 ya tienen sus epics (004 y 005). Los 9 y 10 corren contra una promesa: salen en rojo hasta que los epics 006 y 007 los construyan, y eso es lo esperado.

## Estado inicial común

Todos parten del `tuku init mi-vault` del capítulo 1, con el reloj en el lunes de Andrea: `TUKU_NOW="2026-08-17 08:30"`. Cada capítulo avanza el reloj lo que su historia pide (el 6 termina a media tarde del lunes, el 7 es el martes, el 9 es el lunes siguiente).

## Qué se mira a mano

- Que el lector entienda cada `check` sin conocer el sistema.
- Que ningún capítulo use un dato que el anterior no creó.
- Que la corrida en cadena no tarde más de una hora, que es lo que el tutorial promete.
