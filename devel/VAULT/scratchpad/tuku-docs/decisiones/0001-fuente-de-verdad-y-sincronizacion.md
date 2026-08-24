# ADR-0001 — Fuente de verdad y sincronización

- **Fecha:** 2026-08-23
- **Estado:** aceptada

## Contexto

El libro del autor vive en más de un lugar: una máquina virtual con el servidor y una máquina local. Hace falta definir qué manda y cómo se resuelven las divergencias.

## Decisión

El repositorio **Git es la fuente de verdad**. Las copias se sincronizan cada ~5 minutos con push/pull. Los conflictos los resuelve un agente aplicando la misma lógica que aplicaría el autor.

**Supuesto explícito:** existe un único escritor concurrente. La VM y la máquina local son el mismo autor en dos relojes distintos, no dos personas con intenciones distintas. Esa es la razón por la que no hace falta CRDT — es una condición de operación, no una propiedad del método.

Se distinguen dos tipos de conflicto:

| Tipo | Descripción | Frecuencia |
|---|---|---|
| Mecánico | Ediciones en líneas vecinas sin contradicción real | Alta |
| Semántico | Contradicción real sobre el mismo hecho | Baja |

El agente aporta justamente donde el merge ciego falla: en el mecánico.

## Consecuencias

- Si alguna vez escribe alguien más en el repositorio —un secretario, un socio— este ADR deja de aplicar y hace falta otro.
- El historial de Git queda disponible como insumo para reconstruir marcas de autoría.
