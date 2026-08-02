# ADR 0017 — Adopción de Pydantic v2 para modelos de datos y validación

## Contexto

TUKU procesa archivos Markdown canónicos, Front Matters en YAML y tareas posicionales. La validación de invariantes, tipos y reglas de formato (fechas ISO `YYYY-MM-DD`, franjas horarias `HH:MM-HH:MM`, esquemas de configuración `.tuku/config.yaml`) requiere garantizar rigor estricto sin añadir complejidad imperativa ni degradar el rendimiento en escaneos masivos de repositorios grandes.

Se consideran dos alternativas para la definición de estructuras internas del motor:

1. **`dataclasses` estándar de Python con código de validación manual en Python puro**:
   - Mantiene cero dependencias externas.
   - Requiere comprobaciones imperativas extensas (`isinstance`, regex repetitivos, parsing manual de errores).
   - Rendimiento sujeto a la velocidad de ejecución del intérprete Python puro.

2. **Pydantic v2 (`pydantic>=2.0`)**:
   - Modelos declarativos con validación tipada automática (`@field_validator`, coerciones de tipo, comprobación estricta de esquemas).
   - Núcleo de validación escrito en Rust (`pydantic-core`), entre 5x y 20x más rápido en deserialización/parsing masivo.
   - Mensajes de error estructurados y claros sin boilerplate.

## Decisión

**Adoptar Pydantic v2 (`pydantic>=2.0`) para la definición y validación de modelos de datos e I/O en el motor TUKU.**

- Los modelos de configuración (`ProfileConfig`), tareas (`TukuTask`), entradas (`Entry`) y estructuras de validación de invariantes se definirán utilizando `pydantic.BaseModel`.
- La validación determinista de invariantes de formato se delega a clasificadores declarativos de Pydantic, manteniendo el principio P3 (determinismo primero).

## Consecuencias

**A favor:**
- **Rendimiento superior**: Escaneo y validación de repositorios enteros acelerados por el motor en Rust de Pydantic v2.
- **Reducción de boilerplate**: Eliminación de código imperativo repetitivo de verificación de tipos y expresiones regulares manuales.
- **Claridad de errores**: Errores de parsing y esquema formateados de manera precisa para el CLI y `tuku doctor`.

**En contra:**
- Agrega una dependencia externa de producción en `pyproject.toml` (`pydantic>=2.0`), justificada por su madurez, estabilidad y beneficio directo en rendimiento y mantenibilidad.
