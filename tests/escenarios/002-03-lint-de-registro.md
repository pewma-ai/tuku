# Escenario · 002-03-lint-de-registro

**Cubre:** epic 002, fase 1, criterio de salida. `tuku entry lint`: ontología cerrada estricta, ontología abierta permisiva.

## Estado inicial

El que dejó [`002-02-registro-en-su-dia`](002-02-registro-en-su-dia.md): tres registros en el martes 11, `PENDIENTES.md` intacto.

```bash
cp -r ../../002-02-registro-en-su-dia/tres-registros-caen-en-el-dia-de-hoy-ordenados-por-hora/mi-vault .
```


## Escenario: un tipo abierto desconocido se reporta y se acepta

Dado el estado anterior, más una marca de la ontología cerrada mal escrita

```bash
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 13:00 - [[personal]] **Pendiente**: comprar una maleta"
```

Cuando se escribe un tipo abierto que nadie declaró, y se revisa

```bash
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 12:05 - [[personal]] **cachureo**: ordené los cables del escritorio"
tuku entry lint --vault mi-vault
```

Entonces el registro queda escrito en su día
Y el lint la reporta como tipo desconocido, para preguntar más adelante
Y el reporte no es un error: el lint termina en estado de éxito

Rechazar vocabulario nuevo impediría que la organización emerja ([`spec/bitacora.md`](../../spec/bitacora.md)).

## Escenario: la ontología cerrada se valida estricta

Dado el mismo estado
Cuando se escribe con la marca mal escrita, y se revisa

```bash
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 13:00 - [[personal]] **Pendiente**: comprar una maleta"
tuku entry lint --vault mi-vault
```

Entonces el lint lo reporta como error de la ontología cerrada
Y **no se abre ningún pendiente**: `**Pendiente**` no es `**pendiente**`, y el comando no interpreta
Y la línea queda escrita igual, porque un error del autor se reporta y nunca se rechaza

Este es el caso que separa las dos ontologías: la misma zona de la línea, dos tratamientos.

## Escenario: un registro fuera del rango del ciclo se reporta

Dado el mismo estado, con el ciclo abierto del 11 al 17 de agosto
Cuando se agrega a mano un día fuera de ese rango, y se revisa

```bash
printf '\n## Martes 25 de agosto\n\n- 08:00 - [[personal]] **progreso**: revisé la bodega\n' >> mi-vault/AHORA.md
tuku entry lint --vault mi-vault
```

Entonces el lint la reporta como fuera del rango del ciclo abierto
Y no se inventa el día que falta

## Escenario: el lint no escribe en el vault

Dado el mismo estado
Cuando se corre el lint dos veces seguidas sin escribir nada

```bash
tuku entry lint --vault mi-vault
tuku entry lint --vault mi-vault
```

Entonces el diff contra el estado inicial es vacío las dos veces
Y el reporte es idéntico

El lint informa, no corrige.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_03
```

Cada escenario deja su vault en `playground/002-03-lint-de-registro/<escenario>/mi-vault/`.


## Qué se mira a mano

- Leer el reporte: que se entienda cuál de los tres hallazgos exige acción y cuál es solo una pregunta.
- Que el hallazgo del tipo desconocido no suene a reto: es vocabulario del autor y el sistema pregunta qué significa.
