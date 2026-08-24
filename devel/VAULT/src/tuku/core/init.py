"""Inicialización y siembra de perfiles TUKU.

Implementa `tuku init` acorde a `docs/arquitectura.md` §2 y ADR 0015.
ADR 0018: provisiona `.hermes/` por perfil si Hermes está instalado.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_GITIGNORE = """# TUKU runtime logs y caches (ADR 0015)
tuku.log
.tuku/cache/

# Hermes Agent — estado del perfil agéntico (ADR 0018, nunca versionar)
.hermes/
"""

DEFAULT_CONFIG_YAML = """# Configuración del perfil TUKU (spec/perfil.md)
schema_version: 0
profile_name: "personal"

clasificaciones:
  - hito
  - decision
  - senal
  - msg

task_archive_delay: 7d

derivations:
  - target: "ciclos/plan_{fecha}_{tipo}.md#tareas-del-ciclo"
    sources: ["tareas/tareas.md", "estrategia/cadencias.md"]
    build: "tareas_del_ciclo"

  - target: "entidades/{ruta}/{entidad}.md#bitacora-entidad"
    sources: ["entradas/entradas.md"]
    filter: "entidad == {entidad}"
    build: "proyeccion_entidad"

  - target: "notas/notas.md"
    sources: ["notas/**/*.md"]
    build: "indice_notas"
"""

DEFAULT_ENTRADAS_MD = """---
id: entradas
type: entradas
---

# Bitácora Activa
"""

DEFAULT_TAREAS_MD = """---
id: tareas
type: tareas
---

# Backlog de Tareas
"""

DEFAULT_CAPACIDAD_MD = """---
id: capacidad
type: capacidad
notify_window: "07:00-14:00"
timezone: America/Santiago
---

# Capacidad y Restricciones
"""

DEFAULT_CADENCIAS_MD = """# Cadencias de Estrategia

<!-- tuku:cadencias
- id: cad-cierre-semana
  trigger: { type: calendar, rule: "weekly:FRI" }
  emit: { kind: ciclo, cycle_type: semana }
-->
"""

DEFAULT_NOTAS_INDICE_MD = """---
id: indice-notas
type: indice
---

# Índice de Notas

<!-- tuku:derived id=indice-notas hash=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934 -->
*Sin notas registradas.*
<!-- /tuku:derived -->
"""

DEFAULT_NOTAS_AGENTS_MD = """# Instrucciones del eje deliberativo (notas/)

- Las notas son piezas del eje deliberativo; se corrigen editando (`spec/nota.md`).
- `summary` es obligatorio. Si la nota es un stub, `summary: ""`.
"""

DEFAULT_RAIZ_AGENTS_MD = """# TUKU Agent Instructions

Este repositorio es un perfil de TUKU (Management as Code).
Consulte `docs/` y `spec/` para el contrato de operabilidad.
"""


# Configuración mínima de Hermes para el perfil TUKU (ADR 0018)
_HERMES_CONFIG_PERFIL = """\
# Hermes Agent — config mínima del perfil TUKU (ADR 0018)
# No editar a mano: gestionado por tuku init/sync.
model:
  default: deepseek-v4-flash
  provider: opencode-go
  show_reasoning: false
  thinking: false

tts:
  enabled: false

stt:
  enabled: false
"""


def _provisionar_hermes(target_dir: Path) -> bool:
    """Crea .hermes/ en el perfil con symlinks a credenciales del sistema (ADR 0018).

    Retorna True si se provisionó, False si ~/.hermes no existe o hubo error.
    La operación es idempotente: si .hermes/ ya existe, solo actualiza el config.
    """
    sistema_home = Path.home() / ".hermes"
    if not sistema_home.exists():
        return False

    hermes_dir = target_dir / ".hermes"
    hermes_dir.mkdir(exist_ok=True)

    # Symlinks a credenciales — nunca se copian, solo se enlazan
    for cred_file in [".env", "auth.json"]:
        src = sistema_home / cred_file
        dst = hermes_dir / cred_file
        if src.exists() and not dst.exists():
            dst.symlink_to(src)

    # Config mínima (siempre se escribe para mantenerla actualizada)
    (hermes_dir / "config.yaml").write_text(_HERMES_CONFIG_PERFIL, encoding="utf-8")

    return True


def init_perfil(target_dir: Path) -> Path:
    """Siembra el árbol de directorios y archivos iniciales de un perfil TUKU.

    Si ~/.hermes existe, provisiona .hermes/ en el perfil con symlinks a
    credenciales y config mínima (ADR 0018). La ausencia de Hermes no es error.

    Retorna la ruta absoluta del perfil inicializado.
    """
    target_dir = target_dir.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    # Directorios canónicos
    dirs = [
        target_dir / ".tuku",
        target_dir / ".tuku" / "cache",
        target_dir / ".tuku" / "procesos",
        target_dir / "entradas",
        target_dir / "tareas",
        target_dir / "ciclos",
        target_dir / "entidades" / "personal",
        target_dir / "tipos",
        target_dir / "estrategia",
        target_dir / "notas",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Archivos iniciales (sembrados si no existen)
    archivos = [
        (target_dir / ".gitignore", DEFAULT_GITIGNORE),
        (target_dir / ".tuku" / "config.yaml", DEFAULT_CONFIG_YAML),
        (target_dir / "AGENTS.md", DEFAULT_RAIZ_AGENTS_MD),
        (target_dir / "entradas" / "entradas.md", DEFAULT_ENTRADAS_MD),
        (target_dir / "tareas" / "tareas.md", DEFAULT_TAREAS_MD),
        (target_dir / "estrategia" / "capacidad.md", DEFAULT_CAPACIDAD_MD),
        (target_dir / "estrategia" / "cadencias.md", DEFAULT_CADENCIAS_MD),
        (target_dir / "notas" / "notas.md", DEFAULT_NOTAS_INDICE_MD),
        (target_dir / "notas" / "AGENTS.md", DEFAULT_NOTAS_AGENTS_MD),
    ]

    for path, content in archivos:
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    # ADR 0018: provisionar Hermes por perfil si está instalado
    _provisionar_hermes(target_dir)

    return target_dir
