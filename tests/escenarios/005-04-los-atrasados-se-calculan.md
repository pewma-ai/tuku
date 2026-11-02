# 005-04 · Los atrasados se calculan

> **Principio:** [P3 (el agente propone, el autor decide)](../../docs/principios.md#L25), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Brief:** [Tiempo × ámbito](../../docs/brief.md#L27) · **Spec:** capítulo Pendiente del [libro de estilo](../../template/vanilla/LIBRO-DE-ESTILO.md), [`spec/tuku.md`](../../spec/tuku.md)

Un pendiente atrasado se queda en su fila: se deduce de ella, y un comando lo dice. Con dos semanas de uso hay pendientes que vencieron mientras nadie miraba. Si tiene `Vence`, atrasado es que esa fecha pasó. Si tiene un horizonte, atrasado es que pasó su plazo contado desde `Creado`: 7 días `esta semana` y 14 `próxima semana`.

## Escenario: el comando dice qué venció y deja las filas donde están

Dado el vault de Andrea, y el lunes 24 como HOY
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/el-lunes-24-la-primera-semana/mi-vault .
```
Cuando se revisan los pendientes ese día
```bash
cd mi-vault
TUKU_NOW="2026-08-24 09:00" tuku context todo --late
```
Entonces la salida nombra como atrasado `cerrar la cotización de Colegio Los Robles durante la semana del 17 de agosto`: `esta semana` desde el domingo 16, vencido el domingo 23
Y los pendientes vigentes quedan fuera de la lista
Y `PENDIENTES.md` y `AHORA.md` quedan intactos, y `AHORA.md` ya marca el atrasado en su ventana de pendientes

## Escenario: un plazo que vence hoy todavía no está atrasado

Dado el mismo vault, con un pendiente que vence el lunes 24
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/el-lunes-24-la-primera-semana/mi-vault .
cd mi-vault
export TUKU_NOW="2026-08-24 09:00"
tuku todo open --at "2026-08-23 21:30" --scope bodega --due 2026-08-24 --body "recibir el pedido de cartulina de color"
```
Cuando se revisan los pendientes el mismo lunes 24
```bash
TUKU_NOW="2026-08-24 09:00" tuku context todo --late
```
Entonces la salida deja fuera `recibir el pedido de cartulina de color`
Y sí lo nombra el martes 25, porque «vence el día en que toca el pendiente y desde el siguiente está atrasado»
```bash
TUKU_NOW="2026-08-25 09:00" tuku context todo --late
```
Y `ofrecer reposición a Librería El Compás`, `esta semana` desde el martes 18, vence el martes 25: queda fuera ese día y entra el miércoles 26
```bash
TUKU_NOW="2026-08-26 09:00" tuku context todo --late
```

## Aceptación humana

- La línea de un atrasado dice qué venció, cuándo y de qué ámbito, y se entiende sin abrir `PENDIENTES.md`.
