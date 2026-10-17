"""tuku regenerate: regenera lo derivado del vault desde el canónico (principio 9).

Lo derivado no es fuente de verdad: se regenera, no se repara, y regenerarlo
desde el conjunto canónico devuelve lo mismo byte a byte. Por tema:

- `todo`: la región de cada día de `AHORA.md` y `ambitos/PENDIENTES-AMBITOS.md`,
  desde `PENDIENTES.md` y el árbol de `ambitos/`.
- `scope`: la actividad de cada página de ámbito, desde `AHORA.md`, y su lista
  de hijos, desde las carpetas de `ambitos/`.
- `comandos`: `reglas/comandos.tuku.md`, desde la ayuda del `tuku` instalado.
- Sin tema: los tres.

`todo` y `scope` validan el canónico antes de escribir: con `PENDIENTES.md` o
`ambitos/` rotos rechazan sin tocar nada. `comandos` no depende del canónico.
"""

from __future__ import annotations

from pathlib import Path

from tuku import scope, todo
from tuku.config import archivo_vault
from tuku.resultado import Resultado
from tuku.todo import SinTabla

#: Los temas que se regeneran por separado.
TEMAS = ("todo", "scope", "comandos")

COMANDOS = Path("reglas") / "comandos.tuku.md"


def _rechazo_del_canonico(vault: Path) -> Resultado | None:
    try:
        texto = archivo_vault(vault, "PENDIENTES.md").read_text(encoding="utf-8")
    except Exception as e:
        return Resultado.rechazo(
            f"PENDIENTES.md: error: no se pudo leer ({e}). "
            "Corrige el archivo antes de regenerar."
        )
    try:
        todo.filas(texto)
    except SinTabla:
        return Resultado.rechazo(
            "PENDIENTES.md: error: falta la tabla de pendientes. "
            "Agrega la tabla con sus columnas antes de regenerar."
        )
    except Exception as e:
        return Resultado.rechazo(
            f"PENDIENTES.md: error en la tabla ({e}). "
            "Corrige el formato de la tabla antes de regenerar."
        )
    try:
        scope.leer(vault)
    except Exception as e:
        return Resultado.rechazo(
            f"ambitos: error al leer ámbitos ({e}). "
            "Corrige las carpetas de ámbito antes de regenerar."
        )
    return None


def regenerar(
    vault: Path, *, tema: str | None = None, comandos: str | None = None
) -> Resultado:
    """Regenera lo derivado del `tema`, o todo si no hay tema.

    `comandos`, si se pasa, es `reglas/comandos.tuku.md` tal como lo escribe el
    `tuku` instalado: se deriva de él y no del canónico, y regenerarlo es la
    forma de ponerlo al día tras actualizar TUKU. Solo escribe lo que cambió.
    """
    from tuku.propagate import propagar

    cambiados: list[str] = []

    if tema != "comandos":
        if (rechazo := _rechazo_del_canonico(vault)) is not None:
            return rechazo
        derivados = propagar(vault, vistas=tema != "scope", paginas=tema != "todo")
        cambiados += [p.relative_to(vault).as_posix() for p in derivados]
        if tema != "todo":
            cambiados += [p.relative_to(vault).as_posix() for p in scope.regenerar_hijos(vault)]

    if tema in (None, "comandos") and comandos is not None and (vault / "reglas").is_dir():
        ruta = vault / COMANDOS
        if not ruta.is_file() or ruta.read_text(encoding="utf-8") != comandos:
            ruta.write_text(comandos, encoding="utf-8")
            cambiados.append(COMANDOS.as_posix())

    if not cambiados:
        return Resultado.hecho("regenerate: todo estaba al día.")
    return Resultado.hecho(
        "\n".join(f"regenerado: {ruta}" for ruta in sorted(set(cambiados)))
    )
