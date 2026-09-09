"""tuku rebuild: borra y regenera todo lo derivado del vault (principio 9).

Lo derivado no es fuente de verdad; se genera desde el conjunto canónico
(PENDIENTES.md, ambitos/, etc.) y por eso borrarlo y reconstruirlo debe devolver
exactamente el mismo estado byte a byte.
"""

from __future__ import annotations

from pathlib import Path

from tuku import scope, todo
from tuku.config import archivo_vault
from tuku.propagate import ARCHIVO_AMBITOS, display_name, documento_ambitos
from tuku.resultado import Resultado
from tuku.todo import SinTabla

#: Conjunto canónico de rutas relativas de archivos derivados en el vault.
ARCHIVOS_DERIVADOS: tuple[Path, ...] = (
    ARCHIVO_AMBITOS,  # ambitos/PENDIENTES-AMBITOS.md
)


def archivos_derivados(vault: Path) -> list[Path]:
    """Lista de archivos derivados del vault."""
    return [vault / rel for rel in ARCHIVOS_DERIVADOS]


def reconstruir(vault: Path) -> Resultado:
    """Borra y reconstruye los archivos y secciones derivadas del vault."""
    # 1. Validar canónico antes de tocar disco
    try:
        ruta_pendientes = archivo_vault(vault, "PENDIENTES.md")
    except Exception as e:
        return Resultado.rechazo(
            f"PENDIENTES.md: error: no se pudo leer ({e}). "
            "Corrige el archivo antes de reconstruir."
        )

    pendientes_txt = ruta_pendientes.read_text(encoding="utf-8")
    try:
        todo.filas(pendientes_txt)
    except SinTabla:
        return Resultado.rechazo(
            "PENDIENTES.md: error: falta la tabla de pendientes. "
            "Agrega la tabla con sus columnas antes de reconstruir."
        )
    except Exception as e:
        return Resultado.rechazo(
            f"PENDIENTES.md: error en la tabla ({e}). "
            "Corrige el formato de la tabla antes de reconstruir."
        )

    try:
        ambitos_objs = scope.leer(vault)
    except Exception as e:
        return Resultado.rechazo(
            f"ambitos: error al leer ámbitos ({e}). "
            "Corrige las carpetas de ámbito antes de reconstruir."
        )

    # 2. Borrar derivados existentes (seguro: el canónico ya se validó)
    derivados = archivos_derivados(vault)
    for d in derivados:
        if d.is_file():
            d.unlink()

    # 3. Regenerar derivados
    regenerados: list[str] = []

    disp_map: dict[str, str] = {}
    for a in ambitos_objs:
        pag = a.directorio / f"{a.nombre}.md"
        texto_pag = pag.read_text(encoding="utf-8") if pag.is_file() else None
        disp_map[a.nombre] = display_name(a.nombre, texto_pag)
        pag_mod = scope.actualizar_pagina(vault, a.nombre)
        if pag_mod:
            regenerados.append(str(pag_mod.relative_to(vault)))

    ruta_ambitos = vault / ARCHIVO_AMBITOS
    documento = documento_ambitos(
        pendientes_txt, [a.nombre for a in ambitos_objs], display_names=disp_map
    )
    ruta_ambitos.parent.mkdir(parents=True, exist_ok=True)
    ruta_ambitos.write_text(documento, encoding="utf-8")
    regenerados.append(str(ARCHIVO_AMBITOS))

    n = len(regenerados)
    lista = ", ".join(sorted(set(regenerados)))
    return Resultado.hecho(
        f"rebuild: {n} elemento(s) regenerado(s) ({lista})."
    )
