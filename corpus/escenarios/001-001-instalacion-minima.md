# Escenario · 001-001-instalacion-minima

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 001, fase 0 (`devel/que_implementar.md`).

## Escenario: alguien sin conocimientos de informática instala TUKU y escribe su primera entrada

Dado un directorio vacío
Cuando se instala la variante `vanilla` con `src/install_test_scenario.py`
Entonces `AHORA.md` tiene los siete días de esa semana con su fecha real, sin placeholders
Y `PENDIENTES.md` tiene los cinco callouts de horizonte, vacíos (`spec/pendientes.md`)
Y `ambitos/personal/personal.md` existe y explica que es el único ámbito de partida
Y no hay ningún archivo que solo se pueda leer con TUKU instalado

## Escenario: la persona escribe a mano, sin agente

Dado el vault instalado
Cuando la persona abre `AHORA.md` en el día de hoy y escribe una línea con el formato de `AGENTS.md`
Entonces la entrada queda bien formada sin haber leído `spec/`, solo `AGENTS.md` y `LIBRO-DE-ESTILO.md`
Y nada se rompe si nunca corre ningún janitor

## Cómo se corre

Instalador de una línea, probado el 2026-09-04 contra el repo real:

```bash
curl -fsSL https://raw.githubusercontent.com/pewma-ai/tuku/devel/install.sh | sh -s -- playground/001-001-instalacion-minima
```

Sin fecha, usa el lunes de la semana en curso (así lo va a usar el autor real). Correrlo de nuevo pisa el destino.

Para no depender de la red ni del commit ya empujado, el mismo mecanismo se invoca directo (ver también `001-002-instalacion-local.md`):

```bash
python3 src/install_test_scenario.py --variante vanilla --destino playground/001-001-instalacion-minima --desde AAAA-MM-DD
```

## El test byte a byte

`../../tests/escenarios/test_001_001_instalacion_minima.py` fija la fecha en **2026-08-11** (martes), el mismo día donde arranca el ground truth de `corpus/referencia/referencia-faena.md` ("Turno Faena"), y compara contra el fixture en `../../tests/escenarios/fixtures/001-001-instalacion-minima/esperado/`.

La fecha fija no es arbitraria ni tiene que ser lunes: nada en `spec/` exige que un ciclo semanal empiece en lunes, así que el test elige a propósito una fecha que no lo es, para no dejar ese supuesto sin probar.

```bash
python3 tests/escenarios/test_001_001_instalacion_minima.py
```

## Qué se mira a mano

- Abrir el resultado en Obsidian: que no haya cajas de error ni archivos que Obsidian no sepa mostrar.
- Cronometrar cuánto toma escribir la primera entrada sin haber leído nada más que `AGENTS.md`. Si toma releer `spec/`, la fase 0 no está cumplida.
- Que una persona ajena al diseño (no el autor) la instale y opine, tal como pide el criterio de salida de la fase: se verifica con una persona, no con un diff.

## Qué destapó ya

- ~~El estado cero no es reproducible byte a byte sin fijar `--desde`...~~ **Resuelto:** el test fija `--desde 2026-08-11` y compara contra un fixture. El usuario real sigue instalando sin fecha (usa la de hoy); lo reproducible byte a byte es la garantía de prueba, no la experiencia real de instalar.
- **Bug real, encontrado por este mismo test al escribirlo:** `sembrar_ahora()` nombraba los siete días en orden fijo Lunes..Domingo sin mirar el día de la semana real de `--desde`. Con `--desde 2026-08-11` (martes), el primer día salía etiquetado "Lunes 11 de agosto". Corregido: el nombre real sale de `fecha.weekday()`.
