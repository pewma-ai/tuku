"""Motor de integración agéntica con Hermes (Fase 5).

Implementa invocación de Hermes vía subproceso (ADR 0018), construcción del
tesauro vivo acotado (F5.4), captura conversacional (F5.2) y registro canónico.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from tuku.io.entry import VALORES_CLASIFICACION_DEFAULT, Entry
from tuku.io.frontmatter import parse_frontmatter


class AgentError(Exception):
    """Error al invocar el agente o procesar su respuesta."""


# ---------------------------------------------------------------------------
# F5.4 — Tesauro vivo acotado
# ---------------------------------------------------------------------------

MAX_TESAURO_CHARS = 4000


def build_tesauro_context(profile_dir: Path) -> str:
    """Construye el contexto del tesauro vivo acotado (F5.4).

    Reúne ids de entidades vigentes, topics de notas, tipos de ciclo y
    cadencias activas en un bloque de texto acotado a MAX_TESAURO_CHARS.
    El límite garantiza que el prompt no crezca sin cota (spec §F5.4).
    """
    parts: list[str] = []

    # Entidades vigentes
    entidades_dir = profile_dir / "entidades"
    entity_ids: list[str] = []
    if entidades_dir.exists():
        for md in sorted(entidades_dir.rglob("*.md")):
            try:
                fm, _ = parse_frontmatter(md.read_text(encoding="utf-8"))
                eid = str(fm.get("id", ""))
                lifecycle = str(fm.get("lifecycle", "vigente"))
                if eid and lifecycle != "archivada":
                    entity_ids.append(eid)
            except Exception:
                pass
    if entity_ids:
        parts.append("## Entidades vigentes\n" + "\n".join(f"- {e}" for e in entity_ids))

    # Topics de notas (del índice notas.md)
    notas_index = profile_dir / "notas" / "notas.md"
    topics: list[str] = []
    if notas_index.exists():
        for line in notas_index.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^#{2,3}\s+(.+)", line)
            if m:
                topics.append(m.group(1).strip())
    if topics:
        parts.append("## Topics de notas\n" + "\n".join(f"- {t}" for t in topics))

    # Tipos de ciclo conocidos (de archivos plan_*)
    ciclos_dir = profile_dir / "ciclos"
    cycle_types: set[str] = set()
    if ciclos_dir.exists():
        for f in ciclos_dir.glob("plan_*.md"):
            try:
                fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
                ct = str(fm.get("cycle_type", ""))
                if ct:
                    cycle_types.add(ct)
            except Exception:
                pass
    if cycle_types:
        parts.append("## Tipos de ciclo\n" + "\n".join(f"- {c}" for c in sorted(cycle_types)))

    # Clasificaciones válidas
    parts.append(
        "## Clasificaciones de entradas\n"
        + "\n".join(f"- {c}" for c in sorted(VALORES_CLASIFICACION_DEFAULT))
    )

    context = "\n\n".join(parts)
    # Acotar sin cortar palabras
    if len(context) > MAX_TESAURO_CHARS:
        context = context[:MAX_TESAURO_CHARS].rsplit("\n", 1)[0] + "\n[…tesauro truncado]"
    return context


# ---------------------------------------------------------------------------
# F5.5 — Invocación de Hermes (ADR 0018)
# ---------------------------------------------------------------------------


def run_hermes(
    profile_dir: Path,
    prompt: str,
    *,
    continuar: bool = True,
    timeout: int = 120,
) -> str:
    """Invoca Hermes en modo oneshot con sesión persistente por perfil (ADR 0018).

    Usa `hermes -z <prompt> --continue` con HERMES_HOME apuntando al directorio
    `.hermes/` del perfil. `-z`/`--continue` son flags globales de Hermes (van
    antes de cualquier subcomando, no son parte de `chat`). La bandera
    `--continue` sin nombre retoma la sesión más reciente del HERMES_HOME
    activo; si no existe ninguna, crea una nueva.

    Retorna el stdout limpio de Hermes. Eleva AgentError si falla.
    """
    if shutil.which("hermes") is None:
        raise AgentError(
            "hermes no está instalado o no está en el PATH. "
            "Instala Hermes Agent o usa --sin-agente."
        )

    hermes_home = profile_dir / ".hermes"
    if not hermes_home.exists():
        raise AgentError(
            f"No se encontró {hermes_home}. Ejecuta `tuku init` en el perfil "
            "para provisionar el directorio de Hermes."
        )

    env = {**os.environ, "HERMES_HOME": str(hermes_home), "TZ": "UTC"}

    cmd = ["hermes", "-z", prompt]
    if continuar:
        cmd.append("--continue")

    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise AgentError(
            f"hermes falló (código {result.returncode}):\n{result.stderr.strip()}"
        )

    return result.stdout.strip()


# ---------------------------------------------------------------------------
# F5.2 — Captura conversacional
# ---------------------------------------------------------------------------

_HEURISTICA_TAREA = re.compile(
    r"\b(hay que|necesito|tengo que|hacer|llamar|enviar|revisar|completar|preparar"
    r"|arreglar|coordinar|conseguir|confirmar|escribir|entregar)\b",
    re.IGNORECASE,
)

_MAPA_CLASIFICACION = {
    "hito": "Hito",
    "decision": "Decisión",
    "decisión": "Decisión",
    "senal": "Señal",
    "señal": "Señal",
    "msg": "Msg",
}


def _detect_entity_refs(text: str, profile_dir: Path) -> list[tuple[str, str]]:
    """Extrae referencias [id](ruta) del texto y verifica que existen en el perfil."""
    matches = re.findall(r"\[([\w-]+)\]\(([^)]+)\)", text)
    valid: list[tuple[str, str]] = []
    entidades_dir = profile_dir / "entidades"
    for eid, epath in matches:
        # Verificación factual: el id debe existir en entidades/
        candidates = list(entidades_dir.rglob(f"{eid}.md"))
        if not candidates:
            raise AgentError(
                f"Verificación factual fallida: la entidad '{eid}' no existe "
                f"en {entidades_dir}. Revisa el id o crea la entidad primero."
            )
        valid.append((eid, epath))
    return valid


def registrar_conversacional(
    profile_dir: Path,
    texto: str,
    *,
    sin_agente: bool = True,
    fecha: str | None = None,
) -> tuple[str, str]:
    """Captura conversacional → forma canónica (F5.2).

    Convierte texto en lenguaje natural a una entrada de bitácora o tarea
    canónica. Verifica que todos los ids de entidad citados existen en el
    perfil (capa factual).

    Retorna (tipo, texto_canonico) donde tipo es 'entrada' o 'tarea'.
    """
    today = fecha or datetime.now(UTC).strftime("%Y-%m-%d")

    # Verificación factual de entidades citadas
    _detect_entity_refs(texto, profile_dir)

    if not sin_agente:
        # Modo agente: usar Hermes para parsear y normalizar
        tesauro = build_tesauro_context(profile_dir)
        prompt = (
            f"Contexto del perfil:\n{tesauro}\n\n"
            f"Fecha hoy: {today}\n\n"
            "Convierte el siguiente texto a forma canónica TUKU. "
            "Responde SOLO con la línea canónica (entrada o tarea), sin explicación.\n\n"
            f"Texto: {texto}"
        )
        respuesta = run_hermes(profile_dir, prompt)
        # Determinar tipo por el prefijo de la respuesta
        if respuesta.startswith("- [ ]") or respuesta.startswith("- [x]"):
            return "tarea", respuesta
        return "entrada", respuesta

    # Modo sin agente: heurísticas deterministas
    # Detectar clasificación por tags #
    clasificacion: str | None = None
    tags_found = re.findall(r"#([\w]+)", texto)
    for tag in tags_found:
        if tag.lower() in _MAPA_CLASIFICACION:
            clasificacion = _MAPA_CLASIFICACION[tag.lower()]
            break

    # Detectar entidad
    entity_match = re.search(r"\[([\w-]+)\]\(([^)]+)\)", texto)
    entity_id = entity_match.group(1) if entity_match else None
    entity_path = entity_match.group(2) if entity_match else None

    # Limpiar texto: remover [id](ruta) y #tags
    texto_limpio = re.sub(r"\[[\w-]+\]\([^)]+\)", "", texto)
    texto_limpio = re.sub(r"#[\w]+", "", texto_limpio).strip()
    texto_limpio = re.sub(r"\s+", " ", texto_limpio).strip()

    # Decidir si es tarea o entrada
    es_tarea = bool(_HEURISTICA_TAREA.search(texto_limpio))

    if es_tarea:
        entity_str = entity_id if entity_id else "-"
        # Generar task_id simple
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        task_id = f"reg-{ts}"
        linea = (
            f"- [ ] {today} 1h {entity_str} - - - tuku-registrar {texto_limpio} ^t-{task_id}"
        )
        return "tarea", linea

    # Es entrada
    entry = Entry(
        entity_id=entity_id,
        entity_path=entity_path,
        classification=clasificacion,
        text=texto_limpio,
    )
    return "entrada", entry.serialize()


def escribir_registro(
    profile_dir: Path,
    tipo: str,
    texto_canonico: str,
    *,
    fecha: str | None = None,
) -> Path:
    """Escribe la primitiva canónica al archivo correcto del perfil.

    Entradas → entradas/YYYY-MM.md (crea el archivo si no existe).
    Tareas → tareas/tareas.md.
    """
    today = fecha or datetime.now(UTC).strftime("%Y-%m-%d")

    if tipo == "tarea":
        target = profile_dir / "tareas" / "tareas.md"
        if not target.exists():
            target.write_text("# Backlog de Tareas\n", encoding="utf-8")
        with target.open("a", encoding="utf-8") as f:
            f.write(f"\n{texto_canonico}\n")
        return target

    # entrada
    mes = today[:7]  # YYYY-MM
    entradas_dir = profile_dir / "entradas"
    entradas_dir.mkdir(parents=True, exist_ok=True)
    target = entradas_dir / f"{mes}.md"
    if not target.exists():
        target.write_text(
            f"---\nid: entradas-{mes}\ntype: entradas\n---\n\n# Bitácora {mes}\n",
            encoding="utf-8",
        )
    with target.open("a", encoding="utf-8") as f:
        f.write(f"\n{texto_canonico}\n")
    return target
