# Escenario · 002-008-crear-nota

**Cubre:** epic 002, punto 5, fase 5 en su **versión mínima**: crear una nota a petición y enlazarla. Notas tipadas con plantilla y destilado del histórico no entran.

## Estado inicial

El que dejó [`002-007-crear-ambito`](002-007-crear-ambito.md): existe el ámbito `depto-centro` y `notas/` está vacío.

## La consecuencia "nota" todavía no está en la spec

La tabla de consecuencias de [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md) tiene pendientes, enlaces, cadencias y propuesta. La nota no está y el punto 5 la exige. Como la spec declara la lista abierta y agregar una consecuencia es agregar un archivo en `reglas/`, este escenario obliga a escribir `reglas/notas.tuku.md` y la fila que falta. Es lo primero que el epic 002 mueve en el diseño, previsto en `epics.md` antes de empezar.

## Escenario: la nota se escribe donde corresponde

Dado el ámbito `depto-centro` ya creado
Cuando el autor pide *"una nota respecto al depto centro: cómo funciona el cobro de gastos comunes en una copropiedad"*
Entonces existe `notas/gastos-comunes-en-copropiedad.md`
Y su frontmatter trae `created` con la fecha de hoy
Y el cuerpo es el que el agente redactó, tomado del fixture congelado

## Escenario: queda constancia en la bitácora

Dado el mismo estado
Cuando la nota se escribe
Entonces hay un registro nuevo en el martes 11 que deja constancia de la nota creada
Y ese registro enlaza a la nota
Y no hay ningún otro registro narrando el mecanismo

Crear la nota es un hecho de la vida del autor, que la pidió; mover un pendiente de escalón es del sistema. Por eso esta se registra y aquella no.

## Escenario: la nota queda enlazada a su ámbito, porque se pidió así

Dado que la petición dijo *"respecto al depto centro"*
Cuando la nota se escribe
Entonces la nota enlaza al ámbito `depto-centro`
Y el enlace resuelve a una página que existe

Si la petición no hubiera nombrado un ámbito, la nota quedaría suelta y eso sería correcto.

## Escenario: "Ver además" existe y cada enlace lleva motivo

Dado la nota ya escrita
Cuando corre `tuku note lint`
Entonces la nota tiene una sección `## Ver además`
Y cada enlace de esa sección va seguido de texto de motivo
Y el lint no falla

La **presencia** de la sección y del motivo se verifica sin juicio. Que el motivo sea pertinente y no relleno lo evalúa quien lee, y está más abajo ([`spec/notas.md`](../../spec/notas.md)).

## Escenario: crear la nota dos veces no duplica nada

Dado la nota ya creada
Cuando se repite la operación
Entonces el diff es vacío
Y no hay un segundo registro de constancia en la bitácora

## De dónde sale el contenido

Del fixture `fixtures/002-010-dictado-del-dia-uno/`: el texto de la nota es salida de agente. Todo lo que este escenario prueba (dónde queda el archivo, la constancia, el enlace, el lint) es determinista.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_008
```

## Qué se mira a mano

- **Leer el motivo del "Ver además".** Ningún script lo juzga: si no responde para qué le sirve al lector hacer clic, está de relleno.
- Que el registro de constancia en la bitácora se lea como un hecho del día y no como un log de sistema.
- Que la nota se sostenga sola dentro de un año, sin la conversación que la pidió.
