# Escenario · 002-01-abrir-ciclo

**Cubre:** epic 002, apertura de ciclo desde plantilla en `reglas/plantilla/AHORA.md`.

## Estado inicial

Un vault recién sembrado por `tuku init`. Es el primer paso del epic, así que no hereda de nadie.

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
Y tiene `desde: 2026-08-10` y `hasta: 2026-08-16` (la semana completa que contiene el 11 de agosto)
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

## Por qué existe

`AHORA.md` no se genera por código rígido: se instancia a partir de la plantilla editable en `reglas/plantilla/AHORA.md`. Este escenario fija que `tuku cycle open` verifica la existencia de un ciclo activo para la fecha y lo crea con su semana completa si falta, sirviendo de base para los registros del día uno.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_01
```

Cada escenario deja su vault en `playground/002-01-abrir-ciclo/<escenario>/mi-vault/`. El del primero es el estado inicial del paso siguiente.

## Qué se mira a mano

- Abrir `AHORA.md` y verificar que contenga los 7 días de la semana (del lunes 10 al domingo 16), con fechas resueltas y formato canónico.
