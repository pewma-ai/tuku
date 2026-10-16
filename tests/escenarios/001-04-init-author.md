# Escenario · 001-04-init-author

**Cubre:** epic 001, decisión 10. El nombre lleva espacios, paréntesis y guion para verificar que la siembra no lo parte ni toca la prosa que sigue al marcador.

## Escenario: el nombre del autor queda en el libro de estilo

Dado un directorio destino vacío
Cuando se corre

```bash
tuku init mi-vault --date 2026-08-11 --author "ARTURO PEREZ-REVERTE (Arturo)"
```

Entonces `LIBRO-DE-ESTILO.md` queda con ese nombre en la sección "El autor"
Y no sobrevive el placeholder `por declarar`

## Escenario: un nombre en blanco deja el vault operable

Dado el mismo destino
Cuando se corre

```bash
tuku init en-blanco --date 2026-08-11 --author "   "
```

Entonces la línea `**Nombre del autor:**` queda intacta con su texto de partida
Y el vault igual queda operable (principio 2: dejar el nombre en blanco no impide escribir)

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_04
```

Cada escenario deja lo suyo bajo `playground/001-04-init-author/`: `mi-vault/` el primero, `en-blanco/` el segundo.

## Qué se mira a mano

- Abrir `LIBRO-DE-ESTILO.md` y ver el nombre **al inicio del documento**, en "El autor", sin buscarlo.
- Que quede claro, leyendo, que dejarlo en blanco es válido.
