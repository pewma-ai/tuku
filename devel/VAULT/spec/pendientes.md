# spec · pendientes

> Este documento cubre el modelo. Las **reglas de tratamiento** de tareas —prioridad, tipos, encadenamiento, criterios de vencimiento— van en un documento aparte, aún por escribir.

## Doble fuente

| Rol | Dónde |
|---|---|
| Fuente **de origen** | La bitácora: un pendiente nace de una entrada y muere en otra |
| Fuente **operativa** | `PENDIENTES.md`: donde se consulta, se trabaja y se lee el estado |

`PENDIENTES.md` existe por dos razones concretas: no recorrer más de mil archivos para responder *qué falta*, y que alguien nuevo en el equipo entienda la situación sin leer el corpus completo.

Es un artefacto **único**: almacén deduplicado, sin copias manuales entre archivos.

## Ciclo de vida

```
entrada de bitácora (intención)  →  aparece en PENDIENTES.md
entrada de bitácora (progreso)   →  se actualiza en PENDIENTES.md
entrada de bitácora (hecho)      →  sale de PENDIENTES.md
```

Declarar un pendiente como hecho lo saca de `PENDIENTES.md` y lo deja anotado en la bitácora como hecho, con su motivo o resultado. La bitácora conserva la historia completa; `PENDIENTES.md` solo lo abierto.

**No se edita a mano.** Un janitor lo mantiene a partir de la bitácora. Si se corrompe o se borra, se reconstruye reproyectando (criterio de éxito 4).

## Temporalidad

Tres grados:

| Grado | Ejemplo |
|---|---|
| Fecha fija | *el día 5* |
| Ventana difusa | *esta semana*, *antes de que llegue el pedido* |
| Sin fecha | *cuando se pueda* |

## Emparejamiento

Reconocer que *compré la pintura* de hoy cierra *comprar pintura* de hace tres meses es coincidencia semántica, no textual. Es el **único eslabón de esta cadena que requiere un agente**; el resto es determinista.

Cuando el emparejamiento es ambiguo, el agente propone y el autor confirma con una palabra. Nunca cierra en silencio.

## Vistas

Las notas de estructura por proyecto o entidad contienen vistas filtradas sobre `PENDIENTES.md` —por ejemplo, solo los pendientes abiertos de un proyecto—. Son generadas, no curadas (ver `notas.md`).
