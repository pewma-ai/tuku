# 002-09 · Creación de notas y enlaces

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33), [P7 (enlaces conectan)](../../docs/principios.md#L63) · **Brief:** [Eje deliberación y red zettelkasten](../../docs/brief.md#L27) · **Spec:** [`spec/notas.md`](../../spec/notas.md)

Crear una nota mediante `tuku note create` genera el archivo con frontmatter OKF (`type: Note`), estampa la constancia cronológica en la bitácora `AHORA.md` y exige que todo enlace saliente declare su motivo en `## Ver además`. La operación es atómica: si la constancia no cabe en el ciclo, la nota no se crea.

## Estado inicial

```bash
cp -r ../../002-08-crear-ambito/crear-un-ambito-deja-el-arbol/mi-vault .
cp ../../tests/escenarios/fixtures/002-09-crear-nota/cuerpo-nota.md .
```

## Escenario: la nota se escribe donde corresponde

Dado el ámbito `depto-centro` creado y `notas/` vacío
Cuando el autor solicita crear una nota asociada al ámbito
```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```
Entonces existe `notas/como-funciona-el-cobro-de-gastos-comunes-en-una-copropiedad.md`
Y su frontmatter incluye `type: Note` y `created: 2026-08-11`
Y el cuerpo coincide con el fixture redactado
Y la nota enlaza a `[[depto-centro]]`

## Escenario: queda constancia en la bitácora

Dado el mismo estado inicial
Cuando la nota se escribe
```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```
Entonces `AHORA.md` gana un registro bajo `## Martes 11 de agosto` enlazando a la nota:
`- 21:15 - [[depto-centro]] **nota**: escribí la nota [[como-funciona-el-cobro-de-gastos-comunes-en-una-copropiedad]]`

## Escenario: la nota queda enlazada a su ámbito, porque se pidió así

Dado que la petición indicó `--scope depto-centro`
Cuando la nota se escribe
```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```
Entonces la página propia `ambitos/depto-centro/depto-centro.md` recibe bajo `## Esta semana` la constancia de la nota
Y el enlace en la nota apunta a una página de ámbito existente

## Escenario: "Ver además" existe y cada enlace lleva motivo

Dado la nota ya creada en `notas/`
```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```
Cuando se valida con el linter
```bash
tuku note lint mi-vault/notas/como-funciona-el-cobro-de-gastos-comunes-en-una-copropiedad.md
```
Entonces la nota contiene la sección `## Ver además`
Y cada enlace va acompañado de su motivo explícito
Y el linter finaliza con código 0 (`EXITO`)

## Escenario: la nota recién creada deja el vault sano

Dado un vault limpio recién sembrado con su ámbito
```bash
tuku init vault-limpio --date 2026-08-11
tuku scope create depto-centro --vault vault-limpio
```
Cuando se crea la nota
```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault vault-limpio
```
Entonces `tuku doctor` valida que el vault está 100% sano
```bash
tuku doctor --vault vault-limpio
```

## Escenario: el lint reporta un enlace sin motivo y una sección que falta

Dado dos notas creadas a mano: una con enlace sin motivo y otra sin `## Ver además`
```bash
printf '# Nota\n\ncuerpo\n\n## Ver además\n\n* [[depto-centro]]\n' > sin-motivo.md
printf '# Nota\n\ncuerpo\n' > sin-seccion.md
```
Cuando se validan
```bash
tuku note lint sin-motivo.md
tuku note lint sin-seccion.md
```
Entonces ambas se rechazan con código 1 (`RECHAZO`) explicando el motivo faltante y la sección omitida

## Escenario: crear la nota dos veces no duplica nada

Dado la nota ya creada
```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```
Cuando se corre el mismo comando una segunda vez
```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```
Entonces el diff contra el estado previo es vacío (idempotente)
Y no se duplica la constancia en `AHORA.md`

## Escenario: una nota sin cuerpo se rechaza

Dado el vault de la cadena
Cuando se intenta crear una nota con `--body ""` vacío
```bash
tuku note create "una nota sin cuerpo" --body "" --vault mi-vault
```
Entonces se rechaza con código 1 indicando que falta el cuerpo
Y no se crea ningún archivo en `notas/`

## Escenario: si la constancia no cabe, no se escribe nada

Dado el vault con el ciclo del 10 al 16 de agosto abierto
Cuando se pide crear una nota con fecha fuera del ciclo
```bash
tuku note create "una nota de otro ciclo" --body "da igual" --day 2026-09-01 --vault mi-vault
```
Entonces la operación se rechaza con código 1 explicando el error
Y no se escribe ningún archivo huérfano en `notas/` (operación atómica)

## Aceptación humana (en Obsidian)

- Al leer la sección `## Ver además` de la nota en Obsidian, cada enlace saliente debe explicar en una frase para qué le sirve esa conexión al lector sin obligarlo a abrir el documento enlazado.
- El registro de constancia en la bitácora debe leerse como un hecho natural del autor y no como una traza técnica del sistema.
