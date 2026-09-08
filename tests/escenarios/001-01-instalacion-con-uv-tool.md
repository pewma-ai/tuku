# Escenario · 001-01-instalacion-con-uv-tool

**Cubre:** epic 001, fase 0, decidido #1 de [`../../devel/epics.md`](../../devel/epics.md).

## Escenario: alguien instala TUKU con un comando y siembra un vault

Dado un equipo con `uv` y sin TUKU
Cuando corre `uv tool install "git+https://github.com/pewma-ai/tuku.git@devel"`
Entonces queda el ejecutable `tuku` en el PATH y `tuku --help` responde
Y `tuku init mi-vault` sobre un directorio nuevo siembra un vault operable, sin tocar la red
Y esa primera siembra deja `~/.tuku/template/vanilla/` poblado desde la copia que el wheel trae empaquetada

## Por qué es el único que instala de verdad

Los otros cuatro `001-00X` llaman a `tuku.init.init()` con `home=` apuntando al checkout: prueban la lógica sin instalar nada, rápido y sin red. Este prueba el envoltorio que ninguno de ellos toca: que `uv tool install` desde `git+...@devel` compila el wheel, lo deja en un entorno aislado y expone `tuku`; y que el árbol que `tuku init` necesita viaja dentro del paquete (`setup.py` copia `template/` a `tuku/_home/`), porque el clon de build se descarta.

Lleva el marcador `red` (además de `lento`): descarga y compila. La corrida por defecto lo excluye (`-m "not agentic and not red"`). El branch `devel` tiene que estar empujado a GitHub.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_01 -m red
```

Todo queda aislado: `HOME`, `UV_TOOL_DIR` y `UV_TOOL_BIN_DIR` apuntan a un tempdir, así la instalación no toca el `~` real ni las tools del autor.

A mano, el camino que prueba:

```bash
uv tool install --force "git+https://github.com/pewma-ai/tuku.git@devel"
tuku init /tmp/mi-vault
```

## Qué se mira a mano

- Que `tuku init` sin argumentos, dentro de un directorio cualquiera con contenido, se niegue con un mensaje claro (no un traceback).
- Cronometrar cuánto toma escribir el primer registro en `mi-vault/AHORA.md` leyendo solo `AGENTS.md`.
- Que una persona ajena al diseño instale así y opine (criterio de salida del epic, Wishlist).
