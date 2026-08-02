# Decisiones de arquitectura (ADR)

> `docs/decisiones/README.md` · Índice del historial de decisiones cerradas. Cómo se escribe
> un ADR: [`INSTRUCCIONES.md`](INSTRUCCIONES.md). El porqué general vive en
> [`../brief.md`](../brief.md) y [`../principios.md`](../principios.md); el qué exacto de
> cada formato, en [`../../spec/`](../../spec/).

---

| # | Decisión | Cierra la alternativa | Estado |
|---|---|---|---|
| [0001](0001-id-estable.md) | Identidad estable independiente del path | Identidad por path, con un janitor que reescribe las referencias en cada movimiento | `aceptado` |
| [0002](0002-motor-fuera-del-perfil.md) | El motor nunca se vendoriza en el perfil | Copiar el código dentro del repositorio de datos para reproducibilidad y descubribilidad | `aceptado` |
| [0003](0003-version-de-esquema.md) | Versionado de esquema y migraciones | No versionar; versionar por versión del motor; migrar implícitamente al vuelo | `aceptado` |

**0002 obliga a 0003**: si el motor evoluciona por separado de los datos, el contrato entre
ambos tiene que estar versionado explícitamente.
