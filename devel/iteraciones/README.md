# iteraciones

> Un archivo por día de trabajo. Gobernanza liviana del desarrollo de TUKU: qué se hizo y qué se decidió, para retomar sin depender de recordar la conversación.

No confundir con una bitácora de TUKU (eso sería dogfooding: mezclar el repositorio del software con un vault de autor). Esto es un changelog de decisiones, en prosa corta.

Formato de cada archivo, `AAAA-MM-DD.md`:

```markdown
# AAAA-MM-DD

## Qué se hizo
- ...

## Decisiones
- ...

## Queda pendiente
- ...
```

**Qué se hizo** carga el detalle: qué cambió, en qué archivos, con qué motivo puntual. Puede tener varias líneas por tema.

**Decisiones** es un resumen, no un segundo recuento de lo anterior. Solo lo que importa más allá del día: una regla nueva, un criterio que se fija, algo que otro día va a necesitar sin leer el detalle. Pocas líneas, aunque el día haya sido grande.

**Queda pendiente** son tareas concretas, no temas abiertos.

El estado agregado (qué epic está en curso) sigue viviendo en [`../epics.md`](../epics.md). Aquí queda el detalle día a día que esa tabla no carga.
