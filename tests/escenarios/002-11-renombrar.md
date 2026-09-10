# 002-11 · Renombrar entidades

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P7 (carpetas archivan, enlaces conectan)](../../docs/principios.md#L63) · **Brief:** [Soberanía de datos e integridad referencial](../../docs/brief.md#L43) · **Spec:** [`spec/ambitos.md`](../../spec/ambitos.md)

Corregir o renombrar entidades ya escritas no debe dejar cabos sueltos: los comandos `rename` (`scope rename`, `entry rename`) actualizan de forma atómica todas las referencias enlazadas y sincronizan las tablas derivadas sin dejar enlaces rotos en el grafo Markdown.

## Estado inicial

```bash
cp -r ../../002-09-crear-nota/la-nota-se-escribe-donde/mi-vault .
```

## Escenario: renombrar un ámbito arrastra todo lo que lo nombraba

Dado un vault con el ámbito `depto-centro` referenciado en `AHORA.md`, `PENDIENTES.md` y notas
Cuando el autor renombra el ámbito
```bash
cd mi-vault && tuku scope rename depto-centro depto-playa
```
Entonces el directorio y la página propia pasan a llamarse `depto-playa`
Y cada aparición de `[[depto-centro]]` y `^depto-centro` pasa a `[[depto-playa]]` y `^depto-playa`
Y `tuku scope lint` no detecta ningún enlace roto en el vault
```bash
cd mi-vault && tuku scope lint
```

## Escenario: renombrar sobre un nombre ocupado no toca nada

Dado un vault con dos ámbitos existentes
Cuando se intenta renombrar sobre un nombre que ya está en uso
```bash
cd mi-vault && tuku scope rename depto-centro personal
```
Entonces la operación se rechaza con código 1 (`RECHAZO`) explicando el conflicto
Y ningún archivo ni enlace del vault resulta modificado

## Escenario: corregir un registro corrige también su pendiente

Dado un registro con `**pendiente**` y su correspondiente fila en `PENDIENTES.md`
Cuando el autor corrige la redacción del hecho en la bitácora
```bash
cd mi-vault && tuku entry rename --day 2026-08-12 --hour 09:00 --body "**pendiente**: pagar la sesión de terapia"
```
Entonces el registro de las 09:00 en `AHORA.md` refleja el nuevo texto
Y la fila de `PENDIENTES.md` se actualiza de forma sincronizada carácter por carácter

## Aceptación humana (en Obsidian)

- Al abrir Obsidian tras renombrar un ámbito, el explorador de archivos y las transclusiones deben navegar con total fluidez sin mostrar notas rotas con signos de interrogación.
- La corrección de un registro de compromiso debe garantizar que el texto en la bitácora y en la tabla sea idéntico para que el posterior cierre literal funcione sin fricción.
