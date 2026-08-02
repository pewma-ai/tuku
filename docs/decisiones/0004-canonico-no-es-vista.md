# ADR 0004 — Canónico ≠ vista

## Contexto

La información del sistema aparece en múltiples lugares. Las entradas de una entidad se ven
en su página, en la bitácora del ciclo y en los informes anuales. Las tareas aparecen en la
página de la entidad y en el bloque del plan. Sin una regla clara sobre qué es fuente y qué
es derivado, la información se duplica, se desincroniza y el usuario no sabe qué versión
creer.

La alternativa que este ADR descarta es la que usa el sistema MaC anterior y la mayoría de
los wikis personales: **mantener copias sincronizadas en múltiples lugares**. Tiene un
atractivo real: cada página es completa y autocontenida, el usuario no necesita entender
ningún modelo de derivación, y la lectura funciona aunque el motor esté caído.

El costo de las copias es igualmente real: la sincronización se hace a mano, la mano se
equivoca, y el resultado es dos versiones de la misma tarea con estados distintos en dos
archivos distintos. Ese es, de hecho, el fallo estructural principal que TUKU existe para
corregir: una tarea que vive duplicada en varias bitácoras y se copia manualmente.

## Decisión

**Cada dato se escribe una sola vez, en un lugar canónico. Todo lo demás es proyección
recomputable.** La proyección no se edita a mano; si se borra, se regenera sin pérdida de
información.

Los almacenes canónicos son:

- `entradas/entradas.md` — entradas de bitácora (append-only, particionado por mes)
- `tareas/tareas.md` — tareas abiertas (único archivo mutable del sistema)
- Archivos de entidad — zonas marcadas `<!-- tuku:editable -->`
- `estrategia/` — cadencias y capacidad (con gate humano para cambios)
- `notas/` — notas

Todo lo demás —bitácora de entidad, bloque de tareas del plan, dashboards de ámbito,
informes de ciclo— es proyección declarada en el grafo de derivaciones
([`docs/arquitectura.md`](../arquitectura.md) §4) y marcada `<!-- tuku:derived id=… hash=… -->`.

La bitácora del ciclo y la bitácora de una entidad son **la misma clase de objeto**: dos
filtros distintos sobre el mismo conjunto de entradas. Una filtra por rango de fechas, la
otra por pertenencia. Ninguna es un almacén.

## Consecuencias

**A favor.**

- La fuente de verdad es siempre única y localizable. El usuario sabe dónde buscar y dónde
  corregir.
- Eliminar una proyección no pierde datos: el janitor de build la regenera. Borrar
  `<!-- tuku:derived id=bitacora-entidad -->` de una página de entidad es una operación de
  limpieza, no una pérdida.
- El grafo de derivaciones es explícito y acíclico (K7, `spec/cadencia.md`): el motor sabe
  exactamente qué recomputar cuando cambia una fuente, sin escanear el perfil completo.

**En contra, y aceptado.**

- **Las proyecciones no son autocontenidas.** Una página de entidad sin motor no es completa:
  sus zonas derivadas están vacías o desfasadas. Se acepta porque la fuente cruda —las
  entradas y las tareas— es legible sin motor (P1), aunque menos conveniente.
- **El usuario puede no saber que algo es proyección** y editar dentro de una zona derivada.
  Este riesgo lo gestiona el ADR 0005 —detección por hash— sin hacer nada read-only.
- **Hay una zona de ambigüedad**: los planes del ciclo son "sembrados y luego del humano"
  (`spec/artefactos-ciclo.md` §1), lo que significa que nacen como derivados y pasan a ser
  canónicos tras la corrección humana. El mecanismo es el mismo hash; la diferencia es que
  un plan sembrado no se regenera una vez corregido (C6).

## Estado

`aceptado`
