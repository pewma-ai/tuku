# 002-08 · Creación de ámbito y retroactividad

> **Principio:** [P2 (organización emergente)](../../docs/principios.md#L17), [P7 (carpetas archivan, enlaces conectan)](../../docs/principios.md#L63) · **Brief:** [Frentes de actividad sin configuración previa](../../docs/brief.md#L19) · **Spec:** [`spec/ambitos.md`](../../spec/ambitos.md)

El autor no preconfigura frentes de vida: escribe de corrido y, cuando un ámbito cobra identidad, darlo de alta mediante `tuku scope create` genera la estructura de carpetas, enlaza retroactivamente menciones previas en `AHORA.md` y siembra las transclusiones a `PENDIENTES-AMBITOS.md`.

## Estado inicial

```bash
cp -r ../../002-06-fechar-pendiente/fechar-un-pendiente-en-dia/mi-vault .
```

## Escenario: crear un ámbito deja el árbol correcto

Dado un vault cuyo único ámbito es `personal` y con mención `del depto centro` en el martes 11
Cuando se crea el ámbito `depto-centro`
```bash
tuku scope create depto-centro --vault mi-vault
```
Entonces existe el directorio `ambitos/depto-centro/` con `AGENTS.md`, `CADENCIAS.md` y `depto-centro.md`
Y `depto-centro.md` transcluye a `![[../PENDIENTES-AMBITOS.md#^depto-centro]]`
Y la mención previa en `AHORA.md` pasa automáticamente a `[[depto-centro]]`
Y `ambitos/PENDIENTES-AMBITOS.md` añade el bloque `^depto-centro` con `SIN PENDIENTES`
Y `ambitos/personal/` permanece intacto

## Escenario: las menciones sueltas del ciclo en curso pasan a enlace

Dado el mismo estado con `del depto centro` escrito sin enlazar
Cuando se crea el ámbito `depto-centro`
```bash
tuku scope create depto-centro --vault mi-vault
```
Entonces solo esa mención pasa a ser `[[depto-centro]]` en `AHORA.md`
Y el resto de la línea y demás registros no sufren ninguna alteración

## Escenario: un registro no puede apuntar a una categoría

Dado el ámbito `depto-centro` creado y una subcarpeta `gastos/` sin página propia (categoría)
```bash
tuku scope create depto-centro --vault mi-vault
mkdir mi-vault/ambitos/depto-centro/gastos
touch mi-vault/ambitos/depto-centro/gastos/AGENTS.md mi-vault/ambitos/depto-centro/gastos/CADENCIAS.md
```
Cuando se escribe un registro apuntando a `[[gastos]]` y se valida
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 20:00 --scope gastos --body "**progreso**: revisé el detalle del mes"
tuku scope lint --vault mi-vault
```
Entonces `tuku scope lint` lo reporta con código 1 (`RECHAZO`), explicando que una categoría no recibe registros
Y el registro original permanece escrito en `AHORA.md` (un error del autor se informa, nunca se borra)

## Escenario: el ámbito recién creado deja el vault sano

Dado un vault limpio recién sembrado
```bash
tuku init vault-limpio --date 2026-08-11
```
Cuando se crea el ámbito `depto-centro`
```bash
tuku scope create depto-centro --vault vault-limpio
```
Entonces `tuku doctor` valida que el vault está 100% sano
```bash
tuku doctor --vault vault-limpio
```

## Escenario: crear dos veces el mismo ámbito no hace nada

Dado el ámbito ya creado
```bash
tuku scope create depto-centro --vault mi-vault
```
Cuando se vuelve a ejecutar `tuku scope create` sobre el mismo ámbito
```bash
tuku scope create depto-centro --vault mi-vault
```
Entonces el diff contra el estado previo es vacío (idempotente)
Y los enlaces existentes no se duplican

## Aceptación humana (en Obsidian)

- Al hacer clic en el enlace `[[depto-centro]]` desde `AHORA.md` en Obsidian, debe abrir directamente la página propia `depto-centro.md` y no una página en blanco ni un enlace roto.
- La página `depto-centro.md` debe mostrar la transclusión a su bloque de pendientes y la actividad resumida sin marcas artificiales.
