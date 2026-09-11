---
type: Config
---

# Bitácora

Cómo se escribe un registro. Se lee antes de la primera llamada a `tuku entry add` de la sesión, y con eso basta para todas las demás.

## Cuándo aplica

Cuando el autor cuenta algo que pasó, deja algo por hacer o da por cerrado algo que estaba pendiente. Son las tres primeras filas del `AGENTS.md` de la raíz, y entre ellas cambia la marca, no el comando.

## Le pasas los campos, no la línea

El formato lo arma el comando. El autor dice *"a las dos y veinte, hay que avisarle de los gastos comunes a la administradora"* y eso es, entero:

```
tuku entry add --day 2026-08-11 --hour 14:20 --scope personal \
  --body "**pendiente**: avisar de los gastos comunes a la administradora"
```

| Campo | Qué lleva |
| --- | --- |
| `--body` | El hecho, con su marca al principio si la lleva |
| `--scope` | El frente al que pertenece, sin corchetes |
| `--day` | El día en que ocurrió |
| `--hour` | La hora en que ocurrió |

## El día y la hora

Sin `--day` es hoy y sin `--hour` es ahora.

Si el autor nombra un día explícito ("mañana a las nueve", "el miércoles a las diez"), el registro va a ese día en `--day` y a esa hora en `--hour`.

Cuando el autor no dice el día, los registros van al ciclo abierto de `AHORA.md`: **si hoy cae fuera de ese ciclo, el día es el último del ciclo que ya tiene registros y va explícito en `--day`**. Si el ciclo todavía está vacío, es el primero. Un ciclo que quedó atrás no es motivo para cerrarlo: cerrar el ciclo está en los límites y lo decide el autor.

El último con registros, no el primero del ciclo: es hasta dónde llegó el vault, y es el único que nunca mete un hecho nuevo por delante de otros que ya estaban escritos.

Esta es la regla que más se equivoca sola. Sin ella el comando rechaza el registro, y de un rechazo es fácil concluir que hay que cerrar el ciclo, que es justo lo que no hay que hacer.

## Cuándo vence un pendiente

Si el autor dijo cuándo ("mañana", "el lunes", "antes del 20"), va en `--when` con la fecha ya resuelta.

Solo el pendiente sin fecha nace en el primer escalón de `### Horizontes`. Para mandarlo a otro escalón, `--horizon`, con el nombre tal como está escrito en `LIBRO-DE-ESTILO.md`: los escalones son del autor y puede haberlos renombrado.

## Un hecho, un comando

Una frase del autor puede dar varios registros, y cada uno es una llamada. Lo que no ocurre nunca es lo contrario: dos llamadas para un mismo hecho. `tuku entry add` deja la línea, actualiza las páginas de ámbito y aplica lo que la marca declara, todo en la misma llamada.

Registra el hecho, no la conversación: "recuérdame" y "anota" van dirigidos a ti y no son parte de lo ocurrido. El resto de cómo escribe el autor está en `LIBRO-DE-ESTILO.md`.

## A mano

Escribir la línea a mano en `AHORA.md`, bajo el encabezado del día que corresponde y en su lugar por hora:

```markdown
- 14:20 - [[personal]] **pendiente**: avisar de los gastos comunes a la administradora
```

Si lleva `**pendiente**`, agregar además una fila en la tabla de `PENDIENTES.md` con el mismo cuerpo, carácter por carácter, y su horizonte. Si lleva `~~(Hecho)~~`, buscar esa fila y marcarla cerrada.
