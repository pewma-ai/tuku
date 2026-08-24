# ADR 0006 — La regla muere con su portador; lo emitido sobrevive siempre

## Contexto

Una cadencia puede existir en tres lugares: en el sistema, en un tipo de entidad, en una
entidad concreta. Cuando su portador desaparece —se borra un tipo, se archiva o elimina una
entidad—, hay dos comportamientos posibles para los artefactos que esa cadencia ya emitió.

La alternativa obvia es consistencia total: si la regla ya no existe, sus consecuencias
tampoco. Borrar el tipo `cliente` eliminaría todas las tareas de reposición pendientes, lo
que da un perfil limpio y sin referencias colgantes.

Su atractivo es real: un backlog sin tareas huérfanas es más fácil de auditar y de
comprender. La trazabilidad es perfecta en todo momento.

## Decisión

Una cadencia es una regla y tiene el ciclo de vida de su portador. Una tarea emitida es un
objeto canónico independiente. **La tarea emitida sobrevive siempre** a la desaparición de
su origen.

Cuando la cadencia o su portador desaparecen:

- La cadencia deja de emitir nuevas tareas.
- Las tareas ya emitidas permanecen en `tareas/tareas.md` con `origin` colgante.
- Una referencia `origin` que ya no resuelve **no es una violación de invariante** (K7 de
  `spec/cadencia.md`).

El campo `origin` es una referencia blanda: el motor pierde la capacidad de explicar por
qué existe la tarea, pero la tarea sigue siendo válida y accionable.

`tuku doctor` puede listar las tareas con `origin` colgante como información de diagnóstico,
no como error.

## Consecuencias

**A favor.**

- Borrar un tipo, un área o una entidad nunca elimina compromisos en silencio. En un sistema
  cuya promesa es recordar, ese es el peor fallo posible.
- La operación de borrado es barata: se borra el archivo y el resto del sistema sigue
  funcionando. No hace falta una transacción global que resuelva todas las dependencias.
- El usuario puede revisar las tareas huérfanas y decidir qué hacer con cada una: cerrarlas,
  cancelarlas, reasignarlas. La decisión queda en manos humanas.

**En contra, y aceptado.**

- El backlog puede tener tareas cuyo origen ya no existe y cuya razón de ser es oscura.
  `tuku doctor` y el RADAR pueden surfacearlas periódicamente para que no queden enterradas.
- La referencia colgante no se puede limpiar automáticamente sin decisión humana, lo que
  significa que el backlog puede acumular ruido con el tiempo si nadie hace mantenimiento.

## Estado

`aceptado`
