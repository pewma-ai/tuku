# 002-01 · Apertura de ciclo

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [El ciclo semanal y plantillas](../../docs/brief.md#L44) · **Spec:** [`spec/ciclo.md`](../../spec/ciclo.md)

`AHORA.md` no se genera por código rígido: se instancia desde la plantilla editable en `reglas/plantilla/AHORA.md`. `tuku cycle open` verifica la existencia de un ciclo activo para la fecha y lo crea con su semana completa de lunes a domingo.

## Estado inicial

```bash
tuku init mi-vault --date 2026-08-11
```

## Escenario: crear AHORA.md a partir de la plantilla cuando no existe

Dado un vault sin `AHORA.md` abierto
```bash
rm mi-vault/AHORA.md
```
Cuando se corre
```bash
tuku cycle open --vault mi-vault --fecha 2026-08-11
```
Entonces nace `AHORA.md` a partir de `reglas/plantilla/AHORA.md`
Y tiene `from: 2026-08-10` y `to: 2026-08-16` (la semana completa que contiene el 11 de agosto)
Y contiene todos los días de la semana, desde `## Lunes 10 de agosto` hasta `## Domingo 16 de agosto`
Y ningún placeholder (`AAAA-MM-DD`, `DD de mes`) sobrevive fuera de bloques de código

## Escenario: verificar AHORA.md existente sin modificarlo (idempotencia)

Dado el vault con `AHORA.md` abierto que cubre la fecha deseada
```bash
rm mi-vault/AHORA.md
tuku cycle open --vault mi-vault --fecha 2026-08-11
```
Cuando se corre de nuevo
```bash
tuku cycle open --vault mi-vault --fecha 2026-08-11
```
Entonces el comando informa que ya cubre la fecha
Y el diff contra el estado anterior es vacío

## Aceptación humana (en Obsidian)

- Al abrir `AHORA.md` en Obsidian, debe mostrar los 7 días de la semana (del lunes 10 al domingo 16) limpios, con fechas resueltas y formato canónico, sin ningún placeholder visible.
