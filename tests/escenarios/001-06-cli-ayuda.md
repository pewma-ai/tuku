# Escenario · 001-06-cli-ayuda

**Cubre:** epic 001. La ayuda de `tuku init` y el código de entorno (3), distinto del de uso (2), según [`spec/cli.md`](../../spec/cli.md). La ayuda del resto del CLI está en el [`002-10`](002-10-cli-superficie.md).

## Escenario: `tuku init -h` lista las opciones que añade el epic 001

Dado el mismo CLI
Cuando se corre

```bash
tuku init -h
```

Entonces sale con código 0
Y el texto nombra `dir`, `--variante`, `--author` y `--force`

## Escenario: un entorno roto no se confunde con un error de uso

Dado un directorio que existe pero no tiene `template/`

```bash
mkdir arbol-roto
```

Cuando se corre con `TUKU_HOME` apuntando ahí

```bash
TUKU_HOME=arbol-roto tuku init mi-vault
```

Entonces sale con el código de entorno (3), distinto del de uso
Y el error dice qué le falta al árbol

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_06
```

No produce vault. La carpeta que el runner le da queda vacía, salvo el `arbol-roto/` del último caso.

## Qué se mira a mano

- Correr `uv run tuku -h` y `uv run tuku init -h` y leerlos: que se entiendan sin saber qué es TUKU, que `init` quede claro como "siembra un vault", y que el ejemplo mínimo (`tuku init mi-vault`) se deduzca de lo que hay.
