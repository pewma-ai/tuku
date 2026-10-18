# 005-04 · Los atrasados se calculan

> **Principio:** [P3 (el agente propone, el autor decide)](../../docs/principios.md#L25), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Brief:** [Tiempo × ámbito](../../docs/brief.md#L27) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md), [`spec/cli.md`](../../spec/cli.md)

Un pendiente atrasado se queda en su fila: se deduce de ella, y un comando lo dice. Con dos semanas de uso hay pendientes que vencieron mientras nadie miraba, y la promesa del producto es que abrir el ciclo muestre lo olvidado.

## Escenario: el comando dice qué venció y deja las filas donde están

Dado el vault de la segunda semana de Andrea, y el lunes 24 como HOY
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
```
Cuando se revisan los pendientes ese día
```bash
cd mi-vault
TUKU_NOW="2026-08-24 09:00" tuku todo lint
```
Entonces la salida nombra como atrasado `revisar la bitácora anterior`, que venció el lunes 17
Y los pendientes vigentes quedan fuera de la lista
Y `PENDIENTES.md` y `AHORA.md` quedan intactos

## Escenario: un pendiente que vence hoy todavía no está atrasado

Dado el mismo vault, con un pendiente que vence el lunes 24
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
cd mi-vault
tuku todo open --at "2026-08-23 21:30" --scope bodega --due 2026-08-24 --body "recibir el pedido de cartulina de color"
```
Cuando se revisan los pendientes el mismo lunes 24
```bash
TUKU_NOW="2026-08-24 09:00" tuku todo lint
```
Entonces la salida deja fuera `recibir el pedido de cartulina de color`
Y sí lo nombra el martes 25, porque «vence el día en que toca el pendiente y desde el siguiente está atrasado»
```bash
TUKU_NOW="2026-08-25 09:00" tuku todo lint
```

## Qué se mira a mano

- Qué comando debería informar los atrasados: hoy `tuku todo lint` revisa la coherencia entre la tabla y los registros y no sabe de fechas, y la spec dice solo que «un comando lo informa». Este escenario lo pide a `todo lint` como aviso con código 0; si el autor prefiere un comando propio, se cambia aquí y en `spec/pendientes.md`.

## Aceptación humana

- La línea de un atrasado dice qué venció, cuándo y de qué ámbito, y se entiende sin abrir `PENDIENTES.md`.
