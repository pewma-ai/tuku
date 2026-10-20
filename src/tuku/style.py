"""tuku style: validación y lint del libro de estilo y de los archivos del autor en `reglas/`.

Revisa los contratos que los comandos de TUKU necesitan para operar
(`spec/vault.md`, "El libro de estilo"):
1. La fila `Nombre` de la tabla de `reglas/autor.user.md`.
2. Que cada archivo de vocabulario (`reglas/clasificaciones.user.md`,
   `reglas/pendientes.user.md`, `reglas/notas.user.md`) tenga su tabla de términos.
3. Que ningún capítulo del libro ni archivo del autor tenga más de una tabla.
4. Que cada transclusión `![](ruta)` del libro apunte a un archivo que existe.

Toda falla reporta el defecto y la corrección (spec/cli.md).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from tuku import capitulos, vocab
from tuku.lint import ERROR, PREGUNTA

LIBRO = "LIBRO-DE-ESTILO.md"
AUTOR = "reglas/autor.user.md"

#: Los archivos que el lint necesita además de las transclusiones del libro.
ARCHIVOS = (LIBRO, AUTOR, *vocab.ARCHIVOS)


@dataclass(frozen=True)
class HallazgoEstilo:
    """Un hallazgo del lint de estilo."""

    archivo: str
    linea: int | None
    grado: str
    defecto: str
    correccion: str

    def __str__(self) -> str:
        ref = f"{self.archivo}:{self.linea}" if self.linea else self.archivo
        marca = "error" if self.grado == ERROR else "pregunta"
        return f"{ref}: {marca}: {self.defecto}. {self.correccion}"


def lint(textos: Mapping[str, str | None]) -> list[HallazgoEstilo]:
    """Revisa el libro y los archivos del autor.

    `textos` mapea la ruta de cada archivo dentro del vault a su texto, o a
    `None` si no está. Debe traer `ARCHIVOS` y las transclusiones del libro.
    """
    hallazgos: list[HallazgoEstilo] = []

    # 1. La fila Nombre del autor
    autor = textos.get(AUTOR)
    if autor is None:
        hallazgos.append(_falta_archivo(AUTOR, "con su tabla Campo y Valor y la fila 'Nombre'"))
    elif not _tiene_fila_nombre(autor):
        hallazgos.append(
            HallazgoEstilo(
                archivo=AUTOR,
                linea=None,
                grado=ERROR,
                defecto="falta la fila 'Nombre' en la tabla",
                correccion="Agrégala para que `tuku init --author` funcione.",
            )
        )

    # 2. Las tablas de vocabulario
    for vocabulario, ruta in vocab.FUENTES.items():
        texto = textos.get(ruta)
        if texto is None:
            hallazgos.append(_falta_archivo(ruta, "con su tabla de términos"))
            continue
        tabla = capitulos.primera_tabla(texto)
        if tabla is None:
            hallazgos.append(
                HallazgoEstilo(
                    archivo=ruta,
                    linea=None,
                    grado=ERROR,
                    defecto="falta la tabla de términos",
                    correccion="Es contrato: agrégala con sus encabezados.",
                )
            )
        elif not vocab.terminos(texto, vocabulario):
            hallazgos.append(
                HallazgoEstilo(
                    archivo=ruta,
                    linea=None,
                    grado=PREGUNTA,
                    defecto="la tabla no tiene ningún término declarado",
                    correccion=(
                        "Declara al menos un término en la primera columna entre backticks "
                        "(p. ej. `progreso`)."
                    ),
                )
            )

    # 3. Una tabla por archivo del autor y por capítulo del libro
    for ruta, texto in textos.items():
        if texto is None:
            continue
        if ruta.endswith(".user.md"):
            n = len(capitulos.tablas_del_archivo(texto))
            if n > 1:
                hallazgos.append(
                    HallazgoEstilo(
                        archivo=ruta,
                        linea=None,
                        grado=ERROR,
                        defecto=f"el archivo tiene {n} tablas",
                        correccion=(
                            "Un archivo del autor lleva una tabla: la que leen los comandos."
                        ),
                    )
                )
            continue
        for cap in capitulos.exceso_de_tablas(texto):
            hallazgos.append(
                HallazgoEstilo(
                    archivo=ruta,
                    linea=cap.linea,
                    grado=ERROR,
                    defecto=f"el capítulo '{cap.nombre}' tiene {len(cap.tablas())} tablas",
                    correccion=(
                        "Un capítulo lleva una sola tabla, la que leen los comandos: "
                        "pasa las demás a otro capítulo."
                    ),
                )
            )

    # 4. Las transclusiones del libro apuntan a archivos que existen
    libro = textos.get(LIBRO)
    for ruta in capitulos.transclusiones(libro) if libro is not None else []:
        if textos.get(ruta) is None:
            hallazgos.append(
                HallazgoEstilo(
                    archivo=LIBRO,
                    linea=None,
                    grado=ERROR,
                    defecto=f"la transclusión '![]({ruta})' apunta a un archivo que no existe",
                    correccion=f"Crea {ruta}, o regenera el libro si es viejo.",
                )
            )

    return hallazgos


def _tiene_fila_nombre(texto: str) -> bool:
    tabla = capitulos.primera_tabla(texto)
    return tabla is not None and any(f and f[0].lower() == "nombre" for f in tabla[1:])


def _falta_archivo(ruta: str, que: str) -> HallazgoEstilo:
    return HallazgoEstilo(
        archivo=ruta,
        linea=None,
        grado=ERROR,
        defecto="falta el archivo",
        correccion=f"Es contrato para automatizaciones: créalo {que}.",
    )


def formatear(hallazgos: list[HallazgoEstilo]) -> str:
    """Formatea los hallazgos para salida de CLI o reporte."""
    if not hallazgos:
        return "style lint: sin hallazgos."
    errores = sum(1 for h in hallazgos if h.grado == ERROR)
    preguntas = len(hallazgos) - errores
    resumen = f"style lint: {errores} error(es), {preguntas} pregunta(s)."
    return "\n".join([*(str(h) for h in hallazgos), resumen])
