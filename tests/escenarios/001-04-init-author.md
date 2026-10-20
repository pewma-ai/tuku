# Escenario · 001-04-init-author

**Cubre:** epic 001, decisión 10. El nombre lleva espacios, paréntesis y guion para verificar que la siembra no lo parte ni toca el resto de la tabla.

## Escenario: el nombre del autor queda en reglas/autor.user.md

Dado un directorio destino vacío
Cuando se corre

```bash
tuku init mi-vault --at 2026-08-11 --author "ARTURO PEREZ-REVERTE (Arturo)"
```

Entonces `reglas/autor.user.md` queda con ese nombre en la fila `Nombre` de su tabla
Y no sobrevive el placeholder `PEDIR AL AUTOR!` en esa fila

## Escenario: un nombre en blanco deja el vault operable

Dado el mismo destino
Cuando se corre

```bash
tuku init en-blanco --at 2026-08-11 --author "   "
```

Entonces la fila `Nombre` queda intacta con su texto de partida
Y el vault igual queda operable (principio 2: dejar el nombre en blanco no impide escribir)

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_04
```

Cada escenario deja lo suyo bajo `playground/001-04-init-author/`: `mi-vault/` el primero, `en-blanco/` el segundo.

## Qué se mira a mano

- Abrir `reglas/autor.user.md` y ver el nombre en la primera fila de la tabla, sin buscarlo; y que `tuku context style` lo muestre en el capítulo Autor.
- Que quede claro, leyendo, que dejarlo en blanco es válido.
