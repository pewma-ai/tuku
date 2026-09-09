# Escenario · 003-03-un-hecho-un-comando

**Cubre:** epic 003, tercer peldaño: el agente ejecuta por primera vez. Gemelo determinista: [`002-02-registro-en-su-dia`](002-02-registro-en-su-dia.md).

El dictado más simple que existe. Un hecho que ocurrió, que no deja nada abierto y no cierra nada: una línea en `AHORA.md` y se acabó.

Es el primero que escribe, así que es donde se ve si el agente entendió que **no edita archivos**. Un vault que quedó bien pero cuya traza está vacía es un fallo, no un éxito: significa que abrió el archivo y escribió, que es lo único que el vault prohíbe, y a la tercera vez va a romper algo que ningún comando podría haber roto.

## Estado inicial

El que dejó [`003-02-el-agente-lee-el-vault`](003-02-el-agente-lee-el-vault.md), que preguntó y no tocó nada: un vault sembrado y vacío de registros.

```bash
cp -r ../../003-02-el-agente-lee-el-vault/el-agente-dice-que-haria-y-no/mi-vault .
```

## Escenario: un hecho que no deja nada abierto es una línea y nada más

Dado un vault sembrado, sin ningún registro escrito
Cuando el autor dicta un hecho suelto

```agente
A las nueve y doce me di cuenta de que la administradora responde los mensajes con varios días de atraso.
```

Entonces esa frase se traduce en un solo comando

```text
tuku entry add --day 2026-08-11 --hour 09:12 --scope personal \
  --body "**<clasificación>**: <el cuerpo>"
```

Y queda un registro a las 09:12 bajo el día de hoy, y su cuerpo dice de qué se trata
Y llegó por una invocación de `tuku entry add`, no por una edición del archivo
Y no se abrió ningún pendiente, porque el autor no dejó nada por hacer
Y el delta es el mismo que deja el gemelo determinista: `AHORA.md` y la vista del ámbito

Uno, y no dos: es lo que separa este escenario del [`003-04`](003-04-un-hecho-con-consecuencia.md). El autor contó algo que ocurrió y no dejó nada por hacer, así que no hay consecuencia que aplicar. La clasificación va entre asteriscos porque es vocabulario suyo y no se exige cuál.

La afirmación del delta es la que más delgada parece y la que más cubre, y su valor exacto no se supone: se copia del [`002-02`](002-02-registro-en-su-dia.md), que ya lo dejó fijado. `tuku entry add` regenera la vista del ámbito además de escribir la bitácora. Cualquier otra cosa en el delta la hizo el agente sin que nadie se la pidiera.

## Qué hace fallar y qué solo se reporta

**Falla:** que el registro no exista, que caiga en otro día, que lleve una marca de la ontología cerrada, que abra un pendiente, o que el vault haya cambiado por fuera de `tuku`.

**Se reporta:** la clasificación que elija, y que omita el ámbito. En la primera corrida escribió `- 09:12 - **señal**: ...` sin `[[personal]]`, donde el vault del 002 sí lo lleva. El `AGENTS.md` del vault no dice en ninguna parte que cada registro nombre su ámbito, así que el defecto es del documento y no del agente. Lo exige el [`003-06`](003-00-el-dia-uno-dictado.md), que compara el día completo.

**Se reporta también:** la clasificación que elija. El vault del 002 dice `**señal**`, pero la clasificación es vocabulario abierto del autor ([`spec/despacho.md`](../../spec/despacho.md)) y exigirla acá sería pedirle al agente que adivine una palabra. Lo que sí se exige es que **no** invente una marca cerrada, que es la que tiene consecuencias.

## Qué se mira a mano

El archivo del turno en `playground/`: qué clasificación eligió y cómo redactó el cuerpo. Una redacción que se aleja mucho del dictado es información sobre el libro de estilo.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k "003_0[123]" -m "not red and not pendiente"
```
