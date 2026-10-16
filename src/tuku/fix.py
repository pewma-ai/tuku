"""tuku fix TEMA: repara lo que `tuku doctor TEMA` reporta.

Verificar y reparar son operaciones distintas (`spec/cli.md`): el doctor informa
y este módulo escribe. Cada tema tiene su `fix`, y un hallazgo del tema nombra
`tuku fix TEMA` como corrección.

**Lo determinista se aplica; lo que requiere juicio se devuelve.** Un `fix` con
hallazgos mixtos aplica lo primero, deja intacto lo segundo y sale con
`RECHAZO` listando las decisiones que le tocan al autor. Quien corre TUKU suele
ser un agente, y esas decisiones no son suyas.

**Qué lee y escribe:** todos los `.md` del vault, incluidos los ciclos cerrados
de `bitacoras/`: convertir un link cambia el formato sin agregar enlaces, así
que repara y no enriquece el pasado (`spec/ambitos.md`). Escribe solo los
archivos que cambian, y les conserva la fecha de modificación, porque una
conversión de forma no es una edición del autor.
**A mano:** buscar cada `[[nombre]]` y reemplazarlo por `[nombre](ruta/hasta/nombre.md)`,
con la ruta calculada desde el archivo donde está.
"""

from __future__ import annotations

import os
from pathlib import Path

from tuku import link
from tuku.doctor import archivos_md
from tuku.resultado import Resultado


def _escribir_conservando_fecha(ruta: Path, texto: str) -> None:
    """Escribe `texto` sin tocar la fecha de modificación del archivo."""
    antes = ruta.stat()
    ruta.write_text(texto, encoding="utf-8")
    os.utime(ruta, ns=(antes.st_atime_ns, antes.st_mtime_ns))


def fix_link(vault: Path) -> Resultado:
    """Convierte los wikilinks a Markdown y devuelve lo que no se puede decidir solo.

    Un wikilink que no resuelve, o que resuelve a más de un archivo, se deja
    como está. Un link Markdown roto tampoco se toca. Los dos salen como
    decisión. Una segunda corrida no cambia nada.
    """
    archivos = archivos_md(vault)
    idx = link.indice(archivos)

    convertidos = 0
    tocados = 0
    decisiones: list[str] = []
    for rel in archivos:
        ruta = vault / rel
        texto = ruta.read_text(encoding="utf-8")
        conversion = link.convertir(texto, rel, idx)
        if conversion.convertidos:
            _escribir_conservando_fecha(ruta, conversion.texto)
            convertidos += conversion.convertidos
            tocados += 1
        decisiones += [
            f"{d.archivo}:{d.linea}: {d.original} {d.motivo}. Decide qué archivo es "
            "(o créalo) y escribe el link Markdown a mano."
            for d in conversion.decisiones
        ]
        decisiones += [
            f"{rel}:{r.linea}: [{r.texto}]({r.destino}) apunta a un archivo que no "
            "existe. Decide a cuál debía apuntar, o si hay que crearlo."
            for r in link.rotos(conversion.texto, rel, lambda p: (vault / p).exists())
        ]

    resumen = (
        f"fix link: {convertidos} link(s) convertido(s) en {tocados} archivo(s)."
        if convertidos
        else "fix link: nada que convertir."
    )
    if not decisiones:
        return Resultado.hecho(resumen)
    return Resultado.rechazo(
        "\n".join(
            [
                resumen,
                f"fix link: {len(decisiones)} decisión(es) para el autor, sin escribir:",
                *decisiones,
                "Una vez decididas, corre `tuku doctor link` para confirmar.",
            ]
        ),
        error=False,
    )


TEMAS = {"link": fix_link}


def corregir(vault: Path, tema: str) -> Resultado:
    """Aplica el `fix` de un tema. Los temas son los de `doctor.TEMAS`."""
    return TEMAS[tema](vault)
