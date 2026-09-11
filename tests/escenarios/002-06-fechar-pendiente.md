# 002-06 · Fechado de compromisos

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P6 (tres ejes sin registro paralelo)](../../docs/principios.md#L55) · **Brief:** [Lo que entró vuelve solo cuando corresponde](../../docs/brief.md#L13) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md) · **Origen:** [Lección 7 de `mac-jpgil`](../../devel/lecciones-macjpgil.md) (tareas duplicadas entre horizontes)

Agendar un compromiso opera directamente con el comando `tuku todo open`: pasar una fecha en `--when` asigna automáticamente el horizonte `con fecha` en `PENDIENTES.md`, estampa la constancia cronológica en `AHORA.md` y propaga el callout de pendientes del día bajo la fecha indicada. La vía bitácora (`tuku entry add`) replica esta consecuencia en automático.

## Estado inicial

```bash
cp -r ../../002-05-cerrar-pendiente/el-cierre-repite-el-texto-y/mi-vault .
```

## Escenario: fechar un pendiente en dia futuro

Dado el ciclo abierto del 10 al 16 de agosto con HOY en martes 11 y tabla de pendientes vacía
Cuando se abre un pendiente fechado con todo open
```bash
tuku todo open --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --when 2026-08-12 --body "pagar la sesión con el psicólogo"
```
Entonces la tabla de `PENDIENTES.md` gana una fila con `con fecha` y `2026-08-12`:
`| con fecha | 2026-08-12 | [[personal]] | pagar la sesión con el psicólogo |`
Y el miércoles 12 de `AHORA.md` recibe por propagación el callout:
```markdown
> [!todo] Pendientes del día
> - [[personal]] - pagar la sesión con el psicólogo
```
Y el pendiente no aparece en `esta semana` ni en horizontes postergados

## Escenario: la fecha vive en la columna Cuándo y en ningún otro lugar

Dado que la tabla no tenía pendientes con fecha antes
Cuando nace el compromiso fechado con todo open
```bash
tuku todo open --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --when 2026-08-12 --body "pagar la sesión con el psicólogo"
```
Entonces entra como fila con columna `Cuándo` = `2026-08-12` y horizonte `con fecha`
Y no se crean callouts ni encabezados dentro de `PENDIENTES.md`

## Escenario: fechar dos veces no duplica la fila ni la propagación

Dado el pendiente ya fechado y propagado con todo open
```bash
tuku todo open --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --when 2026-08-12 --body "pagar la sesión con el psicólogo"
```
Cuando se corre el mismo comando otra vez
```bash
tuku todo open --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --when 2026-08-12 --body "pagar la sesión con el psicólogo"
```
Entonces el diff contra el estado previo es vacío (idempotente)
Y permanece una sola fila en `PENDIENTES.md` y una sola línea propagada en el miércoles

## Escenario: la vía bitácora tuku entry add fecha el pendiente en automático

Dado el vault con el ciclo abierto
Cuando se escribe un pendiente bajo el día futuro en la bitácora
```bash
tuku entry add --vault mi-vault --day 2026-08-13 --hour 10:00 --scope personal --when 2026-08-13 --body "**pendiente**: comprar pasajes de tren"
```
Entonces la tabla de `PENDIENTES.md` gana una fila con `con fecha` y `2026-08-13`:
`| con fecha | 2026-08-13 | [[personal]] | comprar pasajes de tren |`
Y el jueves 13 de `AHORA.md` recibe por propagación el callout de pendientes del día
Y `tuku doctor` valida que no quedan consecuencias pendientes

## Aceptación humana (en Obsidian)

- Al abrir `AHORA.md` en Obsidian, el miércoles 12 debe mostrar el callout de pendientes del día arriba del todo, visible antes del primer registro cronológico.
- La columna `Cuándo` en `PENDIENTES.md` debe contener la fecha limpia y sin metadatos intrusivos.
