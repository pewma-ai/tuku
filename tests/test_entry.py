"""Pruebas del parser/serializador de entradas (F1.3)."""

from tuku.io.entry import Entry


def test_roundtrip_entrada_completa() -> None:
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
    line = "- **Señal:** Desconexión recomendada"
    entry = Entry.parse_line(line)
    assert entry.time is None
    assert entry.entity_id is None
    assert entry.classification == "Señal"
    assert entry.text == "Desconexión recomendada"
