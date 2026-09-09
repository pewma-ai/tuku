---
type: Cadence
---

# Cadencias del ciclo

Abrir y cerrar la semana. Si tu ritmo no es de lunes a viernes más un fin de semana, cambia el `Cuándo` más abajo.


> [!info] Ver cómo se escribe una cadencia en el [LIBRO DE ESTILO](../LIBRO-DE-ESTILO.md#Cadencias).

## Apertura de la semana

**Cuándo:** lunes, semanal
**Emite:** `AHORA.md`, el ciclo en curso

### Procedimiento
El lunes, `AHORA.md` tiene su frontmatter con las fechas del ciclo y los días vacíos. La tabla de `PENDIENTES.md` tiene bajo `esta semana` lo comprometido para estos días y nada más.

Después cada día tiene sus registros en orden de hora. Llenarlo no es una cadencia, es el uso normal del sistema.

> [!NOTE] Comandos
> `tuku cycle open`
>
> Abre el ciclo o verifica el que ya está abierto. Es idempotente: correrlo dos veces no duplica nada. Con `--fecha` abre un ciclo que no empieza hoy.
>
> `tuku entry add "- HH:MM - [[ambito]] **clasificacion**: cuerpo"`
> `tuku todo open "<la línea del registro>" --horizonte "esta semana"`
> `tuku todo close "<la línea del registro>"`
>
> El primero escribe el registro en el día que corresponde. Los otros dos aplican su consecuencia sobre `PENDIENTES.md`, siempre después de que la línea ya esté escrita.

### Historia
- Sembrada al instalar. El día que no se registra no se recupera después.

## Cierre de la semana

**Cuándo:** viernes, semanal
**Emite:** `bitacoras/bitacora-<desde>-<hasta>.md`, el ciclo cerrado

### Procedimiento
El viernes, la semana está en `bitacoras/bitacora-<desde>-<hasta>.md` y ya no se toca. `esta-semana` queda vacío: lo que no se hizo está en `proxima-semana`, tiene fecha, o está cerrado porque ya no importa. Los tres `lint` no reportan nada.

Un pendiente que rueda tres semanas seguidas casi nunca es un pendiente. Y lo que no quede escrito el viernes se pierde: el lunes ya no está el contexto.

> [!NOTE] Comandos
> `tuku todo propagate`
> `tuku cycle lint`
> `tuku todo lint`
> `tuku entry lint`
>
> El primero regenera la vista de cada día desde `PENDIENTES.md`. Los tres `lint` revisan y reportan, no escriben: `cycle` la estructura del archivo, `todo` los pendientes, `entry` los registros. Lo que salga se arregla antes de archivar.

### Historia
- Sembrada al instalar. Es la única cadencia sin la cual el resto del sistema se llena y no se vacía.
