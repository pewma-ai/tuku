# 002-04 · Apertura de compromisos

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Triangulación tiempo × compromiso](../../docs/brief.md#L27) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md), [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md)

La captura de un compromiso no requiere abrir y editar tablas de tareas: registrar un hecho con `**pendiente**` abre el ítem en `PENDIENTES.md` de forma atómica e idempotente, copiando el cuerpo literal y propagando las vistas derivadas.

## Estado inicial

```bash
cp -r ../../002-02-registro-en-su-dia/tres-registros-caen-en-el-dia/mi-vault .
```

## Escenario: el registro abre el pendiente y copia el cuerpo literal

Dado el vault con los tres registros del martes 11 y `PENDIENTES.md` vacío
Cuando se registra un compromiso en el día de hoy
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "**pendiente**: avisar de los GGCC a la administradora"
```
Entonces la fila entra en `PENDIENTES.md` bajo `esta semana`:
`| esta semana |  | [[personal]] | avisar de los GGCC a la administradora |`
Y el registro queda escrito bajo `## Martes 11 de agosto` en `AHORA.md`
Y la vista de ámbito `ambitos/personal/personal.md` recibe la actividad propagada
Y `tuku doctor` valida que no quedan consecuencias pendientes

## Escenario: abrir dos veces no duplica

Dado el pendiente ya abierto en `esta semana`
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "**pendiente**: avisar de los GGCC a la administradora"
```
Cuando se corre el mismo comando una segunda vez
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "**pendiente**: avisar de los GGCC a la administradora"
```
Entonces el diff contra el estado previo es vacío
Y hay exactamente una fila en `PENDIENTES.md` con ese detalle

## Escenario: comando directo tuku todo open abre el pendiente y estampa huella en AHORA.md

Dado el vault con los tres registros del martes 11 y `PENDIENTES.md` vacío
Cuando se abre un compromiso directamente con el comando todo open
```bash
TUKU_NOW="2026-08-11 15:30" tuku todo open --vault mi-vault --scope personal --body "comprar filtro de cafe"
```
Entonces la fila entra en `PENDIENTES.md` bajo `esta semana`:
`| esta semana |  | [[personal]] | comprar filtro de cafe |`
Y estampa la constancia en `AHORA.md` bajo `## Martes 11 de agosto`:
`- 15:30 - [[personal]] **pendiente**: comprar filtro de cafe`
Y una segunda ejecución directa es idempotente sin duplicar en la bitácora ni en la tabla
```bash
TUKU_NOW="2026-08-11 15:30" tuku todo open --vault mi-vault --scope personal --body "comprar filtro de cafe"
```

## Aceptación humana (en Obsidian)

- Al leer `PENDIENTES.md`, la tabla debe mostrar el compromiso recién nacido en `esta semana` sin fecha explícita, indicando que pertenece al ciclo en curso.
- En `AHORA.md`, el registro debe leerse limpio como cualquier otro hecho cronológico del día.
