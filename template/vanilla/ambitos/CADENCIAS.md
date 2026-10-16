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

### Historia
- Sembrada al instalar. El día que no se registra no se recupera después.

## Cierre de la semana

**Cuándo:** viernes, semanal
**Emite:** `bitacoras/bitacora-<desde>-<hasta>.md`, el ciclo cerrado

### Procedimiento
El viernes, la semana está en `bitacoras/bitacora-<desde>-<hasta>.md` y ya no se toca. `esta semana` queda vacío: lo que no se hizo está en `próxima semana`, tiene fecha, o está cerrado porque ya no importa. `tuku doctor` no reporta nada.

Un pendiente que rueda tres semanas seguidas casi nunca es un pendiente. Y lo que no quede escrito el viernes se pierde: el lunes ya no está el contexto.

### Historia
- Sembrada al instalar. Es la única cadencia sin la cual el resto del sistema se llena y no se vacía.
