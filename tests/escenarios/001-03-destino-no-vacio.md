# Escenario · 001-03-destino-no-vacio

**Cubre:** epic 001, fase 0, decidido #8 de [`../../devel/epics.md`](../../devel/epics.md).

## Escenario: no sembrar sobre un directorio que ya tiene algo

Dado un directorio destino que ya existe y no está vacío

```bash
mkdir mi-vault
echo "no tocar" > mi-vault/algo-que-ya-estaba.txt
```

Cuando se corre

```bash
tuku init mi-vault --date 2026-08-11
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
tuku init mi-vault --date 2026-08-11 --force
```

Entonces el contenido previo se reemplaza y queda un vault operable

## Escenario: un destino vacío se siembra sin `force`

Dado un directorio que no existe
Cuando se corre

```bash
tuku init mi-vault --date 2026-08-11
```

Entonces siembra sin más: la negativa es por contenido, no por que el directorio exista

## Por qué importa

Es el único caso donde equivocarse borra trabajo de alguien. `001-01` y `001-02` prueban que la siembra llega a buen puerto; este prueba que no hace daño cuando no debería tocar nada.

Cambió respecto al cierre del 2026-09-06: `install.sh` preguntaba por `/dev/tty` y el test respondía el prompt con `pexpect`. La decisión 8 lo reemplazó por el flag `--force`, porque la lógica es importable y no depende de una tty. Ya no hace falta `pexpect` ni pty.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_03
```

Cada caso deja su resultado en su propia carpeta bajo `playground/001-03-destino-no-vacio/`, para poder mirar los tres y no solo el último.

## Qué se mira a mano

- Que el mensaje de `DestinoNoVacio` se entienda sin contexto y diga cómo forzar (`tuku init --force`).
