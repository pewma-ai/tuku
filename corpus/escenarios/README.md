# corpus/escenarios

> Casos narrativos, no unitarios. TUKU se prueba mal con `assert x == y` porque buena parte de lo interesante depende de un agente y de una persona; se prueba mejor contando una historia y revisando si el resultado la sostiene.

Un escenario es un archivo por historia, en formato Dado/Cuando/Entonces. Es dato de prueba, no diseño: referencia `spec/` pero no lo reemplaza. Si un escenario contradice `spec/`, se corrige `spec/` (ver `../../devel/epics.md`, "los epics mueven el diseño"), no el escenario.

Lo que ejecuta un escenario, y lo que esa ejecución produce, va en `playground/`, que se pisa cada vez que se vuelve a correr. El arnés que eventualmente los automatiza vive en `../../tests/escenarios/` y `../../tests/scripts/`.

No hay problema en que esto crezca a cientos de archivos chicos: son texto, cuestan casi nada.

## Convención de nombre

`XXX-YYY-slug.md`, donde `XXX` es el epic al que pertenece el escenario y `YYY` su orden dentro de ese epic, ambos con tres dígitos. Así `001-002-instalacion-local.md` es el segundo escenario del epic 001.

Tres dígitos y no dos por una razón sola: que ordenar alfabéticamente sea ordenar de verdad, hoy y con cien escenarios. El número dice de dónde salió el escenario, no en qué orden conviene leerlo, así que no se renumera cuando cambia el orden de trabajo.

El mismo par `XXX-YYY` identifica al test que lo automatiza (`../../tests/escenarios/test_XXX_YYY_slug.py`) y a la corrida desechable (`playground/XXX-YYY-slug/`).

## Convención de formato

```markdown
# Escenario · <nombre>

**Cubre:** qué fase o epic valida.

## Escenario: <lo que se está probando>

Dado <estado inicial>
Cuando <la acción>
Entonces <lo que debería ser cierto>

## Cómo se corre

Comando para reproducirlo en `playground/`.

## Qué se mira a mano

Lo que ningún script puede verificar todavía, y hay que juzgar leyendo el resultado.
```

## Índice

| Escenario | Cubre | Notas |
| --- | --- | --- |
| [`001-001-instalacion-minima.md`](001-001-instalacion-minima.md) | Epic 001, fase 0 | El camino completo: `curl` contra GitHub |
| [`001-002-instalacion-local.md`](001-002-instalacion-local.md) | Epic 001, fase 0 | El mismo mecanismo, sin red ni git, para iterar rápido |
