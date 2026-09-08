# Epic 001 · Un TUKU mínimo instalable

> Que una persona nueva instale TUKU con un comando, siembre un vault en un directorio vacío y empiece a escribir el mismo día, sin configurar nada y sin saber qué es TUKU. Va primero porque obliga al repositorio a tener estructura, instalación y template, y nada más lo va a forzar. Cubre la fase 0.

## Entregable

Una persona corre `uv tool install git+https://github.com/pewma-ai/tuku.git@devel` (o `pipx install` con la misma URL), después `tuku init mi-vault`, y ya puede abrir `mi-vault/AHORA.md` y escribir. Sin PyPI, sin editar config, sin leer `spec/`.

## Decisiones

1. TUKU se distribuye como paquete Python instalable con `pipx` o `uv tool install` directo desde `git+https://github.com/pewma-ai/tuku.git@devel`. Sin PyPI. Lo fijó la decisión 4 del epic 002.
2. Esa instalación deja en `~/.tuku` lo que `tuku init` necesita. El wheel empaqueta hoy solo `template/` (lo único que `tuku init` copia), no `spec/` ni el árbol entero. La copia empaquetada se materializa en `~/.tuku` la primera vez que se siembra desde ahí, así el árbol queda a la vista y editable.
3. `tuku init [<dir>]` reemplaza a `install.sh` y a `src/install_test_scenario.py`. Copia `~/.tuku/template/<variante>` al destino (`vanilla` por defecto) y siembra `AHORA.md` con las fechas del primer ciclo. Offline: no toca la red.
4. `src/install_test_scenario.py` se reemplaza por la función `init` bajo [`src/tuku/init.py`](../../src/tuku/init.py). El CLI ([`src/tuku/cli.py`](../../src/tuku/cli.py)) es una capa fina de argparse; la lógica es importable y los tests la llaman sin subprocesos, salvo `001-01` que prueba el propio `uv tool install`.
5. `tuku` resuelve la ubicación del árbol con `resolver_home()`: argumento `home=` → variable `TUKU_HOME` → `~/.tuku` → copia empaquetada en el wheel → raíz del checkout. `home=` y `TUKU_HOME` son el override para tests e instalaciones no estándar.
6. `template/`, una carpeta por variante, hermanas y sin composición. `vanilla/` es la mínima.
7. `reglas/config.tuku.md` declara zona horaria y tipo de ciclo, en prosa.
8. Sembrar en un directorio que ya tiene contenido se rechaza, salvo `tuku init --force`.
9. El estado cero se verifica byte a byte con fecha fija (la del ground truth en `referencia-faena.md`), contra `template/vanilla/` en vivo, nunca contra una copia congelada.
10. Capa de identidad mínima: el nombre del autor vive en `LIBRO-DE-ESTILO.md` (sección "El autor", al inicio del documento). `tuku init --author "..."` lo siembra; es opcional y vacío es válido (omitir el flag deja el vault operable).

## Criterio de salida

`uv tool install` desde `git+...@devel` deja `tuku` en el PATH y `~/.tuku` poblado con el árbol del repositorio; `tuku init` en un directorio vacío produce el estado cero de `template/README.md` sin tocar la red; alguien que no sabe qué es TUKU escribe una línea en `AHORA.md` sin romper nada. `tuku init --author` deja el nombre en `LIBRO-DE-ESTILO.md`, y omitirlo no impide escribir. Se verifica con una persona, no con un diff.

## No entra

Comandos, agentes, LLM. Tampoco el tipo de ciclo real de quien lo usa: arranca semanal y el tipo verdadero emerge después.

## Escenarios del epic

- [`001-01-instalacion-con-uv-tool.md`](001-01-instalacion-con-uv-tool.md) — Instalación real con `uv tool install --force` desde git (marcado `red`).
- [`001-02-init-siembra-el-estado-cero.md`](001-02-init-siembra-el-estado-cero.md) — `tuku init` produce byte a byte `template/vanilla/` con fechas resueltas en `AHORA.md`.
- [`001-03-destino-no-vacio.md`](001-03-destino-no-vacio.md) — Rechazo ante destino ocupado salvo `--force`.
- [`001-04-init-author.md`](001-04-init-author.md) — `tuku init --author` siembra el nombre en la sección "El autor".
- [`001-05-init-no-toca-la-red.md`](001-05-init-no-toca-la-red.md) — Siembra offline con socket bloqueado.
- [`001-06-cli-ayuda.md`](001-06-cli-ayuda.md) — Superficie del CLI y opciones de `tuku init`.
- [`001-07-lint-libro-de-estilo.md`](001-07-lint-libro-de-estilo.md) — Validación del contrato de identidad y ontología en `LIBRO-DE-ESTILO.md`.
