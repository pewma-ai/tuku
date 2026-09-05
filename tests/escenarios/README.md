# tests/escenarios

Un escenario es una historia en formato Dado/Cuando/Entonces con su arnés al lado: `001-001-instalacion-minima.md` es el caso, `test_001_001_instalacion_minima.py` lo ejecuta.

Son narrativos y no unitarios porque buena parte de TUKU depende de un agente y no da un resultado único. Lo que se puede verificar con un `assert` vive en el `.py`; lo que solo se puede juzgar leyendo el resultado queda escrito en el `.md` bajo "Qué se mira a mano", y no se finge que un test lo cubre.

Un escenario referencia `spec/` pero no lo reemplaza. Si un escenario contradice `spec/`, se corrige `spec/` (ver [`../../devel/epics.md`](../../devel/epics.md), "los epics mueven el diseño"), no el escenario.

Lo que una corrida produce va a `playground/`, que se pisa cada vez que se vuelve a correr.

No hay problema en que esto crezca a cientos de archivos chicos: son texto, cuestan casi nada.

Esta suite se escribe desde cero. No reutiliza los tests del diseño anterior, que documenta [`../README.md`](../README.md).

## Convención de nombre

`XXX-YYY-slug`, donde `XXX` es el epic al que pertenece el escenario y `YYY` su orden dentro de ese epic, ambos con tres dígitos. Así `001-002-instalacion-local` es el segundo escenario del epic 001.

Tres dígitos y no dos por una razón sola: que ordenar alfabéticamente sea ordenar de verdad, hoy y con cien escenarios. El número dice de dónde salió el escenario, no en qué orden conviene leerlo, así que no se renumera cuando cambia el orden de trabajo.

El mismo par nombra las tres cosas: el caso (`XXX-YYY-slug.md`), el arnés (`test_XXX_YYY_slug.py`, con guiones bajos porque es un módulo de Python) y la corrida desechable (`playground/XXX-YYY-slug/`).

## Fixtures

`fixtures/XXX-YYY-slug/`, con guiones, porque es un directorio de datos y no un módulo.

Un fixture guarda solo lo que el mecanismo bajo prueba transforma. Lo que se copia sin tocar se compara en vivo contra su origen: congelar una copia paralela de algo que nunca debería diferir obliga a regenerarla a mano cada vez que cambia el original. Por eso el fixture de `001-001` es un solo archivo (`AHORA.md`, el único que `instalar()` sustituye) y el resto del árbol se compara contra `template/vanilla/` directamente.

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
