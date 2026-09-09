# Escenario · 003-06-el-dia-completo

**Cubre:** epic 003, sexto y último peldaño, y su criterio de salida. Gemela determinista: la cadena entera del epic 002, de [`002-01`](002-01-abrir-ciclo.md) a [`002-09`](002-09-crear-nota.md).

Los cinco escenarios anteriores dictan una frase y miran una cosa. Este dicta el día entero de una vez y mira el vault que quedó.

Lo que agrega no es volumen. Es **lo que solo aparece cuando las frases conviven**: una menciona un frente que todavía no existe y otra lo abre después; una deja algo por hacer y otra, seis horas más tarde, lo da por hecho repitiendo su texto. Ninguna de las dos cosas se puede probar con una frase sola.

## Estado inicial

Un vault recién sembrado, como el del [`003-01`](003-01-el-vault-dice-a-donde-va.md). **Este escenario rompe la cadena a propósito.**

```bash
tuku init mi-vault --date 2026-08-11
```

Heredar el vault del [`003-05`](003-05-lo-que-no-se-registra.md) sería peor: el dictado repite frases que ahí ya están escritas, y el agente las volvería a redactar con otras palabras. `tuku entry add` es idempotente carácter por carácter, así que dos redacciones del mismo hecho son dos líneas. El escenario mediría duplicación en vez de traducción.

## Escenario: el día dictado entero deja el vault del epic 002

Dado un vault sembrado y vacío de registros
Cuando el autor le cuenta el día completo, al final del día

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

Y cada registro del martes 11 tiene su hora, su ámbito y su marca según la tabla de abajo
Y el cuerpo del registro de las 18:40 enlaza a `depto-centro`, que en ese momento todavía no existía
Y `PENDIENTES.md` queda con una sola fila: la sesión con el psicólogo, fechada el miércoles 12
Y el miércoles 12 abre con el callout del pendiente del día
Y existe una nota en `notas/` y el registro de las 21:15 la enlaza
Y ni "recuérdame" ni ninguna línea que no esté en la tabla aparecen en `AHORA.md`
Y `tuku doctor` no reporta ninguna marca sin su consecuencia

## La tabla de verdad

Sale del vault que dejó la cadena del 002, con las tres correcciones de abajo. Lo que está en esta tabla es lo que falla si no calza; el resto de la línea es del agente.

| Hora | Día | Ámbito | Marca | Qué deja |
| --- | --- | --- | --- | --- |
| 09:12 | martes 11 | `personal` | ninguna | nada |
| 11:30 | martes 11 | `personal` | ninguna | nada |
| 12:05 | martes 11 | `personal` | ninguna | nada |
| 13:00 | martes 11 | `personal` | `**pendiente**` | abre "comprar una maleta" |
| 14:20 | martes 11 | `personal` | `**pendiente**` | abre "avisar de los gastos comunes a la administradora" |
| 18:40 | martes 11 | `personal` | ninguna | menciona un frente que no existe |
| 19:05 | martes 11 | `personal` | `~~(Hecho)~~` | cierra el de las 14:20 |
| 19:10 | martes 11 | `personal` | `~~(Hecho)~~` | cierra el de las 13:00 |
| 21:15 | martes 11 | `depto-centro` | ninguna | constancia de la nota |
| 09:00 | miércoles 12 | `personal` | `**pendiente**` | abre, con fecha 2026-08-12 |

El ámbito de un registro es el `[[...]]` que abre la línea, y no una mención del cuerpo. Las 18:40 nombran `depto-centro` y van en `personal`, porque al escribirse ese frente todavía no existe y ninguno calza. El enlace del cuerpo lo escribe `tuku scope create` tres frases después, al pasar por los registros del ciclo.

Los dos cierres son el juicio más fino del epic: cerrar exige **repetir el cuerpo del pendiente**, no describir lo que se hizo. "Ya compré la maleta" tiene que salir como "comprar una maleta", que es lo que dice la tabla, o el cierre no encuentra su pareja y el sistema informa que no la había.

## Por qué el vault del 002 no se compara byte a byte

El [`003-00`](003-00-el-dia-uno-dictado.md) dice que este epic termina en el mismo vault que el 002. Es cierto en los campos que importan y no en el archivo entero, y las tres diferencias tienen la misma causa: **el 002 escribió a mano casos que probaban el comando, no el día**.

| En el vault del 002 | Acá | Por qué |
| --- | --- | --- |
| 13:00 dice `**Pendiente**` y no abre nada | `**pendiente**`, y abre | El [`002-03`](002-03-lint-de-registro.md) sembró la mayúscula a propósito para probar el lint. Nadie la dicta. |
| 11:30 y 18:40 van sin ámbito | `personal` | El [`002-02`](002-02-registro-en-su-dia.md) probaba el registro sin ámbito. El `AGENTS.md` dice que todos lo llevan. |
| 19:10 es un cierre sin pareja, y se reporta | cierra de verdad | Consecuencia de la primera: como el de las 13:00 sí abrió, este sí tiene qué cerrar. |

`PENDIENTES.md` sí queda idéntico, y eso no es casualidad: las dos correcciones se cancelan, porque lo que el 13:00 abre lo cierra el 19:10.

La abreviatura es aparte y no es un defecto de ninguno de los dos: el 002 escribió "GGCC" y el dictado dice "gastos comunes". Eso es redacción y se reporta.

## Qué hace fallar y qué solo se reporta

**Falla:** un comando de más o de menos, cualquier celda de la tabla de verdad, un cierre que no encontró su pareja, una fila en `PENDIENTES.md` que no sea la del psicólogo, la instrucción del autor escrita como si fuera un hecho, o cualquier archivo tocado por fuera de `tuku`.

**Se reporta:** la redacción de cada cuerpo, la clasificación abierta de los registros sin marca, el título de la nota, y el orden entre comandos que no dependen entre sí. Sí importa el orden entre los que dependen: un cierre antes de su apertura no encuentra nada que cerrar.

## Qué se mira a mano

El archivo del turno en `playground/`, que es el único escenario del epic donde vale la pena leerlo entero.

- **Las clasificaciones abiertas de los ocho registros.** Once frases seguidas obligan al agente a elegir vocabulario, y lo que repita es candidato a entrar al `LIBRO-DE-ESTILO.md`.
- **Si narró el mecanismo.** Un resumen de once comandos es donde más tienta.
- **Si preguntó algo.** Este dictado no tiene ninguna ambigüedad declarada, así que una pregunta acá es un hallazgo sobre el `AGENTS.md` y entra al epic 004.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 003_06 -m "not red and not pendiente"
```
