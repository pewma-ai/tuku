# Escenario · 001-03-destino-no-vacio

**Cubre:** epic 001, decisión 8. Es el único caso donde equivocarse borra trabajo de alguien.

## Escenario: no sembrar sobre un directorio que ya tiene algo

Dado un directorio destino que ya existe y no está vacío

```bash
mkdir mi-vault
echo "no tocar" > mi-vault/algo-que-ya-estaba.txt
```

Cuando se corre

```bash
tuku init mi-vault --at 2026-08-11
```

Entonces sale con código 1, el mensaje nombra el destino ocupado y `--force` como corrección, y el destino queda exactamente igual a como estaba

## Escenario: `--force` siembra igual

Dado el mismo directorio destino

```bash
mkdir mi-vault
echo "no tocar" > mi-vault/algo-que-ya-estaba.txt
```

Cuando se corre

```bash
tuku init mi-vault --at 2026-08-11 --force
```

Entonces el contenido previo se reemplaza y queda un vault operable

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_03
```

Cada caso deja su resultado en su propia carpeta bajo `playground/001-03-destino-no-vacio/`.

## Qué se mira a mano

- Que el mensaje de `DestinoNoVacio` se entienda sin contexto y diga cómo forzar (`tuku init --force`).
