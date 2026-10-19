# Escenario · 001-07-lint-libro-de-estilo

**Cubre:** epic 001, contratos del libro de estilo y de los archivos del autor en [`reglas/`](../../template/vanilla/reglas/) que los comandos de TUKU necesitan: un capítulo `##` por vocabulario y una sola tabla por capítulo. Qué reporta el lint en cada caso lo prueban los unitarios de `tuku.style`; acá se prueba con qué código sale cada comando.

## Escenario: falta un capítulo de contrato

Dado un vault al que le falta `## Horizontes` en `reglas/pendientes.md`

```bash
tuku init mi-vault --at 2026-08-11
grep -v '^## Horizontes$' mi-vault/reglas/pendientes.md > t && mv t mi-vault/reglas/pendientes.md
```

Cuando se corren el lint y un comando que necesita ese vocabulario

```bash
tuku doctor style --vault mi-vault
tuku context style --vault mi-vault
```

Entonces el lint sale con código 1 y nombra el capítulo, el archivo y la corrección
Y `tuku context style` sale con código 1 nombrando el capítulo que falta

## Escenario: tabla de vocabulario vacía

Dado un vault donde `## Clasificaciones` existe pero no declara ningún término

```bash
tuku init mi-vault --at 2026-08-11
grep -vE '^\| `(progreso|decisión|fricción|señal|nota)`' mi-vault/reglas/bitacora.md > t && mv t mi-vault/reglas/bitacora.md
```

Cuando se corre

```bash
tuku doctor style --vault mi-vault
```

Entonces reporta una pregunta y sale con código 0: una pregunta informa, no rechaza

## Escenario: un capítulo con dos tablas

Dado un vault donde `## Horizontes` lleva una segunda tabla

```bash
tuku init mi-vault --at 2026-08-11
printf '\nOtra tabla:\n\n| A |\n| --- |\n| x |\n' >> mi-vault/reglas/pendientes.md
```

Cuando se corre

```bash
tuku doctor style --vault mi-vault
```

Entonces el lint sale con código 1 y dice que el capítulo tiene 2 tablas y cómo corregirlo

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_07
```

## Qué se mira a mano

- Leer la salida de `tuku doctor style` con errores y verificar que cada mensaje diga el defecto y cómo corregirlo.
