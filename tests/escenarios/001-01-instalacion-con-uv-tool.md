# Escenario · 001-01-instalacion-con-uv-tool

**Cubre:** epic 001, fase 0, decidido #1 de [`../../devel/epics.md`](../../devel/epics.md).

## Escenario: `uv tool install` desde git deja TUKU listo

Dado un equipo con `uv` y sin TUKU
Cuando se corre

```bash
uv tool install --force "git+https://github.com/pewma-ai/tuku.git@devel"
tuku --help
tuku init mi-vault
```

Entonces queda el ejecutable `tuku` en el PATH y `tuku --help` responde
Y `tuku init mi-vault` sobre un directorio nuevo siembra un vault operable, sin tocar la red
Y esa primera siembra deja `~/.tuku/template/vanilla/` poblado desde la copia que el wheel trae empaquetada

## Escenario: `pipx install` desde git deja TUKU listo

Dado un equipo con `pipx` y sin TUKU
Cuando se corre

```bash
pipx install --force "git+https://github.com/pewma-ai/tuku.git@devel"
tuku --help
tuku init mi-vault
```

Entonces vale lo mismo que con `uv`: ejecutable en el PATH, vault operable y `~/.tuku` poblado

La decisión 1 nombra las dos vías, así que las dos se prueban. Que una funcione no dice nada de la otra: `uv` y `pipx` resuelven, compilan y exponen el ejecutable por caminos distintos.

## Escenario: `pipx install` desde este repositorio deja TUKU listo

Dado el checkout de trabajo, sin empujar nada a GitHub
Cuando se corre

```bash
pipx install --force <la raíz del repositorio>
tuku --help
tuku init mi-vault
```

Entonces vale lo mismo, con el código de este checkout y no el del branch remoto

Es el que le sirve al autor mientras desarrolla, y el único de los tres que prueba **lo que está escrito ahora**. Los otros dos prueban `devel` tal como quedó en GitHub, que puede ir por detrás. Si el empaquetado se rompe en un cambio sin commitear, este lo dice de inmediato y los otros dos no.

## Por qué son los únicos que instalan de verdad

Los otros `001-0X` corren `tuku` en proceso con `TUKU_HOME` apuntando al checkout: prueban la lógica sin instalar nada, rápido y sin red. Estos prueban el envoltorio que ninguno de ellos toca: que la instalación compila el wheel, lo deja en un entorno aislado y expone `tuku`; y que el árbol que `tuku init` necesita viaja dentro del paquete (`setup.py` copia `template/` a `tuku/_home/`), porque el clon de build se descarta.

Los tres llevan `--force`: reinstalan sobre lo que hubiera en vez de fallar si el entorno aislado ya existe, que es lo que pasa al correrlos dos veces seguidas.

Llevan el marcador `red` (además de `lento`): descargan y compilan. La corrida por defecto los excluye (`-m "not agentic and not red"`). Para los dos primeros, el branch `devel` tiene que estar empujado a GitHub.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_01 -m red
```

Todo queda aislado: `HOME`, `UV_TOOL_DIR`, `UV_TOOL_BIN_DIR` y `PIPX_HOME` apuntan a un tempdir, así ninguna de las tres instalaciones toca el `~` real ni las tools del autor.

## Qué se mira a mano

- Que `tuku init` sin argumentos, dentro de un directorio cualquiera con contenido, se niegue con un mensaje claro (no un traceback).
- Cronometrar cuánto toma escribir el primer registro en `mi-vault/AHORA.md` leyendo solo `AGENTS.md`.
- Que una persona ajena al diseño instale así y opine (criterio de salida del epic, Wishlist).
