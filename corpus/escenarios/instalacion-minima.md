# Escenario · instalacion-minima

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 1, fase 0 (`devel/que_implementar.md`).

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

```bash
python3 src/install_test_scenario.py --variante vanilla --destino playground/epic-1_test-1 --desde AAAA-MM-DD
```

Sin `--desde`, usa el lunes de la semana en curso. Correrlo de nuevo pisa `playground/epic-1_test-1`.

## Qué se mira a mano

- Abrir el resultado en Obsidian: que no haya cajas de error ni archivos que Obsidian no sepa mostrar.
- Cronometrar cuánto toma escribir la primera entrada sin haber leído nada más que `AGENTS.md`. Si toma releer `spec/`, la fase 0 no está cumplida.
- Que una persona ajena al diseño (no el autor) la instale y opine, tal como pide el criterio de salida de la fase: se verifica con una persona, no con un diff.

## Qué destapó ya

- El estado cero no es reproducible byte a byte sin fijar `--desde`: depende de la fecha de instalación. La fase 0 en `que_implementar.md` todavía dice "produce byte a byte el fixture `vacio`", y hay que decidir si el fixture fija una fecha o si el criterio se reescribe.
