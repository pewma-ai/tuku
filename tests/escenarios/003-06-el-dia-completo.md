# 003-06 · El día completo

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Brief:** [La jornada de trabajo](../../docs/brief.md#L15) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md)

Dictado íntegro de la jornada en lenguaje natural. El agente compila la secuencia a comandos deterministas del CLI, alcanzando un estado del vault equivalente al generado a mano en el [Epic 002](002-00-el-dia-uno-a-mano.md).

## Estado inicial

```bash
tuku init mi-vault --date 2026-08-11
```

## Escenario: el día dictado entero deja el vault del epic 002

Dado un vault sembrado y vacío de registros
Cuando el autor le cuenta el día completo al finalizar la jornada
```agente
A las nueve y doce me di cuenta de que la administradora responde los mensajes con varios días de atraso.
A las once y media hice la consulta presencial por el standing desk.
A las doce y cinco ordené los cables del escritorio.
A la una, tengo que comprar una maleta.
A las dos y veinte, hay que avisarle de los gastos comunes a la administradora.
A las seis cuarenta le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp.
A las siete y cinco, listo lo de avisarle de los gastos comunes a la administradora.
A las siete y diez ya compré la maleta.
El depto centro es un frente aparte, ábrelo.
A las nueve y cuarto de la noche guárdame una nota sobre cómo funciona el cobro de gastos comunes en una copropiedad, que es del depto centro.
Mañana a las nueve tengo que pagar la sesión con el psicólogo.
```
Entonces el dictado se traduce en once comandos y ninguno más
```text
tuku entry add --day 2026-08-11 --hour 09:12 --scope personal --body "..."   ×8
tuku scope create depto-centro
tuku note create "<el título>" --scope depto-centro --day 2026-08-11 --hour 21:15
tuku entry add --day 2026-08-12 --hour 09:00 --scope personal --body "**pendiente**: ..."
```
Y cada registro del martes 11 tiene su hora, su ámbito y su marca según la tabla de verdad
Y el cuerpo del registro de las 18:40 enlaza a `depto-centro` de forma retroactiva
Y `PENDIENTES.md` queda con una sola fila correspondiente a la sesión con el psicólogo
Y el miércoles 12 abre con la llamada de pendientes del día
Y existe la nota en `notas/` enlazada desde el registro de las 21:15
Y no aparecen instrucciones ni frases espurias en `AHORA.md`
Y `tuku doctor` confirma la coherencia total del vault

### Tabla de verdad

| Hora | Día | Ámbito | Marca | Qué deja |
| --- | --- | --- | --- | --- |
| 09:12 | martes 11 | `personal` | ninguna | constancia simple |
| 11:30 | martes 11 | `personal` | ninguna | constancia simple |
| 12:05 | martes 11 | `personal` | ninguna | constancia simple |
| 13:00 | martes 11 | `personal` | `**pendiente**` | abre compra de maleta |
| 14:20 | martes 11 | `personal` | `**pendiente**` | abre aviso a administradora |
| 18:40 | martes 11 | `personal` | ninguna | mención retroactiva de `depto-centro` |
| 19:05 | martes 11 | `personal` | `~~(Hecho)~~` | cierra aviso de las 14:20 |
| 19:10 | martes 11 | `personal` | `~~(Hecho)~~` | cierra compra de las 13:00 |
| 21:15 | martes 11 | `depto-centro` | ninguna | constancia de nota creada |
| 09:00 | miércoles 12 | `personal` | `**pendiente**` | compromiso para 2026-08-12 |

## Aceptación humana (en Obsidian)

- Los once hechos se integran con naturalidad entre el martes 11 y el miércoles 12 en `AHORA.md`.
- `PENDIENTES.md` mantiene únicamente el compromiso activo del miércoles 12 tras el ciclo completo de apertura y cierre.
- La nota de copropiedad en `notas/` y el ámbito `depto-centro` quedan interconectados por enlaces válidos.
