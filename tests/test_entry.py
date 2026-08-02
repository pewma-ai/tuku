"""Pruebas del parser y serializador de entradas de bitácora (F1.3).

Verifica el parsing y round-trip de la gramática de entradas acorde a `spec/entradas.md` §3.
"""

from tuku.io.entry import Entry


def test_roundtrip_entrada_completa() -> None:
    """F1.3: Round-trip con hora, enlace a entidad, clasificación y #marcadores."""
    line = (
        "- (09:30) [sw-responsible](../entidades/trabajo/sw-responsible.md) "
        "**Hito:** Instalación validada #urgente"
    )
    entry = Entry.parse_line(line)
    assert entry.time == "09:30"
    assert entry.entity_id == "sw-responsible"
    assert entry.entity_path == "../entidades/trabajo/sw-responsible.md"
    assert entry.classification == "Hito"
    assert entry.text == "Instalación validada"
    assert entry.tags == ["urgente"]

    serialized = entry.serialize()
    assert serialized == line


def test_entrada_sin_entidad_ni_hora() -> None:
    """F1.3: Gramática con omisión de componentes opcionales (hora/entidad)."""
    line = "- **Señal:** Desconexión recomendada"
    entry = Entry.parse_line(line)
    assert entry.time is None
    assert entry.entity_id is None
    assert entry.classification == "Señal"
    assert entry.text == "Desconexión recomendada"
