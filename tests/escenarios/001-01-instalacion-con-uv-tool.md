# Escenario · 001-01-instalacion-con-uv-tool

**Cubre:** epic 001, decisión 1.

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

## Escenario: `pipx install` desde este repositorio deja TUKU listo

Dado el checkout de trabajo, sin empujar nada a GitHub
Cuando se corre

```bash
pipx install --force <la raíz del repositorio>
tuku --help
tuku init mi-vault
```

Entonces vale lo mismo, con el código de este checkout y no el del branch remoto

## Notas

- Son los únicos que instalan: el resto del epic corre `tuku` en proceso. Prueban que el paquete compila, expone `tuku` y lleva dentro el árbol que `tuku init` necesita.
- `--force` reinstala sobre lo que hubiera, para poder correrlos dos veces seguidas.
- Llevan el marcador `red` y la corrida por defecto los excluye. Los dos primeros instalan `devel` desde GitHub, que tiene que estar empujado.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_01 -m red
```

Todo queda aislado: `HOME`, `UV_TOOL_DIR`, `UV_TOOL_BIN_DIR` y `PIPX_HOME` apuntan a un tempdir, así ninguna de las tres instalaciones toca el `~` real ni las tools del autor.

## Qué se mira a mano

- Que `tuku init` sin argumentos, dentro de un directorio cualquiera con contenido, se niegue con un mensaje claro (no un traceback).
- Cronometrar cuánto toma escribir el primer registro en `mi-vault/AHORA.md` leyendo solo `AGENTS.md`.
- Que una persona ajena al diseño instale así y opine.
