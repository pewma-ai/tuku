# Escenario · 002-09-crear-nota

**Cubre:** epic 002, punto 5, fase 5 en su **versión mínima**: crear una nota a petición y enlazarla. Notas tipadas con plantilla y destilado del histórico no entran.

## Estado inicial

El que dejó [`002-08-crear-ambito`](002-08-crear-ambito.md): existe el ámbito `depto-centro` y `notas/` está vacío. El cuerpo de la nota es salida de agente y viene congelado como fixture, porque no hay un original vivo contra el cual compararlo.

```bash
cp -r ../../002-08-crear-ambito/crear-un-ambito-deja-el-arbol/mi-vault .
cp ../../../tests/escenarios/fixtures/002-09-crear-nota/cuerpo-nota.md .
```

## La consecuencia "nota" todavía no está en la spec

La tabla de consecuencias de [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md) tiene pendientes, enlaces, cadencias y propuesta. La nota no está y el punto 5 la exige. Como la spec declara la lista abierta y agregar una consecuencia es agregar un archivo en `reglas/`, este escenario obliga a escribir `reglas/notas.tuku.md` y la fila que falta. Es lo primero que el epic 002 mueve en el diseño, previsto en `epics.md` antes de empezar.

## Escenario: la nota se escribe donde corresponde

Dado el ámbito `depto-centro` ya creado
Cuando el autor pide *"una nota respecto al depto centro: cómo funciona el cobro de gastos comunes en una copropiedad"*

```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```

Entonces existe `notas/gastos-comunes-en-copropiedad.md`
Y su frontmatter trae `type: Note` y `created` con la fecha de hoy
Y el cuerpo es el que el agente redactó, tomado del fixture congelado

## Escenario: queda constancia en la bitácora

Dado el mismo estado
Cuando la nota se escribe

```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```

Entonces hay un registro nuevo en el martes 11 que deja constancia de la nota creada
Y ese registro enlaza a la nota
Y no hay ningún otro registro narrando el mecanismo

Crear la nota es un hecho de la vida del autor, que la pidió; mover un pendiente de escalón es del sistema. Por eso esta se registra y aquella no.

## Escenario: la nota queda enlazada a su ámbito, porque se pidió así

Dado que la petición dijo *"respecto al depto centro"*
Cuando la nota se escribe

```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```

Entonces la nota enlaza al ámbito `depto-centro`
Y el enlace resuelve a una página que existe
Y la constancia se propaga a `ambitos/depto-centro/depto-centro.md` bajo `## Esta semana` sin hora junto al registro previo

Si la petición no hubiera nombrado un ámbito, la nota quedaría suelta y eso sería correcto.

## Escenario: "Ver además" existe y cada enlace lleva motivo

Dado la nota ya escrita

```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```

Cuando se revisa

```bash
tuku note lint mi-vault/notas/como-funciona-el-cobro-de-gastos-comunes-en-una-copropiedad.md
```

Entonces la nota tiene una sección `## Ver además`
Y cada enlace de esa sección va seguido de texto de motivo
Y el lint no falla

La **presencia** de la sección y del motivo se verifica sin juicio. Que el motivo sea pertinente y no relleno lo evalúa quien lee, y está más abajo ([`spec/notas.md`](../../spec/notas.md)).

## Escenario: crear la nota dos veces no duplica nada

Dado la nota ya creada

```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```

Cuando se repite la operación

```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault mi-vault
```

Entonces el diff es vacío
Y no hay un segundo registro de constancia en la bitácora

## Escenario: la nota recién creada deja el vault sano

Este parte de un vault recién sembrado y no del que viene rodando por la cadena: el `002-03` dejó ahí a propósito un registro con `**Pendiente**` mal escrito, y el `doctor` lo reporta con razón. Lo que se afirma acá es lo otro, que TUKU no se reporta a sí mismo.

Dado un vault recién sembrado con su ámbito

```bash
tuku init vault-limpio --date 2026-08-11
tuku scope create depto-centro --vault vault-limpio
```

Cuando se escribe la nota

```bash
tuku note create "cómo funciona el cobro de gastos comunes en una copropiedad" --body-file cuerpo-nota.md --scope depto-centro --day 2026-08-11 --hour 21:15 --vault vault-limpio
```

Entonces `tuku doctor` dice que el vault está sano

```bash
tuku doctor --vault vault-limpio
```

Una nota es un archivo que guarda conocimiento, así que declara `type: Note` como cualquier otro ([`spec/README.md`](../../spec/README.md)). El `subtype` de las notas tipadas es otra clave, de lista abierta, y no la escribe este comando.

## Escenario: el lint reporta un enlace sin motivo y una sección que falta

Dado dos notas escritas a mano, una sin motivo en su enlace y otra sin la sección

```bash
printf '# Nota\n\ncuerpo\n\n## Ver además\n\n* [[depto-centro]]\n' > sin-motivo.md
printf '# Nota\n\ncuerpo\n' > sin-seccion.md
```

Cuando se revisan

```bash
tuku note lint sin-motivo.md
tuku note lint sin-seccion.md
```

Entonces cada una se rechaza nombrando su defecto: el enlace que no dice para qué conecta, y la sección que falta

Es el reverso del escenario anterior: allá se afirma que la nota bien escrita pasa, acá que las dos formas de escribirla mal se reportan.

## De dónde sale el contenido

Del fixture `fixtures/002-09-crear-nota/`: el texto de la nota es salida de agente y se congela, porque no hay un original vivo contra el cual compararlo. Todo lo que este escenario prueba (dónde queda el archivo, la constancia, el enlace, el lint) es determinista.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_09
```

Cada escenario deja su vault en `playground/002-09-crear-nota/<escenario>/mi-vault/`.

## Qué se mira a mano

- **Leer el motivo del "Ver además".** Ningún script lo juzga: si no responde para qué le sirve al lector hacer clic, está de relleno.
- Que el registro de constancia en la bitácora se lea como un hecho del día y no como un log de sistema.
- Que la nota se sostenga sola dentro de un año, sin la conversación que la pidió.
