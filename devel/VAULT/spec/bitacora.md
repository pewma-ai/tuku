# spec · bitácora

**La bitácora es la primitiva única.** Todo lo demás se deriva de ella.

## Naturaleza

Eventos fechados, **con hora**, inmutables. Lo que ocurrió el martes queda registrado el martes y no muta. Para enmendar, se escribe otra entrada.

La hora es obligatoria: es el dato mínimo que habilita modelos aún no imaginados —ritmos, foco, latencia entre entradas—. Sin timestamp, esos modelos son irrecuperables retroactivamente.

## Formato de viñeta

```
área: tipo — texto libre
```

`tipo` pertenece a un vocabulario cerrado y versionado, declarado en el libro de estilo del autor. Por defecto:

| Tipo | Qué registra |
|---|---|
| `señal` | Algo observado que aún no significa nada |
| `fricción` | Algo que costó más de lo que debía |
| `progreso` | Avance sobre algo en curso |
| `decisión` | Una elección tomada y su motivo |
| `nota` | Registro sin categoría más precisa |

La convención tipográfica es lo que permite extraer ámbitos, áreas y vocabulario **de forma determinista y en milisegundos**, sin inferencia y por tanto sin marca de procedencia IA.

## Partición

Un archivo por semana ISO. Un janitor concatena o corta según haga falta; la partición es detalle de implementación, no del modelo.

## Tolerancia

El parser **nunca rompe** ante un tipo de viñeta desconocido: lo tolera, lo registra y lo escala como propuesta al libro de estilo. Cuando un tipo nuevo aparece de forma repetida, un agente conversa con el autor para entender qué significa y propone la entrada correspondiente.

## Referencias

Las entradas referencian entidades con wikilinks: *hoy llamé al [[proveedor del norte]], su envío está retrasado*.

## Origen de los pendientes

Una entrada puede contener la intención de crear, avanzar o cerrar un pendiente. Ese es el único origen legítimo de un pendiente (ver `pendientes.md`).

## Redacción

El caso habitual es el **dictado**: el autor da ideas generales por texto o voz, y un agente redacta la entrada. La idea es del autor, la prosa no — y eso queda marcado (ver `corpus.md`, autoría).
