# 002-04 · Apertura de compromisos

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Triangulación tiempo × compromiso](../../docs/brief.md#L27) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md), [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md)

La captura de un compromiso opera primordialmente mediante el comando directo `tuku todo open`: inserta la fila en `PENDIENTES.md`, estampa su constancia cronológica en `AHORA.md` y propaga las vistas derivadas de forma atómica e idempotente. La vía bitácora (`tuku entry add`) aplica esta misma consecuencia en automático ante la marca `**pendiente**`.

## Estado inicial

```bash
cp -r ../../002-02-registro-en-su-dia/tres-registros-caen-en-el-dia/mi-vault .
```

## Escenario: abrir el pendiente copia el cuerpo literal en esta semana

Dado el vault con los tres registros del martes 11 y `PENDIENTES.md` vacío
Cuando se abre un compromiso directamente con el comando todo open
```bash
tuku todo open --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "avisar de los GGCC a la administradora"
```
Entonces la fila entra en `PENDIENTES.md` bajo `esta semana`:
`| esta semana |  | [[personal]] | avisar de los GGCC a la administradora |`
Y estampa la constancia en `AHORA.md` bajo `## Martes 11 de agosto`
Y la vista de ámbito `ambitos/personal/personal.md` recibe la actividad propagada
Y `tuku doctor` valida que no quedan consecuencias pendientes

## Escenario: abrir dos veces no duplica

Dado el pendiente ya abierto en `esta semana` con todo open
```bash
tuku todo open --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "avisar de los GGCC a la administradora"
```
Cuando se corre el mismo comando una segunda vez
```bash
tuku todo open --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "avisar de los GGCC a la administradora"
```
Entonces el diff contra el estado previo es vacío
Y hay exactamente una fila en `PENDIENTES.md` con ese detalle

## Escenario: la vía bitácora tuku entry add abre el pendiente en automático

Dado el vault con los tres registros del martes 11 y `PENDIENTES.md` vacío
Cuando se registra un hecho con `**pendiente**` en la bitácora
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 16:00 --scope personal --body "**pendiente**: comprar café tostado"
```
Entonces la fila entra en `PENDIENTES.md` bajo `esta semana`:
`| esta semana |  | [[personal]] | comprar café tostado |`
Y el registro queda escrito bajo `## Martes 11 de agosto` en `AHORA.md`
Y `tuku doctor` valida que no quedan consecuencias pendientes

## Aceptación humana (en Obsidian)

- Al leer `PENDIENTES.md`, la tabla debe mostrar el compromiso recién nacido en `esta semana` sin fecha explícita, indicando que pertenece al ciclo en curso.
- En `AHORA.md`, el registro debe leerse limpio como cualquier otro hecho cronológico del día.
