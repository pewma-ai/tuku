# 002-06 · Fechado automático en día futuro

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P6 (tres ejes sin registro paralelo)](../../docs/principios.md#L55) · **Brief:** [Lo que entró vuelve solo cuando corresponde](../../docs/brief.md#L13) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md) · **Origen:** [Lección 7 de `mac-jpgil`](../../devel/lecciones-macjpgil.md) (tareas duplicadas entre horizontes)

Agendar un compromiso debe ser tan simple como anotarlo en el día futuro de la agenda: escribir un registro `**pendiente**` bajo un día posterior a hoy lo fecha automáticamente en `PENDIENTES.md` (`con fecha`), propagándolo a la región del día correspondiente de `AHORA.md` sin requerir comandos adicionales de agendamiento.

## Estado inicial

```bash
cp -r ../../002-05-cerrar-pendiente/el-cierre-repite-el-texto-y/mi-vault .
```

## Escenario: escribir un pendiente en un día futuro lo fecha

Dado el ciclo abierto del 10 al 16 de agosto con HOY en martes 11 y tabla de pendientes vacía
Cuando se escribe un pendiente bajo el miércoles 12
```bash
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --horizon "con fecha" --when 2026-08-12 --body "**pendiente**: pagar la sesión con el psicólogo"
```
Entonces la tabla de `PENDIENTES.md` gana una fila con `con fecha` y `2026-08-12`:
`| con fecha | 2026-08-12 | [[personal]] | pagar la sesión con el psicólogo |`
Y el miércoles 12 de `AHORA.md` recibe por propagación el callout:
```markdown
> [!todo] Pendientes del día
> - [[personal]] - pagar la sesión con el psicólogo
```
Y el pendiente no aparece en `esta semana` ni en horizontes postergados

## Escenario: fechar mueve, nunca copia

Dado el mismo estado inicial
Cuando se registra el pendiente fechado
```bash
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --horizon "con fecha" --when 2026-08-12 --body "**pendiente**: pagar la sesión con el psicólogo"
```
Entonces el pendiente existe en exactamente una fila de `PENDIENTES.md`
Y `tuku todo lint` no encuentra ninguna aparición duplicada

## Escenario: la fecha vive en la columna Cuándo

Dado que la tabla no tenía pendientes con fecha antes
Cuando nace el compromiso fechado
```bash
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --horizon "con fecha" --when 2026-08-12 --body "**pendiente**: pagar la sesión con el psicólogo"
```
Entonces entra como fila con columna `Cuándo` = `2026-08-12` y horizonte `con fecha`
Y no se crean callouts ni encabezados dentro de `PENDIENTES.md`

## Escenario: el movimiento de escalón no se registra en la bitácora

Dado el ciclo abierto antes de agendar
Cuando se agenda el pendiente
```bash
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --horizon "con fecha" --when 2026-08-12 --body "**pendiente**: pagar la sesión con el psicólogo"
```
Entonces la única línea de registro nueva es el compromiso que el autor escribió
Y no se insertan mensajes de auditoría o log del sistema narrando que el ítem cambió de estado

## Escenario: inyectar dos veces no duplica la fila ni la propagación

Dado el pendiente ya fechado y propagado
```bash
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --horizon "con fecha" --when 2026-08-12 --body "**pendiente**: pagar la sesión con el psicólogo"
```
Cuando se corre el mismo comando otra vez
```bash
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --horizon "con fecha" --when 2026-08-12 --body "**pendiente**: pagar la sesión con el psicólogo"
```
Entonces el diff contra el estado previo es vacío (idempotente)
Y permanece una sola fila en `PENDIENTES.md` y una sola línea propagada en el miércoles

## Aceptación humana (en Obsidian)

- Al abrir `AHORA.md` en Obsidian, el miércoles 12 debe mostrar el callout de pendientes arriba del todo, de modo que el autor vea lo comprometido para ese día al iniciar su jornada.
- Fechar debe sentirse tan natural como escribir en una agenda de papel, sin tener que gestionar manualmente estructuras ni identificadores.
