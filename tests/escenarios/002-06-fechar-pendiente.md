# 002-06 · Fechado de compromisos

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P6 (tres ejes sin registro paralelo)](../../docs/principios.md#L55) · **Brief:** [Lo que entró vuelve solo cuando corresponde](../../docs/brief.md#L13) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md) · **Origen:** [Lección 7 de `mac-jpgil`](../../devel/lecciones-macjpgil.md) (tareas duplicadas entre horizontes)

Un compromiso se agenda con `tuku todo open`: una fecha en `--when`, o un `--day` posterior a hoy, le asigna el horizonte `con fecha` en `PENDIENTES.md`, escribe el registro en `AHORA.md` y propaga el callout de pendientes bajo ese día.

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
`| con fecha | 2026-08-12 | [personal](ambitos/personal/personal.md) | pagar la sesión con el psicólogo |`
Y el miércoles 12 de `AHORA.md` recibe por propagación el callout:
```markdown
> [!todo] Pendientes del día
> - [personal](ambitos/personal/personal.md) - pagar la sesión con el psicólogo
```
Y el pendiente no aparece en `esta semana` ni en horizontes postergados
Y la fecha vive solo en la columna `Cuándo`: `PENDIENTES.md` no gana callouts, anclas ni encabezados

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

## Escenario: pendientes de dos días futuros, dos por día

Dado el vault con el ciclo abierto, y hoy martes 11
Cuando se abren cuatro pendientes bajo el miércoles 12 y el jueves 13, sin `--when` y en desorden
```bash
TUKU_NOW="2026-08-11 10:00" tuku todo open --vault mi-vault --day 2026-08-13 --hour 10:00 --scope personal --body "comprar pasajes de tren"
TUKU_NOW="2026-08-11 10:00" tuku todo open --vault mi-vault --day 2026-08-12 --hour 10:05 --scope personal --body "pagar la sesión con el psicólogo"
TUKU_NOW="2026-08-11 10:00" tuku todo open --vault mi-vault --day 2026-08-13 --hour 10:10 --scope personal --body "retirar el pase escolar"
TUKU_NOW="2026-08-11 10:00" tuku todo open --vault mi-vault --day 2026-08-12 --hour 10:15 --scope personal --body "llamar a la administradora"
```
Entonces cada uno queda en `PENDIENTES.md` con `con fecha` y el día bajo el que se escribió
Y cada día de `AHORA.md` recibe sus dos pendientes en su callout:
```markdown
## Miércoles 12 de agosto
> [!todo] Pendientes del día
> - [personal](ambitos/personal/personal.md) - pagar la sesión con el psicólogo
> - [personal](ambitos/personal/personal.md) - llamar a la administradora
```
Y el callout de `personal` en `ambitos/PENDIENTES-AMBITOS.md` los lista por fecha, cada uno con su día y sin el ámbito:
```markdown
> [!todo] Pendientes en **Personal** ^personal
> - Miércoles 12 de agosto - pagar la sesión con el psicólogo
> - Miércoles 12 de agosto - llamar a la administradora
> - Jueves 13 de agosto - comprar pasajes de tren
> - Jueves 13 de agosto - retirar el pase escolar
```
Y `tuku todo lint` sale limpio
```bash
tuku todo lint --vault mi-vault
```

## Aceptación humana (en Obsidian)

- Al abrir `AHORA.md` en Obsidian, el miércoles 12 debe mostrar el callout de pendientes del día arriba del todo, visible antes del primer registro cronológico.
- La columna `Cuándo` en `PENDIENTES.md` debe contener la fecha limpia y sin metadatos intrusivos.
