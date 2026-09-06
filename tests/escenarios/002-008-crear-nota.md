# Escenario · 002-008-crear-nota

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 002, punto 5, fase 5 en su **versión mínima**: crear una nota a petición y enlazarla. Notas tipadas con plantilla y destilado del histórico no entran.

## Estado inicial

El que dejó [`002-007-crear-ambito`](002-007-crear-ambito.md): existe el ámbito `depto-centro` y `notas/` está vacío.

## La consecuencia "nota" todavía no está en la spec

[`../../spec/flujo-informacion.md`](../../spec/flujo-informacion.md) tiene una tabla de consecuencias con pendientes, enlaces, cadencias y propuesta. La nota no está, y el punto 5 del epic la exige. La spec dice que la lista es abierta y que agregar una consecuencia es agregar un archivo en `reglas/`, así que este escenario es el que obliga a escribir `reglas/notas.tuku.md` y la fila que falta.

Es lo primero que el epic 002 mueve en el diseño, y estaba previsto en `epics.md` antes de empezar.

## Escenario: la nota se escribe donde corresponde

Dado el ámbito `depto-centro` ya creado
Cuando el autor pide *"una nota respecto al depto centro: cómo funciona el cobro de gastos comunes en una copropiedad"*
Entonces existe `notas/gastos-comunes-en-copropiedad.md`
Y su frontmatter trae `created` con la fecha de hoy
Y el cuerpo es el que el agente redactó, tomado del fixture congelado

## Escenario: queda constancia en la bitácora

Dado el mismo estado
Cuando la nota se escribe
Entonces hay una entrada nueva en el martes 11 que deja constancia de la nota creada
Y esa entrada enlaza a la nota
Y no hay ninguna otra entrada narrando el mecanismo

Crear la nota es un hecho de la vida del autor (lo pidió), a diferencia de mover un pendiente de escalón, que es un hecho del sistema. Por eso esta sí se registra y aquella no.

## Escenario: la nota queda enlazada a su ámbito, porque se pidió así

Dado que la petición dijo *"respecto al depto centro"*
Cuando la nota se escribe
Entonces la nota enlaza al ámbito `depto-centro`
Y el enlace resuelve a una página que existe

Si la petición no hubiera nombrado un ámbito, la nota quedaría suelta y eso sería correcto.

## Escenario: "Ver además" existe y cada enlace lleva motivo

Dado la nota ya escrita
Cuando corre `jntr.notas-lint`
Entonces la nota tiene una sección `## Ver además`
Y cada enlace de esa sección va seguido de texto de motivo
Y el lint no falla

La **presencia** de la sección y del motivo es verificable sin juicio. Que el motivo sea pertinente y no relleno solo lo evalúa quien lee, y por eso está más abajo y no acá ([`../../spec/notas.md`](../../spec/notas.md)).

## Escenario: crear la nota dos veces no duplica nada

Dado la nota ya creada
Cuando se repite la operación
Entonces el diff es vacío
Y no hay una segunda entrada de constancia en la bitácora

## De dónde sale el contenido

Del fixture `fixtures/002-010-dictado-del-dia-uno/`, igual que las entradas de la cadena: el texto de la nota es salida de agente y no tiene original vivo contra el cual compararse. Lo que este escenario prueba es todo lo demás (dónde queda el archivo, la constancia, el enlace, el lint), que es determinista.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_008
```

## Qué se mira a mano

- **Leer el motivo del "Ver además".** Es la parte que ningún script puede juzgar: si el motivo no responde para qué le sirve al lector de esta nota hacer clic, está de relleno.
- Que la entrada de constancia en la bitácora se lea como un hecho del día y no como un log de sistema.
- Que la nota se sostenga sola dentro de un año, sin la conversación que la pidió.
