# playground

Corridas desechables. Nada de acá se versiona (salvo este archivo) y todo se pisa al volver a correr el escenario que lo produjo.

Un directorio por escenario, con **el mismo nombre del escenario** que lo generó: `XXX-YYY-slug/`, igual que `../corpus/escenarios/XXX-YYY-slug.md`. Así el resultado dice de qué caso salió, y volver a correrlo sobrescribe el anterior en vez de acumular carpetas.

No se numeran los intentos. Si hace falta comparar dos corridas, se copian a mano a otro lado; el nombre del escenario no cambia.
