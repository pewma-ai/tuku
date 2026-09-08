# Escenario · 002-06-escribir-en-un-dia-fecha

**Cubre:** epic 002, punto 3, la razón de ser del epic: agendar es escribir donde corresponde, sin un comando aparte para fechar.

## Estado inicial

El que dejó [`002-05-cerrar-pendiente`](002-05-cerrar-pendiente.md): la tabla de pendientes vacía con su cabecera intacta.

```bash
cp -r ../../002-05-cerrar-pendiente/el-cierre-repite-el-texto-y-borra-el-item/mi-vault .
```

## Escenario: escribir un pendiente en un día futuro lo fecha

Dado el ciclo abierto del 11 al 17 de agosto, con HOY en el martes 11
Cuando se escribe el registro bajo el miércoles 12 y se abre con esa fecha

```bash
tuku entry add --vault mi-vault --dia "## Miércoles 12 de agosto" "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
tuku todo open --vault mi-vault --horizonte "con fecha" --when 2026-08-12 "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
```

Entonces la tabla de `PENDIENTES.md` gana una fila con `con fecha` y `2026-08-12`:
`| con fecha | 2026-08-12 | [[personal]] | pagar la sesión con el psicólogo |`
Y el miércoles 12 de `AHORA.md` recibe por propagación en su región del día el callout:
```markdown
> [!todo] Pendientes del día
> - [[personal]] - pagar la sesión con el psicólogo
```
Y el pendiente **no** aparece en `esta semana` ni en ningún horizonte postergado del autor

Nació con fecha exacta sin pasar por la escalera, que describe cómo se concreta lo que nació difuso y no es un camino obligatorio ([`spec/pendientes.md`](../../spec/pendientes.md)).

## Escenario: fechar mueve, nunca copia

Dado el mismo estado
Cuando se termina de escribir y propagar

```bash
tuku entry add --vault mi-vault --dia "## Miércoles 12 de agosto" "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
tuku todo open --vault mi-vault --horizonte "con fecha" --when 2026-08-12 "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
```

Entonces el pendiente está en exactamente una fila de `PENDIENTES.md`
Y `tuku todo lint` no encuentra ninguna aparición duplicada

Regla 1 de `spec/pendientes.md`, y el error que el vault real tuvo que prohibir por escrito: la misma tarea en dos filas ([`lecciones-macjpgil.md`](../../devel/lecciones-macjpgil.md), lección 7).

## Escenario: la fecha vive en la columna Cuándo

Dado que la tabla no tenía pendientes con fecha antes
Cuando nace

```bash
tuku entry add --vault mi-vault --dia "## Miércoles 12 de agosto" "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
tuku todo open --vault mi-vault --horizonte "con fecha" --when 2026-08-12 "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
```

Entonces entra como fila con columna `Cuándo` = `2026-08-12` y horizonte `con fecha`
Y no se crean callouts ni encabezados en `PENDIENTES.md`

## Escenario: el movimiento de escalón no se registra en la bitácora

Dado el ciclo abierto, antes de agendar nada
Cuando se agenda el pendiente

```bash
tuku entry add --vault mi-vault --dia "## Miércoles 12 de agosto" "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
tuku todo open --vault mi-vault --horizonte "con fecha" --when 2026-08-12 "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
```

Entonces la única línea de registro nueva es el registro `**pendiente**` que el autor escribió
Y no hay ningún registro que narre que el pendiente cambió de escalón

Mover un pendiente es un hecho del sistema, no de la vida del autor.

## Escenario: inyectar dos veces no duplica la fila ni la propagación

Dado el pendiente ya fechado y propagado

```bash
tuku entry add --vault mi-vault --dia "## Miércoles 12 de agosto" "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
tuku todo open --vault mi-vault --horizonte "con fecha" --when 2026-08-12 "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
```

Cuando se corre el comando otra vez

```bash
tuku todo open --vault mi-vault --horizonte "con fecha" --when 2026-08-12 "- 09:00 - [[personal]] **pendiente**: pagar la sesión con el psicólogo"
```

Entonces el diff es vacío
Y hay una sola fila en `PENDIENTES.md` y una sola línea propagada en el miércoles

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_06
```

Cada escenario deja su vault en `playground/002-06-escribir-en-un-dia-fecha/<escenario>/mi-vault/`.

## Qué se mira a mano

- **Abrirlo en Obsidian**, que es donde esto se verifica: el miércoles 12 muestra el pendiente en la región del día antes del primer registro.
- Que agendar se haya sentido como escribir en una agenda de papel. Si el autor tuvo que pensar en columnas o comandos especiales, el punto 3 del epic no está cumplido.

