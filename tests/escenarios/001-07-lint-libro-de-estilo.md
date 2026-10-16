# Escenario · 001-07-lint-libro-de-estilo

**Cubre:** epic 001, contratos de [`LIBRO-DE-ESTILO.md`](../../template/vanilla/LIBRO-DE-ESTILO.md) que los comandos de TUKU necesitan. Qué reporta el lint en cada caso lo prueban los unitarios de `tuku.style`; acá se prueba con qué código sale cada comando.

## Escenario: falta un encabezado de contrato

Dado un vault al que le falta `### Horizontes` en el libro de estilo

```bash
tuku init mi-vault --at 2026-08-11
grep -v '^### Horizontes$' mi-vault/LIBRO-DE-ESTILO.md > t && mv t mi-vault/LIBRO-DE-ESTILO.md
```

Cuando se corren el lint y un comando que necesita ese vocabulario

```bash
tuku style lint --vault mi-vault
tuku vocab show --vault mi-vault
```

Entonces el lint sale con código 1 y nombra el encabezado y la corrección
Y `tuku vocab show` sale con código 1 nombrando el encabezado que falta

## Escenario: tabla de vocabulario vacía

Dado un vault donde `### Clasificaciones` existe pero no declara ningún término

```bash
tuku init mi-vault --at 2026-08-11
grep -vE '^\| `(progreso|decisión|fricción|señal|nota)`' mi-vault/LIBRO-DE-ESTILO.md > libro.tmp
mv libro.tmp mi-vault/LIBRO-DE-ESTILO.md
```

Cuando se corre

```bash
tuku style lint --vault mi-vault
```

Entonces reporta una pregunta y sale con código 0: una pregunta informa, no rechaza

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_07
```

## Qué se mira a mano

- Leer la salida de `tuku style lint` con errores y verificar que cada mensaje diga el defecto y cómo corregirlo.
