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

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from tuku import archivo, link
from tuku.doctor import archivos_md
from tuku.resultado import Resultado


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
        texto = archivo.leer(ruta)
        conversion = link.convertir(texto, rel, idx)
        if conversion.convertidos:
            archivo.escribir(ruta, conversion.texto, conservar_fecha=True)
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


def fix_todo(vault: Path, *, now: datetime) -> Resultado:
    """Repara `PENDIENTES.md` y `AHORA.md`.

    Pasa la tabla anterior a `Creado` a la de cinco columnas, con el día de `now`
    en las filas que no lo tenían. Quita de `AHORA.md` los registros que abrieron
    un pendiente cerrado el mismo día: queda solo el `(Hecho)`. Después regenera
    lo que se deriva. Una segunda corrida no cambia nada.
    """
    from tuku import regenerate, todo_core
    from tuku.config import archivo_vault

    ruta = archivo_vault(vault, "AHORA.md")
    texto = archivo.leer(ruta)
    quitados = todo_core.cerrados_el_mismo_dia(texto)
    ruta_tabla = archivo_vault(vault, "PENDIENTES.md")
    tabla = archivo.leer(ruta_tabla)
    migrada = todo_core.migrar(tabla, now.date()) if todo_core.sin_creado(tabla) else tabla
    if not quitados and migrada == tabla:
        return Resultado.hecho("fix todo: nada que reparar.")
    if migrada != tabla:
        archivo.escribir(ruta_tabla, migrada)
    if quitados:
        archivo.escribir(ruta, todo_core.quitar_aperturas_cerradas(texto))
    regenerate.rehacer(vault, ["AHORA.md"])
    return Resultado.hecho(
        "\n".join(
            [
                *(
                    [f"PENDIENTES.md: columna `Creado` agregada, con {now.date().isoformat()}."]
                    if migrada != tabla
                    else []
                ),
                *(f"AHORA.md: quitado el que abrió {a.cuerpo!r} ({a.dia})." for a in quitados),
                f"fix todo: {len(quitados)} registro(s) quitado(s).",
            ]
        )
    )


TEMAS: dict[str, Callable[[Path, datetime], Resultado]] = {
    "link": lambda vault, now: fix_link(vault),
    "todo": lambda vault, now: fix_todo(vault, now=now),
}


def corregir(vault: Path, tema: str, *, now: datetime) -> Resultado:
    """Aplica el `fix` de un tema. Los temas son los de `doctor.TEMAS`."""
    return TEMAS[tema](vault, now)
