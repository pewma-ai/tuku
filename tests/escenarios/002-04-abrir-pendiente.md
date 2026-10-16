# 002-04 · Apertura de compromisos

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Triangulación tiempo × compromiso](../../docs/brief.md#L27) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md), [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md)

Un compromiso se abre con `tuku todo open`: escribe el registro `**pendiente**` en `AHORA.md`, inserta la fila en `PENDIENTES.md` y propaga las vistas derivadas. `tuku entry add` rechaza la marca `**pendiente**` y nombra este comando.

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
`| esta semana |  | [personal](ambitos/personal/personal.md) | avisar de los GGCC a la administradora |`
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

## Escenario: todo lint encuentra la fila que se borró a mano

Dado un pendiente abierto con su comando
```bash
tuku todo open --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "avisar de los GGCC a la administradora"
```
Cuando el autor borra a mano su fila de `PENDIENTES.md` y se revisa
```bash
sed -i.bak '/avisar de los GGCC a la administradora/d' mi-vault/PENDIENTES.md
tuku todo lint --vault mi-vault
```
Entonces `tuku todo lint` sale con código 1 (`RECHAZO`)
Y nombra como corrección el comando original, `tuku todo open`

## Escenario: todo lint encuentra una vista desactualizada

Dado un pendiente abierto con su comando
```bash
tuku todo open --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "avisar de los GGCC a la administradora"
```
Cuando el autor borra a mano el pendiente del callout de `ambitos/PENDIENTES-AMBITOS.md` y se revisa
```bash
sed -i.bak '/avisar de los GGCC a la administradora/d' mi-vault/ambitos/PENDIENTES-AMBITOS.md
tuku todo lint --vault mi-vault
```
Entonces `tuku todo lint` sale con código 1 (`RECHAZO`) y nombra `tuku regenerate todo` como corrección
Y después de propagar, `tuku todo lint` sale limpio
```bash
tuku regenerate todo --vault mi-vault
tuku todo lint --vault mi-vault
```

## Aceptación humana (en Obsidian)

- Al leer `PENDIENTES.md`, la tabla debe mostrar el compromiso recién nacido en `esta semana` sin fecha explícita, indicando que pertenece al ciclo en curso.
- En `AHORA.md`, el registro debe leerse limpio como cualquier otro hecho cronológico del día.
