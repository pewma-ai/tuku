---
type: Config
---

# Bitácora

Cómo se escribe un registro. Se lee antes de la primera llamada de la sesión a `tuku entry add`, `tuku todo open` o `tuku todo close`, y con eso basta para todas las demás.

## Cuándo aplica

Cuando el autor cuenta algo que pasó (`tuku entry add`), deja algo por hacer (`tuku todo open`) o da por cerrado algo que estaba pendiente (`tuku todo close`). Son las tres primeras filas del `AGENTS.md` de la raíz, y los tres reciben los mismos campos. `tuku entry add` rechaza `**pendiente**` y `(Hecho)` y nombra el comando que corresponde.

## Le pasas los campos, no la línea

El formato lo arma el comando. El autor dice *"a las dos y veinte, hay que avisarle de los gastos comunes a la administradora"* y eso es, entero:

```
tuku todo open --day 2026-08-11 --hour 14:20 --scope personal \
  --body "avisar de los gastos comunes a la administradora"
```

| Campo | Qué lleva |
| --- | --- |
| `--body` | El hecho. En `tuku entry add`, con su clasificación al principio si la lleva; en `tuku todo open` y `tuku todo close`, solo el cuerpo: la marca la pone el comando |
| `--scope` | El frente al que pertenece, sin corchetes |
| `--day` | El día en que ocurrió, o en que se prometió si es un pendiente |
| `--hour` | La hora en que ocurrió, o en que se prometió |
| `--due` | Solo en `tuku todo open`: el día en que vence |

## El día y la hora

Sin `--day` es hoy y sin `--hour` es ahora.

Si el autor cuenta algo de otro día ("ayer a las nueve", "el lunes a las diez"), el registro va a ese día en `--day` y a esa hora en `--hour`. Un día que todavía no llega no es un `--day`: es el vencimiento de un pendiente.

Cuando el autor no dice el día, los registros van al ciclo abierto de `AHORA.md`: **si hoy cae fuera de ese ciclo, el día es el último del ciclo que ya tiene registros y va explícito en `--day`**. Si el ciclo todavía está vacío, es el primero. Un ciclo que quedó atrás no es motivo para cerrarlo: cerrar el ciclo está en los límites y lo decide el autor.

El último con registros, no el primero del ciclo: es hasta dónde llegó el vault, y es el único que nunca mete un hecho nuevo por delante de otros que ya estaban escritos.

Esta es la regla que más se equivoca sola. Sin ella el comando rechaza el registro, y de un rechazo es fácil concluir que hay que cerrar el ciclo, que es justo lo que no hay que hacer.

## Cuándo vence un pendiente

Si el autor dijo para cuándo ("mañana", "el lunes", "antes del 20"), va en `--due` con la fecha ya resuelta. El registro queda hoy y ahora, que es cuándo se prometió, y el pendiente aparece en su día de `AHORA.md`.

Sin `--due`, el pendiente nace en el primer escalón de `### Horizontes`. Para mandarlo a otro escalón, `--horizon`, con el nombre tal como está escrito en `LIBRO-DE-ESTILO.md`: los escalones son del autor y puede haberlos renombrado. `--due` y `--horizon` no van juntos.

## Un hecho, un comando

Una frase del autor puede dar varios registros, y cada uno es una llamada. Lo que no ocurre nunca es lo contrario: dos llamadas para un mismo hecho. Cada comando deja la línea y actualiza las páginas de ámbito; `tuku todo open` y `tuku todo close` además abren o cierran la fila de `PENDIENTES.md`, todo en la misma llamada.

Registra el hecho, no la conversación: "recuérdame" y "anota" van dirigidos a ti y no son parte de lo ocurrido. El resto de cómo escribe el autor está en `LIBRO-DE-ESTILO.md`.

## A mano

Escribir la línea a mano en `AHORA.md`, bajo el encabezado del día que corresponde y en su lugar por hora:

```markdown
- 14:20 - [personal](ambitos/personal/personal.md) **pendiente**: avisar de los gastos comunes a la administradora
```

Si lleva `**pendiente**`, agregar además una fila en la tabla de `PENDIENTES.md` con el mismo cuerpo, carácter por carácter, y su horizonte. Si lleva `(Hecho)`, buscar esa fila, sin contar los links, y quitarla; en el registro, la marca va a la vista y el cuerpo tachado: `(Hecho): ~~cuerpo~~`. Si el pendiente se abrió ese mismo día, borrar también el registro que lo abrió: queda solo el cierre.
