# corpus/escenarios

> Casos narrativos, no unitarios. TUKU se prueba mal con `assert x == y` porque buena parte de lo interesante depende de un agente y de una persona; se prueba mejor contando una historia y revisando si el resultado la sostiene.

Un escenario es un archivo por historia, en formato Dado/Cuando/Entonces. Es dato de prueba, no diseño: referencia `spec/` pero no lo reemplaza. Si un escenario contradice `spec/`, se corrige `spec/` (ver `../../devel/epics.md`, "los epics mueven el diseño"), no el escenario.

Lo que ejecuta un escenario, y lo que esa ejecución produce, va en `playground/`, que se pisa cada vez que se vuelve a correr. El arnés que eventualmente los automatiza vive en `../../tests/escenarios/` y `../../tests/scripts/`.

No hay problema en que esto crezca a cientos de archivos chicos: son texto, cuestan casi nada.

## Convención

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
| [`instalacion-minima.md`](instalacion-minima.md) | Epic 1, fase 0 | El camino completo: `curl` contra GitHub |
| [`instalacion-local.md`](instalacion-local.md) | Epic 1, fase 0 | El mismo mecanismo, sin red ni git, para iterar rápido |
