# Epic 001 · Un TUKU mínimo instalable

> Una persona nueva instala TUKU con un comando, siembra un vault en un directorio vacío y empieza a escribir el mismo día, sin configurar nada y sin saber qué es TUKU. Cubre la fase 0.

## Entregable

Una persona corre `uv tool install git+https://github.com/pewma-ai/tuku.git@devel` (o `pipx install` con la misma URL), después `tuku init mi-vault`, y ya puede abrir `mi-vault/AHORA.md` y escribir. Sin PyPI, sin editar config, sin leer `spec/`.

## Decisiones

1. TUKU se instala con `pipx` o `uv tool install` directo desde `git+https://github.com/pewma-ai/tuku.git@devel`. Sin PyPI.
2. El paquete trae `template/`, `docs/` y `spec/`, y la primera siembra los deja en `~/.tuku`, a la vista.
3. `tuku init [<dir>]` copia `template/<variante>` al destino (`vanilla` por defecto) y siembra `AHORA.md` con las fechas del primer ciclo. No toca la red.
4. La lógica vive en [`src/tuku/init.py`](../../src/tuku/init.py) y el CLI es una capa fina de argparse: los tests la llaman en proceso, salvo `001-01`, que prueba la instalación.
5. `resolver_home()` busca el árbol en este orden: argumento `home=`, variable `TUKU_HOME`, `~/.tuku`, copia empaquetada, raíz del checkout.
6. `template/` tiene una carpeta por variante, hermanas y sin composición. `vanilla/` es la mínima.
7. `reglas/config.tuku.md` declara zona horaria y tipo de ciclo.
8. Sembrar en un directorio con contenido se rechaza, salvo `tuku init --force`.
9. El estado cero se verifica byte a byte con fecha fija, contra `template/vanilla/` en vivo.
10. El nombre del autor vive en la fila `Nombre` de `reglas/autor.user.md`. `tuku init --author "..."` lo siembra; es opcional.

## Escenario: preparar el ambiente del epic

Dado el `playground/` como lo dejó la corrida anterior
Cuando se corre

```bash
rm -rf 001-*
```

Entonces no queda ningún resultado del epic 001, y cada escenario siembra sobre limpio

Es el único borrado del epic. `playground/001-*` es territorio de la suite: una carpeta tuya que empiece con `001-` se borra.

## Criterio de salida

`uv tool install` desde `git+...@devel` deja `tuku` en el PATH; `tuku init` en un directorio vacío produce el estado cero sin tocar la red; alguien que no sabe qué es TUKU escribe una línea en `AHORA.md` sin romper nada. Se verifica con una persona, no con un diff.

## No entra

Comandos, agentes, LLM. Tampoco el tipo de ciclo real de quien lo usa: arranca semanal.

## Escenarios del epic

- [`001-01-instalacion-con-uv-tool.md`](001-01-instalacion-con-uv-tool.md) — Instalación real con `uv tool install` y `pipx` (marcado `red`).
- [`001-02-init-siembra-el-estado-cero.md`](001-02-init-siembra-el-estado-cero.md) — `tuku init` produce byte a byte `template/vanilla/` con fechas resueltas, con la red bloqueada.
- [`001-03-destino-no-vacio.md`](001-03-destino-no-vacio.md) — Rechazo ante destino ocupado salvo `--force`.
- [`001-04-init-author.md`](001-04-init-author.md) — `tuku init --author` siembra el nombre en "El autor".
- [`001-06-cli-ayuda.md`](001-06-cli-ayuda.md) — Opciones de `tuku init` y código de entorno.
- [`001-07-lint-libro-de-estilo.md`](001-07-lint-libro-de-estilo.md) — Códigos de salida ante un libro de estilo o unos archivos de `reglas/` rotos.
