# tests/unitarios/

Pruebas unitarias de grano fino sobre componentes de `src/tuku/`.

## Propósito

A diferencia de [`../escenarios/`](../escenarios/README.md) (que verifica flujos de integración y evolución del vault mediante escenarios Gherkin en `playground/`), esta capa verifica:
- Funciones puras de parsing y serialización (configuración, vocabularios, fechas).
- Reglas de validación y linters en memoria.
- Estructuras de datos internas y excepciones.

Se ejecutan en milisegundos, sin efectos colaterales en disco ni dependencias externas.

**Qué prueba esta capa, ahora que el código tiene tres.** El núcleo puro es lo que se afirma acá: `entry.add`, `todo.abrir`, `note.lint`, `link.backfill`, `ahora.encabezado_de`. Los casos de uso (`add_al_vault`, `crear_con_constancia`, `abrir_en_vault`) leen y escriben archivos, así que no caben bajo la invariante de cero I/O y quedan para [`../escenarios/`](../escenarios/README.md), que además verifica sus efectos completos sobre el vault. Si una regla no se puede probar acá, casi siempre es porque está en la capa equivocada: la lógica va en el núcleo, y el caso de uso solo la conecta con el disco.

## Cómo correrlos

Se autoejecutan al correr la suite completa:

```bash
uv run pytest
```

Para correr **únicamente** los tests unitarios:

```bash
uv run pytest --unittests
# o bien:
uv run pytest tests/unitarios/
# o mediante el marcador:
uv run pytest -m unitario
```
