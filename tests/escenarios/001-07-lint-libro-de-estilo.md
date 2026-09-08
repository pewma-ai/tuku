# Escenario · 001-07-lint-libro-de-estilo

**Cubre:** epic 001, contratos de [`LIBRO-DE-ESTILO.md`](../../template/vanilla/LIBRO-DE-ESTILO.md) requeridos por comandos de TUKU.

## Estado inicial

Un vault recién sembrado por `tuku init`.

## Escenario: el libro de estilo vanilla pasa el lint sin hallazgos

Dado un vault recién sembrado
Cuando se ejecuta `tuku style lint`
Entonces sale con código 0 (éxito) y sin hallazgos

## Escenario: falta el marcador de autor

Dado un vault donde se eliminó la línea `**Nombre del autor:**` de `LIBRO-DE-ESTILO.md`
Cuando se ejecuta `tuku style lint`
Entonces reporta un error señalando que falta el marcador y la corrección
Y cuando se intenta `tuku init --author "Pepe"` sobre ese vault
Entonces se rechaza con código 1 indicando el defecto y la corrección

## Escenario: falta un encabezado de contrato

Dado un vault donde falta alguno de los encabezados de contrato (`### Clasificaciones`, `### Horizontes`, `### Tipos de nota`)
Cuando se ejecuta `tuku style lint`
Entonces reporta un error por cada encabezado faltante indicando defecto y corrección
Y cuando se invoca un comando que requiere ese vocabulario (`tuku vocab show`)
Entonces se rechaza con código 1 nombrando el encabezado faltante

## Escenario: tabla de vocabulario vacía

Dado un vault donde un encabezado de contrato existe pero no declara ningún término
Cuando se ejecuta `tuku style lint`
Entonces reporta una pregunta indicando que la tabla no tiene términos y cómo declararlos

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_07
```

Deja el vault en `playground/001-07-lint-libro-de-estilo/`.

## Qué se mira a mano

- Leer la salida de `tuku style lint` cuando hay errores y verificar que cada mensaje indique con claridad el defecto y cómo corregirlo.
