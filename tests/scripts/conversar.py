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
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import agente
import vault

ESTADO = "conversacion.json"
TRAZAS = "trazas"
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


def registro(
    frase: str,
    turno: agente.Turno,
    delta: dict[str, str],
    enviado: datetime,
    respondido: datetime,
) -> dict[str, Any]:
    """Un turno para el log: lo que dijo el autor, cuándo, y lo que `resumir` guarda."""
    return {
        "damian": frase,
        "enviado": enviado.isoformat(timespec="seconds"),
        "respondido": respondido.isoformat(timespec="seconds"),
        "segundos": round((respondido - enviado).total_seconds()),
        "codigo": turno.codigo,
        **resumir(turno, delta),
    }


def _sin_links(texto: str) -> str:
    """El texto con sus links vueltos literales.

    La respuesta del agente cita links relativos a la raíz del vault, y desde
    `notas/` no resuelven: el doctor los marcaría como rotos.
    """
    return texto.replace("](", "]\\(").replace("[[", "[\\[")


def _callout(
    tipo: str, nombre: str, hora_iso: str | None, texto: str, extra: str = ""
) -> list[str]:
    """`> [!tipo] Nombre (HH:MM:SS, 37 s)` y debajo el texto citado."""
    titulo = f"{nombre} ({hora_iso[11:19]}{extra})" if hora_iso else nombre
    return [f"> [!{tipo}] {titulo}", *(f"> {x}".rstrip() for x in texto.splitlines())]


def renderizar(estado: dict[str, Any], titulo: str) -> str:
    """El `conversation-log.md`: una nota con la conversación completa."""
    autor = estado.get("autor", "Damián")
    presenta = estado.get("presenta", "Damián lo interpreta quien conduce la prueba.")
    reloj = f"Reloj simulado: {estado['ahora']}. " if estado.get("ahora") else ""
    lineas = [
        "---",
        "type: Note",
        "---",
        f"# {titulo}",
        "",
        f"{reloj}{presenta} Responde el agente del arnés (`{estado['modelo']}`) con `tuku`.",
        "",
    ]
    for n, t in enumerate(estado["turnos"], start=1):
        escribe = "\n".join(f"- `{c}`" for c in t["escribe"]) or "ninguno"
        delta = "\n".join(f"- `{r}`: {c}" for r, c in t["delta"].items()) or "vacío"
        lineas += [
            f"## Turno {n}",
            "",
            *_callout("question", autor, t.get("enviado"), t["damian"]),
            "",
            *_callout(
                "info",
                "Agente",
                t.get("respondido"),
                _sin_links(t["agente"] or "(sin respuesta)"),
                f", {t.get('segundos', 0)} s",
            ),
            "",
            "**Comandos que escriben:**" + (" ninguno" if escribe == "ninguno" else ""),
            "",
            *([escribe, ""] if escribe != "ninguno" else []),
            "**Delta del vault:**" + (" vacío" if delta == "vacío" else ""),
            "",
            *([delta, ""] if delta != "vacío" else []),
            *(
                ["**Salió del vault:**", "", *(f"- `{f}`" for f in t["fuera"]), ""]
                if t.get("fuera")
                else []
            ),
        ]
    # Toda nota cierra con `## Ver además` (`tuku doctor note` lo exige); el log no enlaza.
    lineas += ["## Ver además", ""]
    return "\n".join(lineas)


def escribir_log(v: Path, estado: dict[str, Any], titulo: str) -> Path:
    """Deja el `conversation-log.md` en `notas/` del vault `v`."""
    ruta = v / LOG
    ruta.parent.mkdir(exist_ok=True)
    ruta.write_text(renderizar(estado, titulo), encoding="utf-8")
    return ruta


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


def dejar_traza(v: Path, numero: int, resultado: agente.Turno) -> None:
    """Deja junto al vault lo que el arnés devolvió, sin filtrar, y los pasos que dio.

    Va fuera del vault, en `trazas/turno-NN.jsonl` y `.txt`: es la evidencia para
    ver en qué se fue el tiempo de un turno y qué leyó el agente antes de escribir.
    """
    carpeta = v.parent / TRAZAS
    carpeta.mkdir(exist_ok=True)
    (carpeta / f"turno-{numero:02d}.jsonl").write_text(resultado.crudo, encoding="utf-8")
    if resultado.conversacion.strip():
        (carpeta / f"turno-{numero:02d}.txt").write_text(
            resultado.conversacion.strip() + "\n", encoding="utf-8"
        )


def turno(
    v: Path,
    frase: str,
    ahora: str,
    en_vivo: Callable[[str], None] | None = None,
    en_error: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    estado = _cargar(v)
    sesion = agente.Sesion(estado["id"])
    antes = vault.instantanea(v)
    enviado = datetime.now()
    resultado = agente.turno(
        v, frase, ahora=ahora, sesion=sesion, en_vivo=en_vivo, en_error=en_error
    )
    respondido = datetime.now()
    turno_registrado = registro(
        frase, resultado, vault.delta(antes, vault.instantanea(v)), enviado, respondido
    )
    turno_registrado["fuera"] = agente.fuera_del_vault(resultado.crudo, v)
    arnes = agente.configurado()
    estado.update(
        id=sesion.id,
        ahora=ahora,
        modelo=estado["modelo"]
        or arnes.modelo
        or agente.modelo_barato(arnes.nombre, arnes.ejecutable),
    )
    dejar_traza(v, len(estado["turnos"]) + 1, resultado)
    estado["turnos"].append(turno_registrado)
    _ruta_estado(v).write_text(
        json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return turno_registrado


def cerrar(v: Path, slug: str, titulo: str) -> Path | None:
    """Escribe el log en el vault y archiva el resultado en `playground/`."""
    escribir_log(v, _cargar(v), titulo)
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
