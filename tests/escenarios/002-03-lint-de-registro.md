# 002-03 · Validación ontológica

> **Principio:** [P2 (organización emergente)](../../docs/principios.md#L17), [P4 (determinismo)](../../docs/principios.md#L33), [P5 (reglas en prosa)](../../docs/principios.md#L47) · **Brief:** [Ontologías y lenguaje del autor](../../docs/brief.md#L23) · **Spec:** [`spec/bitacora.md`](../../spec/bitacora.md)

`tuku entry lint` verifica la integridad de las marcas en la bitácora: la ontología cerrada (`**pendiente**`, `~~(Hecho)~~`, `**cadencia**`) es estricta y rechaza errores de tipeo; la ontología abierta es libre y permisiva para que el vocabulario propio emerja sin trabas. Los linters informan y jamás modifican el vault.

## Estado inicial

```bash
cp -r ../../002-02-registro-en-su-dia/tres-registros-caen-en-el-dia/mi-vault .
```

## Escenario: un tipo abierto desconocido se reporta y se acepta

Dado el vault con los registros del martes 11
Cuando se escribe un tipo abierto no declarado y se valida
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 12:05 --scope personal --body "**cachureo**: ordené los cables del escritorio"
tuku entry lint --vault mi-vault
```
Entonces el registro queda escrito en su día
Y el lint lo reporta como tipo desconocido para orientar al autor
Y el comando finaliza con código 0 (`EXITO`) sin rechazar

## Escenario: la ontología cerrada se valida estricta

Dado el mismo estado inicial
Cuando se escribe una marca cerrada mal escrita y se valida
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 13:00 --scope personal --body "**Cadencia**: comprar una maleta"
tuku entry lint --vault mi-vault
```
Entonces el lint lo reporta como error formal de ontología cerrada con código 1 (`RECHAZO`)
Y no se abre ningún compromiso derivado en `PENDIENTES.md`
Y la línea original permanece intacta en `AHORA.md` (no se censura la voz del autor)

## Escenario: un registro fuera del rango del ciclo se reporta

Dado el vault con el ciclo abierto del 10 al 16 de agosto
Cuando se agrega a mano un día fuera de ese rango y se valida
```bash
printf '\n## Martes 25 de agosto\n\n- 08:00 - [[personal]] **progreso**: revisé la bodega\n' >> mi-vault/AHORA.md
tuku entry lint --vault mi-vault
```
Entonces el lint reporta el día fuera del ciclo abierto y no inventa días intermedios

## Escenario: el lint no escribe en el vault

Dado el mismo estado inicial
Cuando se corre `tuku entry lint` dos veces consecutivas
```bash
tuku entry lint --vault mi-vault
tuku entry lint --vault mi-vault
```
Entonces el diff contra el estado previo es vacío en ambas corridas
Y el reporte de salida es idéntico

## Aceptación humana (en Obsidian)

- Al leer el reporte en la terminal, debe distinguirse de inmediato qué hallazgo requiere corrección urgente (marca cerrada) y cuál es solo una consulta sobre vocabulario nuevo del autor.
- El aviso de tipo desconocido no debe sonar punitivo, sino receptivo a términos propios del autor.
