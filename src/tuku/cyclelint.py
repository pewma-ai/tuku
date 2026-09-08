"""tuku cycle lint: revisa la estructura de `AHORA.md` y reporta. Nunca escribe.

Es el complemento de `tuku entry lint`: aquel revisa los registros, este revisa
el archivo que los contiene. Lo que verifica es lo que el resto de los comandos
da por cierto sin comprobarlo, y que si falta produce fallas mudas más adelante:

- El frontmatter OKF con `from` y `to` resueltos. Sin eso, ningún encabezado de
  día puede fecharse, porque el año sale del rango (`ahora.py`).
- Los siete encabezados de día dentro del rango del ciclo.
- El `type` y el `status` que `reglas/types.md` y el libro de estilo fijan para
  un ciclo. De `to` sale dónde termina, así que no hace falta marcarlo aparte
  en el cuerpo.

**Qué lee y escribe:** lee `AHORA.md`. **No escribe.** Verificar y corregir son
operaciones distintas (`spec/cli.md`).
**A mano:** abrir `AHORA.md` y revisar su frontmatter y sus encabezados de día.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tuku import ahora as _ahora
from tuku.resultado import Resultado

#: Lo que un ciclo declara en su frontmatter. `Logbook` porque `AHORA.md` y una
#: bitácora cerrada son el mismo tipo de archivo (ver `reglas/types.md`).
TYPE_DEL_CICLO = "Logbook"

#: Un ciclo abierto es borrador. Pasa a `stable` cuando se archiva.
STATUS_ABIERTO = "draft"

ERROR = "error"


@dataclass(frozen=True)
class Hallazgo:
    """Un hallazgo del lint. `correccion` no es opcional: `spec/cli.md` exige
    que toda salida nombre el defecto y qué hacer con él."""

    linea: int
    grado: str
    defecto: str
    correccion: str

    def __str__(self) -> str:
        return f"AHORA.md:{self.linea}: {self.grado}: {self.defecto}. {self.correccion}"


def lint(ahora: str) -> list[Hallazgo]:
    """Los hallazgos estructurales de `AHORA.md`, en orden. No modifica nada."""
    hallazgos: list[Hallazgo] = []
    rango = _ahora.rango(ahora)

    if rango is None:
        hallazgos.append(
            Hallazgo(
                1,
                ERROR,
                "el frontmatter no tiene `from` y `to` resueltos",
                "Corre `tuku cycle open`, que los escribe con las fechas del ciclo.",
            )
        )
    else:
        desde, hasta = rango
        for n, texto, fecha in _ahora.dias(ahora):
            if fecha is None:
                hallazgos.append(
                    Hallazgo(
                        n,
                        ERROR,
                        f"el encabezado {texto!r} no se puede fechar",
                        "Escríbelo como `## Lunes 7 de septiembre`, con el mes en palabras.",
                    )
                )
            elif not desde <= fecha <= hasta:
                hallazgos.append(
                    Hallazgo(
                        n,
                        ERROR,
                        f"el día {fecha.isoformat()} cae fuera del ciclo abierto "
                        f"({desde.isoformat()} a {hasta.isoformat()})",
                        "Sácalo de aquí, o abre el ciclo que lo cubre.",
                    )
                )

    frontmatter = _frontmatter(ahora)
    for campo, esperado, correccion in (
        ("type", TYPE_DEL_CICLO, "Es el `type` de un ciclo, y sale de `reglas/types.md`."),
        ("status", STATUS_ABIERTO, "Un ciclo abierto es borrador; `stable` es el archivado."),
    ):
        valor = frontmatter.get(campo)
        if valor is None:
            hallazgos.append(
                Hallazgo(
                    1,
                    ERROR,
                    f"el frontmatter no declara `{campo}`",
                    f"Agrega `{campo}: {esperado}`. {correccion}",
                )
            )
        elif valor != esperado:
            hallazgos.append(
                Hallazgo(
                    1,
                    ERROR,
                    f"el frontmatter dice `{campo}: {valor}` y un ciclo abierto es "
                    f"`{campo}: {esperado}`",
                    correccion,
                )
            )

    return hallazgos


def _frontmatter(ahora: str) -> dict[str, str]:
    """Los campos escalares del frontmatter. `{}` si no hay bloque."""
    if not ahora.startswith("---\n"):
        return {}
    fin = ahora.find("\n---", 4)
    if fin == -1:
        return {}
    campos: dict[str, str] = {}
    for linea in ahora[4:fin].splitlines():
        clave, sep, valor = linea.partition(":")
        if sep and not clave.startswith((" ", "\t")):
            campos[clave.strip()] = valor.strip()
    return campos


def formatear(hallazgos: list[Hallazgo]) -> str:
    """El reporte, para persona y para agente. Es el mismo texto para los dos."""
    if not hallazgos:
        return "cycle lint: sin hallazgos."
    return "\n".join([*(str(h) for h in hallazgos), f"cycle lint: {len(hallazgos)} error(es)."])


def lint_del_vault(vault: Path) -> Resultado:
    """Revisa la estructura de `AHORA.md` y reporta; no escribe."""
    from tuku.config import archivo_vault

    ahora = archivo_vault(vault, "AHORA.md").read_text(encoding="utf-8")
    hallazgos = lint(ahora)
    mensaje = formatear(hallazgos)
    if hallazgos:
        return Resultado.rechazo(mensaje, error=False)
    return Resultado.hecho(mensaje)
