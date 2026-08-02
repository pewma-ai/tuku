# ADR 0008 — `parent` se deriva del path, no se declara

## Contexto

Las entidades se organizan en una jerarquía: ámbito → niveles opcionales → entidad. Esta
jerarquía tiene dos representaciones posibles: como campo `parent` en el front matter de cada
archivo, o como posición en el árbol de directorios.

Declarar `parent` en el front matter tiene ventajas reales: la jerarquía es explícita aunque
el directorio esté desorganizado, se puede reflejar en cualquier visualización sin parsear
rutas, y el motor no depende de convenciones de nombrado de directorios.

## Decisión

**`parent` no se declara**. Se deriva del path: el padre de
`entidades/trabajo/log-analysis/spie2026-paper.md` es `log-analysis`, cuya página es
`entidades/trabajo/log-analysis/log-analysis.md`.

El path tiene dos funciones a la vez: namespace de navegación (para Obsidian) y declaración
de jerarquía (para el motor). Son compatibles porque la regla de derivación es trivial y
determinista.

El `id` (ADR 0001) sigue siendo independiente del path, lo que preserva la integridad de
las referencias cuando una entidad se mueve.

## Consecuencias

**A favor.**

- Elimina una fuente de desincronización: si `parent` se declarara, podría diferir del path
  real, y el motor necesitaría una regla de precedencia. Con la derivación, hay un solo lugar
  donde vive la jerarquía.
- Mover una entidad de subdirectorio cambia su padre automáticamente, sin editar front matter.
- El anidamiento de instrucciones de agente (`AGENTS.md` por nivel) funciona sin configuración
  adicional: el motor ya sabe qué nivel corresponde a cada archivo.

**En contra, y aceptado.**

- La jerarquía no es visible en el front matter: quien lea el archivo sin conocer su ruta no
  sabe dónde está en el árbol. Se mitiga porque el front matter tiene `id` y `type`, que son
  suficientes para el motor, y porque Obsidian muestra la ruta en su panel de archivos.
- Mover una entidad cambia su padre: es una operación semánticamente significativa que parece
  trivial. El motor puede advertir cuando un movimiento cambia el padre de una entidad con
  cadencias heredadas.

## Estado

`aceptado`
