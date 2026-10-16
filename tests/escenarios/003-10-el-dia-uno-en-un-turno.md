# 003-10 · El día uno en un turno

> **Principio:** [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md), [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md)

El criterio de salida del epic en un solo turno: el autor dicta el día uno entero y el agente lo compila a comandos deterministas, dejando un vault equivalente al del [epic 002](002-00-el-dia-uno-a-mano.md). En el mismo turno van las frases que no se anotan: una consulta previa, una instrucción y una pregunta mezcladas con hechos, un cierre ambiguo y un pedido estructural sin comando.

El día que se deriva del vault, sin dictarlo, está en el [`003-11`](003-11-el-dia-que-no-se-dicta.md).

## Estado inicial

```bash
tuku init mi-vault --date 2026-08-11
```

## Escenario: el día uno entero, con lo que no se anota, en un turno

Dado un vault sembrado y vacío de registros
Cuando el autor le cuenta el día de una vez, con una consulta antes y dos pedidos que no puede resolver solo al final
```agente
Una pregunta antes de lo de hoy: si te dijera que hay que renovar el pase escolar, ¿qué anotarías y en qué archivo? Eso no lo anotes, solo dime.
A las nueve y doce me di cuenta de que la administradora responde los mensajes con varios días de atraso.
A las once y media hice la consulta presencial por el standing desk.
A las doce y cinco ordené los cables del escritorio. Recuérdame que eso es importante.
A la una, tengo que comprar una maleta.
A las dos y veinte, hay que avisarle de los gastos comunes a la administradora.
A las seis cuarenta le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp.
A las siete y cinco, listo lo de avisarle de los gastos comunes a la administradora.
A las siete y diez ya compré la maleta.
El depto centro es un frente aparte, ábrelo.
A las nueve y cuarto de la noche guárdame una nota sobre cómo funciona el cobro de gastos comunes en una copropiedad, que es del depto centro.
Mañana a las nueve tengo que pagar la sesión con el psicólogo.
Mañana a las nueve y media hay que pagar los gastos comunes del depto centro.
¿Cuántos pendientes tengo abiertos?
Ah, y ya pagué.
Cámbiale el nombre a la carpeta de notas, ponle "apuntes".
```
Entonces el dictado se traduce en doce comandos y ninguno más
```text
tuku entry add --day 2026-08-11 --hour 09:12 --scope personal --body "..."   ×4
tuku todo open --day 2026-08-11 --hour 13:00 --scope personal --body "..."    ×2
tuku todo close --day 2026-08-11 --hour 19:05 --scope personal --body "..."   ×2
tuku scope create depto-centro --day 2026-08-11
tuku note create "<el título>" --scope depto-centro --day 2026-08-11 --hour 21:15
tuku todo open --day 2026-08-12 --hour 09:00 --scope personal --body "..."
tuku todo open --day 2026-08-12 --hour 09:30 --scope depto-centro --body "..."
```
Y cada registro tiene su hora, su ámbito y su marca cerrada según la tabla de verdad
Y la consulta del pase escolar no deja nada escrito, y la respuesta nombra `AHORA.md` y `PENDIENTES.md`
Y ni "recuérdame" ni la pregunta por los pendientes entran a `AHORA.md`
Y el cuerpo del registro de las 18:40 enlaza a `depto-centro` de forma retroactiva, y el martes tiene la constancia de haberlo abierto
Y los dos cierres de las 19:05 y las 19:10 encontraron su pareja, y como se abrieron ese mismo día, de cada uno queda solo el cierre
Y "ya pagué" no cierra ninguno de los dos pendientes de mañana, y el agente pregunta cuál
Y `notas/` sigue llamándose así, con la nota de las 21:15 adentro
Y fuera de lo que el día escribe, no cambió ningún archivo
Y `tuku doctor` confirma la coherencia total del vault
```bash
tuku doctor --vault mi-vault
```

### Tabla de verdad

Solo se afirma la marca cerrada (`**pendiente**`, `(Hecho)`). "Ninguna" significa que no lleva ninguna de las dos: la clasificación abierta la elige el agente y no se verifica.

| Hora | Día | Ámbito | Marca cerrada |
| --- | --- | --- | --- |
| 09:12 | martes 11 | `personal` | ninguna |
| 11:30 | martes 11 | `personal` | ninguna |
| 12:05 | martes 11 | `personal` | ninguna |
| 18:40 | martes 11 | `personal` | ninguna |
| 19:05 | martes 11 | `personal` | `(Hecho)` |
| 19:10 | martes 11 | `personal` | `(Hecho)` |
| 21:15 | martes 11 | `depto-centro` | ninguna |
| 09:00 | miércoles 12 | `personal` | `**pendiente**` |
| 09:30 | miércoles 12 | `depto-centro` | `**pendiente**` |
