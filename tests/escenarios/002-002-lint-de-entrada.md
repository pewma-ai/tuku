# Escenario · 002-002-lint-de-entrada

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 002, fase 1, criterio de salida. `jntr.entrada-lint`: ontología cerrada estricta, ontología abierta permisiva.

## Estado inicial

El que dejó [`002-001-entrada-en-su-dia`](002-001-entrada-en-su-dia.md): tres entradas en el martes 11, `PENDIENTES.md` intacto.

## Escenario: un tipo abierto desconocido se reporta y se acepta

Dado el estado anterior
Cuando se inyecta `- 12:05 - [[personal]] **cachureo**: ordené los cables del escritorio`
Entonces la entrada queda escrita en su día
Y el lint la reporta como tipo desconocido, para preguntar más adelante
Y el reporte no es un error: el lint termina en estado de éxito

Un linter que rechaza vocabulario nuevo impide que la organización emerja, que es justo lo que el diseño busca ([`../../spec/bitacora.md`](../../spec/bitacora.md)).

## Escenario: la ontología cerrada se valida estricta

Dado el mismo estado
Cuando se inyecta `- 13:00 - [[personal]] **Pendiente**: comprar una maleta`, con la marca mal escrita
Entonces el lint lo reporta como error de la ontología cerrada
Y **no se abre ningún pendiente**: `**Pendiente**` no es `**pendiente**`, y el janitor no interpreta
Y la línea queda escrita igual, porque un error del autor se reporta y nunca se rechaza

Este es el caso que separa las dos ontologías: la misma zona de la línea, dos tratamientos.

## Escenario: una entrada fuera del rango del ciclo se reporta

Dado el mismo estado, con el ciclo abierto del 11 al 17 de agosto
Cuando se inyecta una entrada fechada el 2026-08-25
Entonces el lint la reporta como fuera del rango del ciclo abierto
Y no se inventa el día que falta

## Escenario: el lint no escribe en el vault

Dado el mismo estado
Cuando se corre el lint dos veces seguidas sin inyectar nada
Entonces el diff contra el estado inicial es vacío las dos veces
Y el reporte es idéntico

El lint informa, no corrige. Es lo que permite correrlo cuantas veces haga falta sin miedo.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_002
```

## Qué se mira a mano

- Leer el reporte del lint como lo leería el autor: que se entienda cuál de los tres hallazgos exige acción y cuál es solo una pregunta pendiente.
- Que el hallazgo del tipo desconocido no suene a reto. Es vocabulario del autor, y el sistema está preguntando qué significa.
