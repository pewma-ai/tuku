# Escenario · 003-04-un-hecho-con-consecuencia

**Cubre:** epic 003, cuarto peldaño. Gemelo determinista: [`002-04-abrir-pendiente`](002-04-abrir-pendiente.md).

El escenario central del epic. Todo lo anterior se podía resolver con una sola llamada; este no.

Lo que el agente decide acá no es qué comando correr, que es el mismo del escenario anterior: es **si el hecho deja algo abierto**. De esa sola decisión depende que el pendiente exista o no, porque `tuku entry add` aplica lo que la marca declara.

Este escenario se escribió cuando abrir el pendiente era un segundo comando y el agente tenía que acordarse de él. Esa asimetría se corrigió el 2026-09-09: las consecuencias son parte de escribir, igual que la propagación de ámbitos. Lo que queda por probar es más fino y más interesante, porque es el único juicio que no se puede automatizar.

## Estado inicial

El que dejó [`003-03-un-hecho-un-comando`](003-03-un-hecho-un-comando.md): un registro escrito y ningún pendiente abierto.

```bash
cp -r ../../003-03-un-hecho-un-comando/un-hecho-que-no-deja-nada/mi-vault .
```

## Escenario: lo que queda por hacer se escribe y además se abre

Dado un vault con un registro escrito y la tabla de pendientes vacía
Cuando el autor dicta algo que queda por hacer

```agente
A las dos y veinte, hay que avisarle de los gastos comunes a la administradora.
```

Entonces esa frase se traduce en un solo comando

```text
tuku entry add --day 2026-08-11 --hour 14:20 --scope personal \
  --body "**pendiente**: <el cuerpo>"
```

Y queda un registro a las 14:20 con la marca `**pendiente**`
Y la tabla de `PENDIENTES.md` gana una fila con el mismo cuerpo, carácter por carácter
Y la fila entra en el primer escalón de la escalera del autor, que es el del ciclo en curso
Y no queda ninguna marca sin su consecuencia: la bitácora y la tabla dicen lo mismo
Y el delta es el mismo que deja el gemelo determinista

Lo único que el agente decide es la marca, y de ella se sigue todo lo demás: `**pendiente**` hace que `tuku entry add` abra el pendiente en `PENDIENTES.md` además de escribir la línea. El cuerpo lo redacta él; la hora, el día, el ámbito y el formato salen de la frase.

Ese bloque no es ilustración: el test compara contra él la secuencia de comandos que el agente ejecutó de verdad. Los de lectura no cuentan, así que mirar la ayuda antes de escribir o correr `tuku doctor` al terminar no lo rompe.

La afirmación de las consecuencias sigue siendo la que da nombre al escenario, aunque ya no dependa de que el agente recuerde nada: hoy verifica que el comando cumple lo que promete, y protege el día que alguien vuelva a separarlos.

## Qué hace fallar y qué solo se reporta

**Falla:** que la traducción sea otra (otro comando, o uno de más), que falte la marca, que falte la fila, que el cuerpo de la fila no sea el del registro, que el horizonte no salga de la escalera del autor, o que algo del vault haya cambiado por fuera de `tuku`.

**Se reporta:** cómo redacte el cuerpo. El vault del 002 dice "avisar de los GGCC a la administradora" y el dictado dice "gastos comunes"; que el agente abrevie o no es suyo. Lo que sí se exige es que el registro y la fila digan **lo mismo**, porque de eso depende poder cerrarlo después repitiendo el texto.

## Qué se mira a mano

El archivo del turno en `playground/`. Si el agente corrió además un `tuku todo open`, el vault queda igual de bien (el comando es idempotente) pero está siguiendo un mapa viejo: vale la pena mirar qué se lo sugirió.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k "003_0[1234]" -m "not red and not pendiente"
```
