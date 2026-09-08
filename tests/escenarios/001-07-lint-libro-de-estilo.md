# Escenario · 001-07-lint-libro-de-estilo

**Cubre:** epic 001, contratos de [`LIBRO-DE-ESTILO.md`](../../template/vanilla/LIBRO-DE-ESTILO.md) requeridos por comandos de TUKU.

## Estado inicial

Un vault recién sembrado por `tuku init`.

## Escenario: el libro de estilo vanilla pasa el lint sin hallazgos

Dado un vault recién sembrado

```bash
tuku init mi-vault --date 2026-08-11
```

Cuando se corre

```bash
tuku style lint --vault mi-vault
```

Entonces sale con código 0 (éxito) y sin hallazgos

## Escenario: falta el marcador de autor

Dado un vault donde se eliminó la línea `**Nombre del autor:**` de `LIBRO-DE-ESTILO.md`

```bash
tuku init mi-vault --date 2026-08-11
grep -v '\*\*Nombre del autor:\*\*' mi-vault/LIBRO-DE-ESTILO.md > libro.tmp
mv libro.tmp mi-vault/LIBRO-DE-ESTILO.md
```

Cuando se corre

```bash
tuku style lint --vault mi-vault
```

Entonces reporta un error señalando que falta el marcador y la corrección
Y sembrar el nombre sobre ese vault se rechaza nombrando el mismo defecto

La segunda afirmación no tiene comando propio: `tuku init --author` sobre un vault existente exige `--force`, y `--force` recopia el template, con lo que el marcador volvería y el defecto desaparecería antes de probarse. El arnés ejerce esa ruta por dentro y así queda dicho, en vez de fingir un comando que no prueba lo que dice.

## Escenario: falta un encabezado de contrato

Dado tres vaults, a cada uno le falta uno de los encabezados de contrato

```bash
tuku init sin-clasificaciones --date 2026-08-11
tuku init sin-horizontes --date 2026-08-11
tuku init sin-tipos-de-nota --date 2026-08-11
grep -v '^### Clasificaciones$' sin-clasificaciones/LIBRO-DE-ESTILO.md > t && mv t sin-clasificaciones/LIBRO-DE-ESTILO.md
grep -v '^### Horizontes$' sin-horizontes/LIBRO-DE-ESTILO.md > t && mv t sin-horizontes/LIBRO-DE-ESTILO.md
grep -v '^### Tipos de nota$' sin-tipos-de-nota/LIBRO-DE-ESTILO.md > t && mv t sin-tipos-de-nota/LIBRO-DE-ESTILO.md
```

Cuando se corre, sobre cada uno, el lint y un comando que necesita ese vocabulario

```bash
tuku style lint --vault sin-clasificaciones
tuku style lint --vault sin-horizontes
tuku style lint --vault sin-tipos-de-nota
tuku vocab show --vault sin-clasificaciones
tuku vocab show --vault sin-horizontes
tuku vocab show --vault sin-tipos-de-nota
```

Entonces el lint reporta un error por el encabezado faltante, indicando defecto y corrección
Y `tuku vocab show` se rechaza con código 1 nombrando el encabezado que falta

## Escenario: tabla de vocabulario vacía

Dado un vault donde `### Clasificaciones` existe pero no declara ningún término

```bash
tuku init mi-vault --date 2026-08-11
grep -vE '^\| `(progreso|decisión|fricción|señal|nota)`' mi-vault/LIBRO-DE-ESTILO.md > libro.tmp
mv libro.tmp mi-vault/LIBRO-DE-ESTILO.md
```

Cuando se corre

```bash
tuku style lint --vault mi-vault
```

Entonces reporta una pregunta indicando que la tabla no tiene términos y cómo declararlos
Y sale con código 0: una pregunta informa, no rechaza

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_07
```

Cada caso deja sus vaults en su propia carpeta bajo `playground/001-07-lint-libro-de-estilo/`.

## Qué se mira a mano

- Leer la salida de `tuku style lint` cuando hay errores y verificar que cada mensaje indique con claridad el defecto y cómo corregirlo.
