"""Escribe treinta notas `persona` en `notas/` del vault que se pasa como argumento.

La primera tiene el `updated` más antiguo (2026-06-01) y la última el más reciente
(2026-06-30), un día de diferencia entre una y otra.
"""

from __future__ import annotations

import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

PERSONAS = [
    "Rodrigo Salinas",
    "Elena Vidal",
    "Hugo Ortega",
    "Inés Cabrera",
    "Samuel Toro",
    "Teresa Montt",
    "Andrés Lagos",
    "Beatriz Ferrada",
    "Cristóbal Pinto",
    "Gloria Sandoval",
    "Esteban Araya",
    "Fernanda Bravo",
    "Gonzalo Mena",
    "Helena Cortés",
    "Ignacio Vera",
    "Julia Bustos",
    "Manuel Parra",
    "Natalia Rojas",
    "Óscar Tapia",
    "Pilar Méndez",
    "Ramón Sepúlveda",
    "Sofía Aguirre",
    "Tomás Escobar",
    "Valeria Contreras",
    "Walter Núñez",
    "Ximena Godoy",
    "Yerko Campos",
    "Zulema Soto",
    "Álvaro Fierro",
    "Daniela Paredes",
]


def slug(titulo: str) -> str:
    plano = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    return "-".join(plano.lower().split())


def main(vault: Path) -> None:
    for i, nombre in enumerate(PERSONAS):
        dia = (date(2026, 6, 1) + timedelta(days=i)).isoformat()
        (vault / "notas" / f"{slug(nombre)}.md").write_text(
            f"---\ntype: Note\nsubtype: persona\ncreated: {dia}\nupdated: {dia}\n---\n\n"
            f"# {nombre}\n\nPersona del negocio.\n\n## Ver además\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main(Path(sys.argv[1]))
