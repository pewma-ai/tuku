"""Una conversación a mano: quien hace de autor manda una frase por vez al agente.

El autor simulado no es otro modelo del arnés: lo interpreta quien conduce la
prueba. Responde el agente del arnés con `tuku`. Cada turno retoma la misma
conversación (`agente.Sesion`), anota los comandos que escriben y el delta del
vault, y al cerrar deja `notas/conversation-log.md` en el vault.

El estado vive junto al vault y no dentro, así el agente no lo ve mientras
conversa.

    uv run python tests/scripts/conversar.py preparar BASE SLUG ESCENARIO
    uv run python tests/scripts/conversar.py turno VAULT --ahora "AAAA-MM-DD HH:MM" "frase"
    uv run python tests/scripts/conversar.py cerrar VAULT SLUG --titulo "..."
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import agente
import vault

ESTADO = "conversacion.json"
LOG = Path("notas") / "conversation-log.md"


def _ruta_estado(v: Path) -> Path:
    return v.parent / ESTADO


def _cargar(v: Path) -> dict[str, Any]:
    ruta = _ruta_estado(v)
    if ruta.is_file():
        return json.loads(ruta.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    return {"id": None, "ahora": None, "modelo": None, "turnos": []}


def resumir(turno: agente.Turno, delta: dict[str, str]) -> dict[str, Any]:
    """Lo que el log guarda de un turno: qué respondió, qué escribió y qué cambió."""
    escriben = [argv for argv in turno.traza if agente.escribe(argv)]
    return {
        "agente": turno.stdout.strip(),
        "escribe": [shlex.join(["tuku", *a]) for a in escriben],
        "delta": dict(sorted(delta.items())),
    }


def _quien(nombre: str, hora_iso: str | None, extra: str = "") -> str:
    """`**Nombre** (HH:MM:SS, 37 s):`, o `**Nombre:**` si el turno no trae hora."""
    if not hora_iso:
        return f"**{nombre}:**"
    return f"**{nombre}** ({hora_iso[11:19]}{extra}):"


def renderizar(estado: dict[str, Any], titulo: str) -> str:
    """El `conversation-log.md`: una nota con la conversación completa."""
    lineas = [
        "---",
        "type: Note",
        "---",
        f"# {titulo}",
        "",
        f"Reloj simulado: {estado['ahora']}. Damián lo interpreta quien conduce la prueba. "
        f"Responde el agente del arnés (`{estado['modelo']}`) con `tuku`.",
        "",
    ]
    for n, t in enumerate(estado["turnos"], start=1):
        escribe = "\n".join(f"- `{c}`" for c in t["escribe"]) or "ninguno"
        delta = "\n".join(f"- `{r}`: {c}" for r, c in t["delta"].items()) or "vacío"
        lineas += [
            f"## Turno {n}",
            "",
            f"{_quien('Damián', t.get('enviado'))} {t['damian']}",
            "",
            _quien("Agente", t.get("respondido"), f", {t.get('segundos', 0)} s"),
            "",
            *(f"> {x}".rstrip() for x in (t["agente"] or "(sin respuesta)").splitlines()),
            "",
            "**Comandos que escriben:**" + (" ninguno" if escribe == "ninguno" else ""),
            "",
            *([escribe, ""] if escribe != "ninguno" else []),
            "**Delta del vault:**" + (" vacío" if delta == "vacío" else ""),
            "",
            *([delta, ""] if delta != "vacío" else []),
        ]
    return "\n".join(lineas)


def preparar(base: Path, slug: str, escenario: str) -> Path:
    """Copia el vault de partida al banco, donde corre el agente."""
    vault.exigir_banco_limpio()
    vault.enlazar_fixtures()
    destino = vault.BANCO / slug / escenario
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    shutil.copytree(base, destino / "mi-vault")
    return destino / "mi-vault"


def turno(v: Path, frase: str, ahora: str) -> dict[str, Any]:
    estado = _cargar(v)
    sesion = agente.Sesion(estado["id"])
    antes = vault.instantanea(v)
    enviado = datetime.now()
    resultado = agente.turno(v, frase, ahora=ahora, sesion=sesion)
    respondido = datetime.now()
    registro = {
        "damian": frase,
        "enviado": enviado.isoformat(timespec="seconds"),
        "respondido": respondido.isoformat(timespec="seconds"),
        "segundos": round((respondido - enviado).total_seconds()),
        **resumir(resultado, vault.delta(antes, vault.instantanea(v))),
    }
    arnes = agente.configurado()
    estado.update(
        id=sesion.id,
        ahora=ahora,
        modelo=estado["modelo"]
        or arnes.modelo
        or agente.modelo_barato(arnes.nombre, arnes.ejecutable),
    )
    estado["turnos"].append(registro)
    _ruta_estado(v).write_text(
        json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return registro


def cerrar(v: Path, slug: str, titulo: str) -> Path | None:
    """Escribe el log en el vault y archiva el resultado en `playground/`."""
    registro = v / LOG
    registro.parent.mkdir(exist_ok=True)
    registro.write_text(renderizar(_cargar(v), titulo), encoding="utf-8")
    return vault.archivar(slug)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    sub = p.add_subparsers(dest="orden", required=True)
    a = sub.add_parser("preparar")
    a.add_argument("base", type=Path)
    a.add_argument("slug")
    a.add_argument("escenario")
    b = sub.add_parser("turno")
    b.add_argument("vault", type=Path)
    b.add_argument("--ahora", required=True)
    b.add_argument("frase")
    c = sub.add_parser("cerrar")
    c.add_argument("vault", type=Path)
    c.add_argument("slug")
    c.add_argument("--titulo", required=True)
    args = p.parse_args(argv)

    if args.orden == "preparar":
        print(preparar(args.base, args.slug, args.escenario))
    elif args.orden == "turno":
        r = turno(args.vault, args.frase, args.ahora)
        print(r["agente"])
        print("\n--- escribe:", r["escribe"] or "ninguno")
        print("--- delta:", r["delta"] or "vacío")
        if r["delta"] and not r["escribe"]:
            print("--- AVISO: el vault cambió sin un comando tuku en la traza")
    else:
        print(cerrar(args.vault, args.slug, args.titulo))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
